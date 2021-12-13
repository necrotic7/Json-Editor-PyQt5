# Std
import collections
import json
import sys
import os
# External
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

try:
    from PyQt5.QtCore import QStringList
except ImportError:
    QStringList = list

QtCore.QTextCodec.setCodecForLocale(QtCore.QTextCodec.codecForName("gb18030"))


TREE_STYLESHEET = ''' 
    QTreeWidget::item { border-bottom: 1px solid black;}
    
    QTreeWidget::item:selected { background-color: #366be7; border-color:blue; 
    border-style:outset; border-width:0px; color:white; }
    '''
    
TEXT_STYLESHEET = '''
    background-color: white;
    color: black;
    selection-background-color: #606060; selection-color: white;
'''

class JsonView(QtWidgets.QWidget):

    def __init__(self):
        
        
        super(JsonView, self).__init__()

        #Load file
        self.tree_widget = None
        self.textEdit = QtWidgets.QTextEdit()
        self.TempEdit = QtWidgets.QTextEdit()
        self.textEdit.setStyleSheet(TEXT_STYLESHEET)

        filenames = QStringList()

        #define widgets
        self.savefile_btn = QtWidgets.QPushButton("儲存")
        self.filenames = filenames
        self.savefile_btn.clicked.connect(self.Save_textEdit)
        self.restart_btn = QtWidgets.QPushButton("重啟")
        self.restart_btn.clicked.connect(self.restart)
        self.open_btn = QtWidgets.QPushButton("開啟檔案")
        self.open_btn.clicked.connect(self.OpenFile)
        self.SaveAs_btn = QtWidgets.QPushButton("另存新檔")
        self.SaveAs_btn.clicked.connect(self.Save_as)
        self.find_lineEdit = QtWidgets.QLineEdit()
        self.find_btn = QtWidgets.QPushButton("尋找")
        self.find_btn.clicked.connect(self.find_word)
        self.settings = []

        self.reload_btn = QtWidgets.QPushButton("重新讀檔")
        self.reload_btn.clicked.connect(self.Reload)

        # Tree
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)##
        selmodel = self.tree_widget.selectionModel()
        selmodel.selectionChanged.connect(self.handleSelection)
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)  
        self.tree_widget.customContextMenuRequested.connect(self.contextMenu)
        self.tree_widget.setStyleSheet(TREE_STYLESHEET)

        #add widgets to layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.textEdit)
        self.table_gbox = QtWidgets.QGroupBox("filenames")
        self.table_gbox.setLayout(layout)

        layout1 = QtWidgets.QHBoxLayout()
        layout1.addWidget(self.open_btn)
        layout1.addWidget(self.savefile_btn)
        layout1.addWidget(self.SaveAs_btn)
        layout1.addWidget(self.reload_btn)
        layout1.addWidget(self.restart_btn)
        acts_btn_gbox = QtWidgets.QGroupBox('Actions')
        acts_btn_gbox.setLayout(layout1)

        layout3 = QtWidgets.QVBoxLayout()
        layout3.addWidget(self.find_lineEdit)
        layout3.addWidget(self.find_btn)
        layout3.addWidget(acts_btn_gbox)
        layout3.addWidget(self.table_gbox)
        self.setLayout(layout3)
        self.LoadSettings()
   
    def rc(self, rel_path):
        """Return full path of resource according to rel_path."""
        if not hasattr(sys, '_MEIPASS'):
            # for elder PyInstaller.
            rc_path = os.environ.get("_MEIPASS2", os.getcwd())
        else:
            rc_path = getattr(sys, '_MEIPASS', os.getcwd())
        return os.path.join(rc_path, rel_path)
        
    def LoadSettings(self):
        #尋找打包後讀取settings的solution
        filename = self.rc('settings.json')
        # filename = os.path.join(os.environ['_MEIPASS2'], filename)
        if not self.settings:
            try:
                open(filename, 'r')
                self.settings.append(filename)
            except FileNotFoundError:
                QtWidgets.QMessageBox.warning(self, 'Hint', '請先選擇settings檔', QtWidgets.QMessageBox.Yes)
                
                dlg = QtWidgets.QFileDialog()
                dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
                if dlg.exec_():
                    self.settings = dlg.selectedFiles()
            except Exception as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, 'Hint', '請確認settings檔案是否無誤', QtWidgets.QMessageBox.Yes)
                sys.exit()
        
        try:
            with open(self.settings[0], 'r') as f:
                settings = json.load(f)
                self.CAN_DELETE = settings['CAN_DELETE'] #可選填
                self.CAN_DELETE_CHILD = settings['CAN_DELETE_CHILD'] #子可以刪掉
                self.CANNOT_EDIT_VALUE = settings['CANNOT_EDIT_VALUE'] #value不可修改
                self.VALID_KEYS = settings['VALID_KEYS']
                self.CONFIG_SET_KEYS = settings['CONFIG_SET_KEYS']
                self.AI_FEATURES_SETS = settings['AI_FEATURES_SETS']
                self.AI_FEATURES_KEYS = settings['AI_FEATURES_KEYS']
                self.ROIOBJ_KEYS = settings['ROIOBJ_KEYS']
                self.VALID_KEYS.extend(self.CONFIG_SET_KEYS)
                self.VALID_KEYS.extend(self.AI_FEATURES_KEYS)
                self.VALID_KEYS.extend(self.ROIOBJ_KEYS)
                self.VALID_KEYS.extend(self.CANNOT_EDIT_VALUE)

            self.SETTINGS_KEYS = ['CAN_DELETE', 'CAN_DELETE_CHILD', 'CANNOT_EDIT_VALUE', 'VALID_KEYS', 'CONFIG_SET_KEYS', 'AI_FEATURES_KEYS', 'ROIOBJ_KEYS']
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '請確認settings檔案是否無誤', QtWidgets.QMessageBox.Yes)
            sys.exit()
    def contextMenu(self, point):
        self.menu = QtWidgets.QMenu(self)
        self.menu.addAction('新增child', self.itemInsert)
        self.menu.addAction('刪除', self.itemDelete)
        self.menu.addAction('複製', self.itemDuplicate)
        self.menu.exec_( self.focusWidget().mapToGlobal(point) )

    def OpenFile(self):
        self.LoadSettings()
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.filenames = dlg.selectedFiles()
            try:
                with open(filenames[0], 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                
                data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
                self.textEdit.setText(data1)
                self.tree_widget.clear()
                jfile = open(filenames[0])
                jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
                root_item = QtWidgets.QTreeWidgetItem(["Root"])
                self.recurse_jdata(jdata, root_item)
                self.tree_widget.addTopLevelItem(root_item)
                self.table_gbox.setTitle(filenames[0])
                self.tree_widget.expandAll()
            except json.decoder.JSONDecodeError:
                QtWidgets.QMessageBox.warning(self, 'Hint', '非合規的Json檔', QtWidgets.QMessageBox.Yes)
            except Exception as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)

    def Reload(self):
        try:
            with open(self.filenames[0], 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
            self.textEdit.setText(data1)
            self.tree_widget.clear()
            jfile = open(self.filenames[0])
            jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
            root_item = QtWidgets.QTreeWidgetItem(["Root"])
            self.recurse_jdata(jdata, root_item)
            self.tree_widget.addTopLevelItem(root_item)
            self.table_gbox.setTitle(self.filenames[0])
            self.tree_widget.expandAll()
        except json.decoder.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '非Json檔案', QtWidgets.QMessageBox.Yes)
        except IndexError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '請先開啟一個檔案', QtWidgets.QMessageBox.Yes)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)

    def handleSelection(self, selected, deselected):
        for i, index in enumerate(selected.indexes()):
            item = self.tree_widget.itemFromIndex(index)
            column = self.tree_widget.currentColumn()
            edit = QtWidgets.QLineEdit()
            #i=0為key, i=1為value
            # print('i:', i, item.text(i))
            if column == 1 and str(item.text(0)) not in self.CANNOT_EDIT_VALUE:
                old = item.text(column)
                edit.setText(old)
                edit.returnPressed.connect(lambda *_: self.setData(edit, item, column, self.tree_widget, old))
                self.tree_widget.setItemWidget(item, column, edit)
            elif column == 0 and str(item.text(0)) in self.AI_FEATURES_SETS :
                old = item.text(column)
                edit.setText(old)
                edit.returnPressed.connect(lambda *_: self.setData(edit, item, column, self.tree_widget, old))
                self.tree_widget.setItemWidget(item, column, edit)
            # print('SEL: row: %s, col: %s, text: %s' % (
            #     index.row(), index.column(), item.text(i)))

    def setData(self, edit, item, column, tree, old):
        item.setText(int(column), edit.text())
        key = item.text(0)
        print('key:', key)
        tree.setItemWidget(item, column, None)
        if item.parent():
            self.Case(item, old, edit.text(), key)
        self.data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
        self.textEdit.setText(self.data1)

    def itemInsert(self):
        text, ok = QtWidgets.QInputDialog.getText(self, "新增Child", "輸入child key值:")
        if ok and text != "":
            try:
                if str(text) in self.VALID_KEYS or isinstance(int(text), int):
                    if len(self.tree_widget.selectedItems()) > 0:
                        QtWidgets.QTreeWidgetItem(self.tree_widget.selectedItems()[0], [text])
                    else:
                        QtWidgets.QTreeWidgetItem(self.tree_widget, [text])
            except:
                QtWidgets.QMessageBox.warning(self, 'Hint', '未知的key值', QtWidgets.QMessageBox.Yes)
    
    def itemDelete(self):
        for item in self.tree_widget.selectedItems():
            if str(item.text(0)) not in self.CAN_DELETE:
                try:
                    if str(self.get_parent(item, 1).text(0)) not in self.CAN_DELETE_CHILD and str(self.get_parent(item, 2).text(0)) != 'ROI' and str(item.parent().text(0)) not in self.SETTINGS_KEYS:
                        QtWidgets.QMessageBox.warning(self, 'Hint', '無法刪除', QtWidgets.QMessageBox.Yes)
                        return
                except:
                    QtWidgets.QMessageBox.warning(self, 'Hint', '無法刪除', QtWidgets.QMessageBox.Yes)
                    return
            self.DCase(item, item.text(0))
            self.tree_widget.clear()
            root_item = QtWidgets.QTreeWidgetItem(["Root"])
            self.recurse_jdata(self.data, root_item)
            self.tree_widget.addTopLevelItem(root_item)
            self.tree_widget.expandAll()
            self.data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
            self.textEdit.setText(self.data1)
        
    def itemDuplicate(self):
        for item in self.tree_widget.selectedItems():
            if str(item.parent().text(0)) == 'config_set':
                content = self.data['config_set'][int(item.text(0))]
                self.data['config_set'].append(content) 
            elif str(item.parent().text(0)) == 'AI_features':
                text, ok = QtWidgets.QInputDialog.getText(self, "複製", "輸入key值:")
                if ok and text != "":
                    content = self.data['config_set'][int(self.get_parent(item, 2).text(0))]['AI_features']
                    if str(text) not in self.VALID_KEYS:
                        QtWidgets.QMessageBox.warning(self, 'Hint', '未知的Key值', QtWidgets.QMessageBox.Yes)
                        return
                    try:
                        if content[str(text)]:
                            QtWidgets.QMessageBox.warning(self, 'Hint', 'Key值已存在', QtWidgets.QMessageBox.Yes)
                            return
                    except Exception as e:
                        print(e)
                    content[str(text)] = content.copy()[item.text(0)]
            else:
                QtWidgets.QMessageBox.warning(self, 'Hint', '只有config_set和AI_features底下的child可被複製', QtWidgets.QMessageBox.Yes)
                return
            self.data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
            self.textEdit.setText(self.data1)
            self.Save_textEdit()
            self.Reload()
        
    def Case(self,item, old, new, key):
        #讓key_set可改
        
        try:
            print('parent:', item.parent().text(0), old, new)
            
            if str(old) in self.AI_FEATURES_SETS:
                if str(new) in self.AI_FEATURES_SETS:
                    AI_F = self.data['config_set'][int(self.get_parent(item, 2).text(0))]['AI_features']
                    AI_F[str(new)] = AI_F.pop(str(old))
                    return
            
            if str(item.parent().text(0)) in self.SETTINGS_KEYS:
                try:
                    if self.data[str(self.get_parent(item, 1).text(0))][int(key)] is not None:
                        self.data[str(self.get_parent(item, 1).text(0))][int(key)] = str(new)
                except IndexError:
                    self.data[str(self.get_parent(item, 1).text(0))].append(str(new))
                return
            
            if str(key) == 'switch':
                self.data['switch'] = str(new)
                return
            
            if key in self.CONFIG_SET_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 1).text(0))]
                
                if str(key) == 'dps':
                    content[str(key)] = int(new)
                    
                else:
                    content[str(key)] = str(new)
                
                return
            
            if key in self.AI_FEATURES_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 3).text(0))]
                AI_F = content['AI_features']
                try:
                    AI_F_C = AI_F[str(item.parent().text(0))]
                    if AI_F_C[str(key)] is not None:
                        if str(key) == 'GPU_Index':
                            AI_F_C[str(key)] = int(new)
                        else:
                            AI_F_C[str(key)] = str(new)
                        print('done-2')
                except Exception as e:
                    print(e)
                    AI_F_C = AI_F[str(item.parent().text(0))]
                    AI_F_C[str(key)] = str(new)
                    
                return

            if key in self.ROIOBJ_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                AI_F = content['AI_features']
                AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                ROIObj = AI_F_C['ROIObj'][int(item.parent().text(0))]
                try:
                    if ROIObj[str(key)] is not None:
                        ROIObj[str(key)] = str(new)
                        print('done-3')
                except:
                    ROIObj[str(key)] = str(new)      
                return

            if str(self.get_parent(item, 2).text(0)) == 'ROI':
                #ROIObj裡的ROI
                try:
                    content = self.data['config_set'][int(self.get_parent(item, 7).text(0))]
                    AI_F = content['AI_features']
                    AI_F_C = AI_F[str(self.get_parent(item, 5).text(0))]
                    ROIObj = AI_F_C['ROIObj'][int(self.get_parent(item, 3).text(0))]
                    ROI = ROIObj['ROI'][int(item.parent().text(0))]
                    try:
                        if ROI[int(key)] is not None:
                            ROI[int(key)] = float(new) 
                            print('done-4')
                    except IndexError:
                        ROI.append(float(new))
                except IndexError:
                    ROI = ROIObj['ROI']
                    ROI.append([float(new)])
                #外面的ROI
                except ValueError:
                    try:
                        content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                        AI_F = content['AI_features']
                        AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                        ROI = AI_F_C['ROI'][int(item.parent().text(0))]
                        try:
                            if ROI[int(key)] is not None:
                                ROI[int(key)] = float(new)
                                print('done-5')
                        except Exception as e:
                            ROI.append(float(new))
                    except IndexError:
                        ROI = AI_F_C['ROI']
                        ROI.append([float(new)])      
                return
            
            if str(self.get_parent(item, 2).text(0)) == 'Threshold':
                content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                AI_F = content['AI_features']
                AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                Threshold = AI_F_C['Threshold'][str(item.parent().text(0))]
                try:
                    if Threshold[int(key)] is not None:
                        Threshold[int(key)] = float(new)
                        print('done-6')
                except:
                    Threshold.append(float(new))           
                return
        except ValueError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '格式錯誤', QtWidgets.QMessageBox.Yes)
            return
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)
            return
        QtWidgets.QMessageBox.warning(self, 'Hint', '未知key值不會被儲存', QtWidgets.QMessageBox.Yes)
    
    def DCase(self, item, key):
        try:
            
            if str(self.get_parent(item, 1).text(0)) in self.SETTINGS_KEYS:
                if int(item.text(0)) == 0:
                    QtWidgets.QMessageBox.warning(self, 'Hint', '說明文字無法刪除', QtWidgets.QMessageBox.Yes)
                    return
                del self.data[str(self.get_parent(item, 1).text(0))][int(item.text(0))]
            
            if str(self.get_parent(item, 1).text(0)) == 'config_set':
                try:
                    if self.data['config_set'][1] is not None:
                        pass
                    try:
                        del self.data['config_set'][int(item.text(0))]
                    except Exception as e:
                        print(e)
                except IndexError:
                    QtWidgets.QMessageBox.warning(self, 'Hint', '無法刪除', QtWidgets.QMessageBox.Yes)
                return

            #刪陣列整串
            if str(self.get_parent(item, 1).text(0)) == 'ROI':
                #ROIObj裡的ROI
                try:
                    content = self.data['config_set'][int(self.get_parent(item, 6).text(0))]
                    AI_F = content['AI_features']
                    AI_F_C = AI_F[str(self.get_parent(item, 4).text(0))]
                    ROIObj = AI_F_C['ROIObj'][int(self.get_parent(item, 2).text(0))]
                    ROI = ROIObj['ROI']
                    del ROI[int(item.text(0))]
                #外面的ROI
                except:
                    content = self.data['config_set'][int(self.get_parent(item, 4).text(0))]
                    AI_F = content['AI_features']
                    AI_F_C = AI_F[str(self.get_parent(item, 2).text(0))]
                    ROI = AI_F_C['ROI']
                    del ROI[int(item.text(0))]
                return
            #刪整串
            if str(key) == 'ROI':
                #ROIObj裡的ROI
                try:
                    content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]['AI_features'][str(self.get_parent(item, 3).text(0))]['ROIObj'][int(self.get_parent(item, 1).text(0))]
                    del content['ROI']
                #外面ROI
                except:
                    content = self.data['config_set'][int(self.get_parent(item, 3).text(0))]['AI_features'][str(self.get_parent(item, 1).text(0))]
                    del content['ROI']
                return
            
            if str(key) == 'switch':
                del self.data['switch']
                return
            
            if key in self.CONFIG_SET_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 1).text(0))]
                try:
                    del content[str(key)]
                except Exception as e:
                    print(e)
                return
            
            if key in self.AI_FEATURES_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 3).text(0))]
                AI_F = content['AI_features']
                try:
                    AI_F_C = AI_F[str(item.parent().text(0))]
                    del AI_F_C[str(key)]
                    print('done-2')
                except Exception as e:
                    print(e)
                return

            if key in self.ROIOBJ_KEYS:
                content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                AI_F = content['AI_features']
                AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                ROIObj = AI_F_C['ROIObj'][int(item.parent().text(0))]
                try:
                    del ROIObj[str(key)]     
                except Exception as e:
                    print(e)
                return

            if str(self.get_parent(item, 2).text(0)) == 'ROI':
                #ROIObj裡的ROI
                try:
                    content = self.data['config_set'][int(self.get_parent(item, 7).text(0))]
                    AI_F = content['AI_features']
                    AI_F_C = AI_F[str(self.get_parent(item, 5).text(0))]
                    ROIObj = AI_F_C['ROIObj'][int(self.get_parent(item, 3).text(0))]
                    ROI = ROIObj['ROI'][int(item.parent().text(0))]
                    ROI.remove(float(item.text(1)))
                    
                #外面的ROI
                except ValueError:
                    try:
                        content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                        AI_F = content['AI_features']
                        AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                        ROI = AI_F_C['ROI'][int(item.parent().text(0))]
                        ROI.remove(float(item.text(1)))                      
                    except:
                        pass
                return
            
            if str(self.get_parent(item, 2).text(0)) == 'Threshold':
                content = self.data['config_set'][int(self.get_parent(item, 5).text(0))]
                AI_F = content['AI_features']
                AI_F_C = AI_F[str(self.get_parent(item, 3).text(0))]
                Threshold = AI_F_C['Threshold'][str(item.parent().text(0))]
                try:
                    if Threshold[1] is not None:
                        pass
                    try:
                        Threshold.remove(float(item.text(1)))
                    except:
                        pass
                except:
                    QtWidgets.QMessageBox.warning(self, 'Hint', '無法刪除', QtWidgets.QMessageBox.Yes)
                return

            #刪掉整組config_set
            if str(item.parent().text(0)) == 'config_set':
                content = self.data[str(item.parent().text(0))]
                try:
                    del content[int(key)]
                except:
                    del content[str(key)]
                return
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)
        # QtWidgets.QMessageBox.warning(self, 'Hint', 'Unknow key will not be saved.', QtWidgets.QMessageBox.Yes)

    def get_parent(self, item, times):
        parent = item.parent()
        for i in range(times-1):
            parent = parent.parent()
        return parent

    def restart(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)

    def Save_textEdit(self):
        
        filename = self.filenames
        update = self.textEdit.toPlainText()
        
        try:
            data = eval(update)
            
            data_for_write = json.dumps(data, indent=5, ensure_ascii=False)
            
            with open(filename[0], 'w', encoding='utf-8') as f:
                f.write(data_for_write)
                f.close()
            QtWidgets.QMessageBox.information(self, 'Hint', '存檔完成', QtWidgets.QMessageBox.Yes)
        except IndexError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '請先另存新檔', QtWidgets.QMessageBox.Yes)
        except json.decoder.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '非正確的Json格式', QtWidgets.QMessageBox.Yes)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)
        self.Reload()

    def Save_as(self):
        try:
            text = self.textEdit.toPlainText()
            data = eval(text)
            data_for_write = json.dumps(data, indent=5, ensure_ascii=False)
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            filename = str(name[0])
            file = open(filename, 'w', encoding='utf-8')
            file.write(data_for_write)
            file.close()
            QtWidgets.QMessageBox.information(self, 'Hint', '存檔完成', QtWidgets.QMessageBox.Yes)
            self.tree_widget.clear()
            with open(filename, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            data1 = json.dumps(self.data, indent=5, ensure_ascii=False)
            self.textEdit.setText(data1)
            jfile = open(filename)
            jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
            root_item = QtWidgets.QTreeWidgetItem(["Root"])
            self.recurse_jdata(jdata, root_item)
            self.tree_widget.addTopLevelItem(root_item)
            self.table_gbox.setTitle(filename)
            self.tree_widget.expandAll()
        except FileNotFoundError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '請選取正確的路徑', QtWidgets.QMessageBox.Yes)
        except json.decoder.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, 'Hint', '非正確的Json格式', QtWidgets.QMessageBox.Yes)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', '發生錯誤', QtWidgets.QMessageBox.Yes)

    def recurse_jdata(self, jdata, tree_widget):
        if isinstance(jdata, dict): #isinstance用來判斷jdata是否為dict
            for key, val in jdata.items():
                self.tree_add_row(key, val, tree_widget)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                key = str(i)
                self.tree_add_row(key, val, tree_widget)
        else:
            pass

    def tree_add_row(self, key, val, tree_widget):
        if isinstance(val, dict) or isinstance(val, list):#如果為還能拆解的dict, list 就再送回去拆解
            row_item = QtWidgets.QTreeWidgetItem([key])
            self.recurse_jdata(val, row_item)
        else:
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)])
        tree_widget.addChild(row_item)#add on tree

    def find_word(self):
        words = self.find_lineEdit.text()
        if not self.textEdit.find(words):
            cursor = self.textEdit.textCursor()
            cursor.setPosition(0)
            self.textEdit.setTextCursor(cursor)
            self.textEdit.find(words)

class JsonViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(JsonViewer, self).__init__()
        json_view = JsonView()
        self.setCentralWidget(json_view)
        self.setWindowTitle("Beseye Config JSON Editor")
        self.setMinimumSize(950, 600)
        self.show()

if "__main__" == __name__:
    qt_app = QtWidgets.QApplication(sys.argv)
    json_viewer = JsonViewer()
    sys.exit(qt_app.exec_())