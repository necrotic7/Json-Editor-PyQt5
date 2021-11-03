#!/usr/bin/env python3

__author__ = "Ashwin Nanjappa"

# GUI viewer to view JSON data as tree.
# Ubuntu packages needed:
# python3-pyqt5

# Std
import argparse
import collections
import json
import sys

# External
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets


try:
    from PyQt5.QtCore import QStringList
except ImportError:
    QStringList = list

class TextToTreeItem:#意義不明 就算不經過這裡也能正常顯示

    def __init__(self):
        self.text_list = []
        self.titem_list = []

    def append(self, text_list, titem):
        for text in text_list:
            self.text_list.append(text)
            self.titem_list.append(titem)

    # Return model indices that match string


class JsonView(QtWidgets.QWidget):

    def __init__(self):
        super(JsonView, self).__init__()

        self.find_box = None
        self.tree_widget = None
        self.textEdit = QtWidgets.QTextEdit()
        self.text_to_titem = TextToTreeItem()

        dlg = QtWidgets.QFileDialog()
        dlg.setFileMode(QtWidgets.QFileDialog.AnyFile)

        filenames = QStringList()

        if dlg.exec_():
            filenames = dlg.selectedFiles()

            with open(filenames[0], 'r') as f:
                data = json.load(f)

            data1 = json.dumps(data, indent=5)
            self.textEdit.setText(data1)

        jfile = open(filenames[0])
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)  # 不懂後面那是幹嘛的


        # Tree

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)#應該是自動調整視窗大小的東西

        root_item = QtWidgets.QTreeWidgetItem(["Root"])
        self.recurse_jdata(jdata, root_item)
        self.tree_widget.addTopLevelItem(root_item)#新增root在樹上

        self.savefile_btn = QtWidgets.QPushButton("save file...")

        self.filenames = filenames
        self.savefile_btn.clicked.connect(self.SaveJson)

        self.restart_btn = QtWidgets.QPushButton("Restart")
        self.restart_btn.clicked.connect(self.restart)

        # Add table to layout

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.textEdit)


        # Group box

        gbox = QtWidgets.QGroupBox(filenames[0])
        gbox.setLayout(layout)

        layout2 = QtWidgets.QVBoxLayout()
        layout2.addWidget(gbox)
        layout2.addWidget(self.savefile_btn)
        layout2.addWidget(self.restart_btn)

        self.setLayout(layout2)

    def restart(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
        print(status)


    def SaveJson(self):
        try:
            filename = self.filenames
            update = self.textEdit.toPlainText()
            with open(filename[0], 'w') as f:
                f.write(update)
                f.close()
            QtWidgets.QMessageBox.information(self, 'Hint', 'File Saved.', QtWidgets.QMessageBox.Yes)
        except:
            QtWidgets.QMessageBox.warning(self, 'Hint', 'Fail.', QtWidgets.QMessageBox.Yes)


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

        text_list = []

        if isinstance(val, dict) or isinstance(val, list):#如果為還能拆解的dict, list 就把key值留下 val再送回去拆解
            text_list.append(key)
            row_item = QtWidgets.QTreeWidgetItem([key])
            self.recurse_jdata(val, row_item)
        else:
            text_list.append(key)
            text_list.append(str(val))
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)])


        tree_widget.addChild(row_item) #把東西加到樹上
        self.text_to_titem.append(text_list, row_item)


class JsonViewer(QtWidgets.QMainWindow):

    def __init__(self):
        super(JsonViewer, self).__init__()

        json_view = JsonView()

        self.setCentralWidget(json_view)
        self.setWindowTitle("JSON Viewer")
        self.setMinimumSize(800, 600)
        self.show()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()


if "__main__" == __name__:
    qt_app = QtWidgets.QApplication(sys.argv)
    json_viewer = JsonViewer()
    sys.exit(qt_app.exec_())




