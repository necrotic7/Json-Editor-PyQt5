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
        jdata = json.load(jfile, object_pairs_hook=collections.OrderedDict)##

        #define widgets
        self.savefile_btn = QtWidgets.QPushButton("Save")
        self.filenames = filenames
        self.savefile_btn.clicked.connect(self.Save_textEdit)
        self.restart_btn = QtWidgets.QPushButton("Restart")
        self.restart_btn.clicked.connect(self.restart)

        # Tree
        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.header().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)##
        root_item = QtWidgets.QTreeWidgetItem(["Root"])
        self.recurse_jdata(jdata, root_item)
        self.tree_widget.addTopLevelItem(root_item)#Add root on tree
        selmodel = self.tree_widget.selectionModel()
        selmodel.selectionChanged.connect(self.handleSelection)


        #add widgets to layout
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree_widget)
        layout.addWidget(self.textEdit)
        table_gbox = QtWidgets.QGroupBox(filenames[0])
        table_gbox.setLayout(layout)

        layout2 = QtWidgets.QHBoxLayout()
        layout2.addWidget(self.savefile_btn)
        layout2.addWidget(self.restart_btn)
        btn_gbox = QtWidgets.QGroupBox()
        btn_gbox.setLayout(layout2)

        layout3 = QtWidgets.QVBoxLayout()
        layout3.addWidget(table_gbox)
        layout3.addWidget(btn_gbox)
        self.setLayout(layout3)

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
        if isinstance(val, dict) or isinstance(val, list):#如果為還能拆解的dict, list 就再送回去拆解
            row_item = QtWidgets.QTreeWidgetItem([key])
            self.recurse_jdata(val, row_item)
        else:
            row_item = QtWidgets.QTreeWidgetItem([key, str(val)])

        tree_widget.addChild(row_item) #add on tree


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




