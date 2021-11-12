#!/usr/bin/env python3


# Std
import argparse
import collections
import json
import sys

# External
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

import os


try:
    from PyQt5.QtCore import QStringList
except ImportError:
    QStringList = list


class JsonView(QtWidgets.QWidget):

    def __init__(self):
        super(JsonView, self).__init__()

        #Load file
        self.tree_widget = None
        self.textEdit = QtWidgets.QTextEdit()
        self.TreeEdit = QtWidgets.QTextEdit()

        filenames = QStringList()

        #define widgets
        self.savefile_btn = QtWidgets.QPushButton("Save")
        self.filenames = filenames
        self.savefile_btn.clicked.connect(self.Save_textEdit)
        self.restart_btn = QtWidgets.QPushButton("Restart")
        self.restart_btn.clicked.connect(self.restart)
        self.open_btn = QtWidgets.QPushButton("Open")
        self.open_btn.clicked.connect(self.OpenFile)
        self.SaveAs_btn = QtWidgets.QPushButton("Save as...")
        self.SaveAs_btn.clicked.connect(self.Save_as)

        # Tree
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)##
        selmodel = self.tree_widget.selectionModel()
        selmodel.selectionChanged.connect(self.handleSelection)

        #add widgets to layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.textEdit)
        self.table_gbox = QtWidgets.QGroupBox("filenames")
        self.table_gbox.setLayout(layout)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.open_btn)
        layout2.addWidget(self.savefile_btn)
        layout2.addWidget(self.SaveAs_btn)
        layout2.addWidget(self.restart_btn)
        btn_gbox = QtWidgets.QGroupBox()
        btn_gbox.setLayout(layout2)

        layout3 = QtWidgets.QVBoxLayout()
        layout3.addWidget(self.table_gbox)
        layout3.addWidget(btn_gbox)
        self.setLayout(layout3)

    def OpenFile(self):
        self.tree_widget.clear()
        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)
        if dlg.exec_():
            filenames = dlg.selectedFiles()
            self.filenames = dlg.selectedFiles()
            try:
                with open(filenames[0], 'r') as f:
                    data = json.load(f)
                data1 = json.dumps(data, indent=5)
                self.textEdit.setText(data1)
                jfile = open(filenames[0])
                jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)
                root_item = QtWidgets.QTreeWidgetItem(["Root"])
                self.recurse_jdata(jdata, root_item)
                self.tree_widget.addTopLevelItem(root_item)
                self.table_gbox.setTitle(filenames[0])
            except json.decoder.JSONDecodeError:
                QtWidgets.QMessageBox.warning(self, 'Hint', 'This is not a json file.', QtWidgets.QMessageBox.Yes)
            except Exception as e:
                print(e)
                QtWidgets.QMessageBox.warning(self, 'Hint', 'Something went wrong.', QtWidgets.QMessageBox.Yes)

    def TreeClicked(self):
        getSelected = self.tree_widget.selectedItems()
        if getSelected:
            baseNode = getSelected[0]
            getChildNode = baseNode.text(1)
            print(getChildNode)


    def handleSelection(self, selected, deselected):
        for i, index in enumerate(selected.indexes()):
            item = self.tree_widget.itemFromIndex(index)#item-QTreeWidgetItem, index-QModelIndex
            column = self.tree_widget.currentColumn()
            edit = QtWidgets.QLineEdit()

            if item.text(column):
                edit.setText(item.text(column))
                edit.returnPressed.connect(lambda *_: self.setData(edit, item, column, self.tree_widget))
                self.tree_widget.setItemWidget(item, column, edit)
            else:
                return
            # print('SEL: row: %s, col: %s, text: %s' % (
            #     index.row(), index.column(), item.text(i)))

    def setData(self, data, item, column, tree):
        item.setText(int(column), data.text())
        tree.setItemWidget(item, column, None)

    def restart(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)

    def Save_textEdit(self):
        filename = self.filenames
        update = self.textEdit.toPlainText()
        try:
            data = json.loads(update)
            with open(filename[0], 'w') as f:
                f.write(update)
                f.close()
            QtWidgets.QMessageBox.information(self, 'Hint', 'File Saved.', QtWidgets.QMessageBox.Yes)
        except IndexError:
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Please press Save as first.', QtWidgets.QMessageBox.Yes)
        except json.decoder.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Not the right json format.', QtWidgets.QMessageBox.Yes)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Something went wrong.', QtWidgets.QMessageBox.Yes)

    def Save_as(self):
        try:
            text = self.textEdit.toPlainText()
            data = json.loads(text)
            name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File')
            filename = str(name[0])
            file = open(filename, 'w')
            file.write(text)
            file.close()
            QtWidgets.QMessageBox.information(self, 'Hint', 'File Saved.', QtWidgets.QMessageBox.Yes)
        except json.decoder.JSONDecodeError:
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Not the right json format.', QtWidgets.QMessageBox.Yes)
        except Exception as e:
            print(e)
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Something went wrong.', QtWidgets.QMessageBox.Yes)



    def recurse_jdata(self, jdata, tree_widget):
        if isinstance(jdata, dict): #isinstance用來判斷jdata是否為dict
            for key, val in jdata.items():
                self.tree_add_row(key, val, tree_widget)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                key = str(i)
                self.tree_add_row(key, val, tree_widget)
        else:
            print("This should never be reached!")

    def tree_add_row(self, key, val, tree_widget):
        if isinstance(val, dict) or isinstance(val, list):#如果為還能拆解的dict, list 就再送回去拆解
            row_item = QtWidgets.QTreeWidgetItem([key])
            self.recurse_jdata(val, row_item)
        else:
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)])
        tree_widget.addChild(row_item)#add on tree



    def get_subtree_nodes(self, tree_widget_item):
        """Returns all QTreeWidgetItems in the subtree rooted at the given node."""
        nodes = []

        nodes.append(tree_widget_item)
        for i in range(tree_widget_item.childCount()):
            nodes.extend(self.get_subtree_nodes(tree_widget_item.child(i)))
            j = 0
            while nodes[i].text(j):
                print('i:', i, ', j:', j)
                print(nodes[i].text(j))
                j+=1


        return nodes

    # def get_all_items(self):
    #     """Returns all QTreeWidgetItems in the given QTreeWidget."""
    #     all_items = []
    #     for i in range(self.tree_widget.topLevelItemCount()):
    #         top_item = self.tree_widget.topLevelItem(i)
    #         all_items.extend(self.get_subtree_nodes(top_item))
    #
    #     return all_items


class JsonViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(JsonViewer, self).__init__()

        json_view = JsonView()

        self.setCentralWidget(json_view)
        self.setWindowTitle("JSON Editor")
        self.setMinimumSize(800, 600)
        self.show()


if "__main__" == __name__:
    qt_app = QtWidgets.QApplication(sys.argv)
    json_viewer = JsonViewer()
    sys.exit(qt_app.exec_())




