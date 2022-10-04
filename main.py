# -*- coding: utf-8 -*-

# F1orm implementation generated from reading ui file 'main.py'
#1e
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

import sys,os
if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']
import Prepare,SBAS
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
import multiprocessing as mp

filename = ""
class parentWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setFixedSize(958, 840)
        self.main_ui = Prepare.Ui_MainWindow()
        self.main_ui.setupUi(self)

    def openMyDialog(self):
        my = child1Window()
        # 在主窗口中连接信号和槽
        global filename
        rootpath = os.path.abspath(os.path.join(filename, "../"))
        dir = rootpath + '\config.ini'
        print("更改目录为：", dir)
        if os.path.exists(dir):
            my.child1_ui.groupBox.setVisible(True)
            my.child1_ui.groupBox_2.setVisible(True)
            my.child1_ui.lineEdit.setText(dir)
        else:
            buttonReply = QMessageBox.question(my.child1_ui, '错误信息', "请选择正确的项目工程", QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
            if buttonReply ==QMessageBox.Yes:
                print('Yes clicked.')
            else:
                print('No clicked.')
        my.exec_()

    def openMyDialog1(self):
        my = child2Window()
        # 在主窗口中连接信号和槽
        global filename
        rootpath = os.path.abspath(os.path.join(filename, "../"))
        dir = rootpath + '\config.ini'
        print("更改目录为：", dir)
        if os.path.exists(dir):
            my.child2_ui.groupBox.setVisible(True)
            my.child2_ui.groupBox_2.setVisible(True)
            my.child2_ui.lineEdit.setText(dir)
        else:
            buttonReply = QMessageBox.question(my.child2_ui, '错误信息', "请选择正确的项目工程", QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
            if buttonReply ==QMessageBox.Yes:
                print('Yes clicked.')
            else:
                print('No clicked.')
        my.exec_()
    def tree_clicked(self, Qmodelidx):
        print("tree_clicked  is ")
        global filename
        filename=self.main_ui.model.filePath(Qmodelidx)
        self.main_ui.statusbar.showMessage(filename)

class child1Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child1_ui = SBAS.Ui_Dialog()
        self.child1_ui.setupUi(self)
class child2Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child2_ui = PS_InSAR.Ui_Dialog()
        self.child2_ui.setupUi(self)
        self.child2_ui.groupBox_2.setVisible(False)

if __name__ == '__main__':
    mp.freeze_support()
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = parentWindow()
    window.setStyleSheet("#MainWindow{border-image:url(./img/timg.jpg);}")
    window.setWindowIcon(QtGui.QIcon('./img/r11.ico'))
    btn = window.main_ui.actionSBAS
    btn.triggered.connect(window.openMyDialog)
    btn1 = window.main_ui.actionPS
    btn1.triggered.connect(window.openMyDialog1)
    tree = window.main_ui.treeView
    tree.clicked.connect(window.tree_clicked)
    window.show()
    sys.exit(app.exec_())
