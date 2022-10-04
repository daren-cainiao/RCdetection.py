# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SAR.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import os, shutil, sys, configparser
from datetime import datetime
import SBAS

class Ui_MainWindow(QtWidgets.QWidget):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(958, 840)
        MainWindow.setDocumentMode(False)
        self.rootpath="D:/"
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeView = QtWidgets.QTreeView(self.centralwidget)
        self.treeView.setGeometry(QtCore.QRect(10, 10, 301, 491))
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.treeView.setObjectName("treeView")
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(10, 510, 921, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.tableView.setGeometry(QtCore.QRect(350, 10, 581, 491))
        self.tableView.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tableView.setObjectName("tableView")
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setGeometry(QtCore.QRect(320, 10, 21, 491))
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 540, 921, 251))
        self.textBrowser.setObjectName("textBrowser")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 958, 26))
        self.menubar.setObjectName("menubar")
        self.menufile = QtWidgets.QMenu(self.menubar)
        self.menufile.setObjectName("menufile")
        self.menu_6 = QtWidgets.QMenu(self.menufile)
        self.menu_6.setObjectName("menu_6")
        self.menu_7 = QtWidgets.QMenu(self.menufile)
        self.menu_7.setObjectName("menu_7")
        self.menu = QtWidgets.QMenu(self.menubar)
        self.menu.setObjectName("menu")
        self.menuPS = QtWidgets.QMenu(self.menu)
        self.menuPS.setObjectName("menuPS")
        self.menu_2 = QtWidgets.QMenu(self.menubar)
        self.menu_2.setObjectName("menu_2")
        self.menu_3 = QtWidgets.QMenu(self.menubar)
        self.menu_3.setObjectName("menu_3")
        self.menu_4 = QtWidgets.QMenu(self.menubar)
        self.menu_4.setObjectName("menu_4")
        self.menu_5 = QtWidgets.QMenu(self.menubar)
        self.menu_5.setObjectName("menu_5")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.action_2 = QtWidgets.QAction(MainWindow)
        self.action_2.setObjectName("action_2")
        self.action_4 = QtWidgets.QAction(MainWindow)
        self.action_4.setObjectName("action_4")
        self.action_5 = QtWidgets.QAction(MainWindow)
        self.action_5.setObjectName("action_5")
        self.action_6 = QtWidgets.QAction(MainWindow)
        self.action_6.setObjectName("action_6")
        self.actionSBAS = QtWidgets.QAction(MainWindow)
        self.actionSBAS.setObjectName("actionSBAS")
        self.actionPS = QtWidgets.QAction(MainWindow)
        self.actionPS.setObjectName("actionPS")
        self.action_7 = QtWidgets.QAction(MainWindow)
        self.action_7.setCheckable(False)
        self.action_7.setObjectName("action_7")
        self.action_3 = QtWidgets.QAction(MainWindow)
        self.action_3.setObjectName("action_3")
        self.action_8 = QtWidgets.QAction(MainWindow)
        self.action_8.setObjectName("action_8")
        self.actiongsview = QtWidgets.QAction(MainWindow)
        self.actiongsview.setObjectName("actiongsview")
        self.menu_6.addAction(self.action_7)
        self.menu_6.addAction(self.action_3)
        self.menu_7.addAction(self.action_8)
        self.menufile.addAction(self.menu_7.menuAction())
        self.menufile.addAction(self.action_2)
        self.menufile.addAction(self.menu_6.menuAction())
        self.menufile.addAction(self.action_4)
        self.menufile.addAction(self.action_5)
        self.menufile.addAction(self.action_6)
        self.menu.addAction(self.actionPS)
        self.menu.addAction(self.actionSBAS)
        self.menu_2.addAction(self.actiongsview)
        self.menubar.addAction(self.menufile.menuAction())
        self.menubar.addAction(self.menu.menuAction())
        self.menubar.addAction(self.menu_2.menuAction())
        self.menubar.addAction(self.menu_3.menuAction())
        self.menubar.addAction(self.menu_4.menuAction())
        self.menubar.addAction(self.menu_5.menuAction())
        self.retranslateUi(MainWindow)
        self.action_3.triggered.connect(self.opendir)
        self.action_8.triggered.connect(self.create_pro)
        self.actiongsview.triggered.connect(self.gsshow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "SAR数据处理平台"))
        self.menufile.setTitle(_translate("MainWindow", "文件"))
        self.menu_6.setTitle(_translate("MainWindow", "打开"))
        self.menu_7.setTitle(_translate("MainWindow", "新建项目"))
        self.menu.setTitle(_translate("MainWindow", "功能"))
        self.menuPS.setTitle(_translate("MainWindow", "PS"))
        self.menu_2.setTitle(_translate("MainWindow", "工具"))
        self.menu_3.setTitle(_translate("MainWindow", "设置"))
        self.menu_4.setTitle(_translate("MainWindow", "帮助"))
        self.menu_5.setTitle(_translate("MainWindow", "退出"))
        self.action_2.setText(_translate("MainWindow", "新建"))
        self.action_4.setText(_translate("MainWindow", "保存"))
        self.action_5.setText(_translate("MainWindow", "另存为"))
        self.action_6.setText(_translate("MainWindow", "退出"))
        self.actionSBAS.setText(_translate("MainWindow", "SBAS"))
        self.actionPS.setText(_translate("MainWindow", "PS"))
        self.action_7.setText(_translate("MainWindow", "文件"))
        self.action_3.setText(_translate("MainWindow", "文件夹"))
        self.action_8.setText(_translate("MainWindow", "新建"))
        self.actiongsview.setText(_translate("MainWindow", "gsview"))

    def opendir(self):
        dir = QFileDialog.getExistingDirectory(self, "选取文件夹", self.rootpath)  # 起始路径
        self.model = QFileSystemModel()
        self.model.setRootPath(dir)
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(dir))

    def create_pro(self):
        workspace2, ok2 = QFileDialog.getSaveFileName(self, "生成项目", "D:/", "All Files (*);;Text Files (*.ini)")
        self.textBrowser.append('生成项目名称：' + workspace2)
        prj_dir = workspace2.split('.')[0]
        prj_data_dir = workspace2.split('.')[0]+'/data'

        # 创建管理对象
        conf = configparser.ConfigParser(allow_no_value=True)
        if not os.path.exists(prj_dir):
            os.makedirs(prj_dir)
            os.makedirs(prj_data_dir)
            configfile = prj_dir + '/config.ini'
            shutil.copyfile("D:/cygwin64/project/cmd/config.ini", configfile)
            conf.read(configfile)
            now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conf.set("项目", "项目名称", configfile)
            conf.set("项目", "项目路径", prj_dir)
            conf.set("项目", "创建时间", now_time)
            conf.write(open(configfile, "w"))
        else:
            prj_dir = prj_dir + "_new"
            os.makedirs(prj_dir)
        self.textBrowser.append('创建工程目录：' + prj_dir)
        self.rootpath = os.path.abspath(os.path.join(prj_dir, "../"))
        self.model = QFileSystemModel()
        self.model.setRootPath(self.rootpath)
        self.treeView.setModel(self.model)
        self.treeView.setRootIndex(self.model.index(self.rootpath))

    def gsshow(self):
        os.popen("D:\cygwin64\Ghostgum\gsview\gsview64.exe")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())


