# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tt.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

class ClickableLineEdit(QLineEdit):
    clicked = pyqtSignal()
    def mousePressEvent(self, event):
        self.clicked.emit()
        QLineEdit.mousePressEvent(self, event)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(400, 268)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(2, 10, 2, 0)
        self.verticalLayout_4.setSpacing(15)

        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_width = QtWidgets.QLabel(Dialog)
        self.label_width.setObjectName("label_width")
        self.verticalLayout.addWidget(self.label_width)
        self.label_height = QtWidgets.QLabel(Dialog)
        self.label_height.setObjectName("label_height")
        self.verticalLayout.addWidget(self.label_height)
        self.label_path_master = QtWidgets.QLabel(Dialog)
        self.label_path_master.setObjectName("label_path_master")
        self.verticalLayout.addWidget(self.label_path_master)
        self.label_path_slave = QtWidgets.QLabel(Dialog)
        self.label_path_slave.setObjectName("label_path_slave")
        self.verticalLayout.addWidget(self.label_path_slave)
        self.label_paht_output = QtWidgets.QLabel(Dialog)
        self.label_paht_output.setObjectName("label_paht_output")
        self.verticalLayout.addWidget(self.label_paht_output)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.line_width = QtWidgets.QLineEdit(Dialog)
        self.line_width.setObjectName("line_width")
        self.verticalLayout_2.addWidget(self.line_width)
        self.line_height = QtWidgets.QLineEdit(Dialog)
        self.line_height.setObjectName("line_height")
        self.verticalLayout_2.addWidget(self.line_height)
        self.line_path_master = QtWidgets.QLineEdit(Dialog)
        self.line_path_master.setObjectName("line_path_master")
        self.verticalLayout_2.addWidget(self.line_path_master)
        self.line_path_slave = QtWidgets.QLineEdit(Dialog)
        self.line_path_slave.setObjectName("line_path_slave")
        self.verticalLayout_2.addWidget(self.line_path_slave)
        self.line_path_output = QtWidgets.QLineEdit(Dialog)
        self.line_path_output.setObjectName("line_path_output")
        self.verticalLayout_2.addWidget(self.line_path_output)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.Btn_path_master = QtWidgets.QPushButton(Dialog)
        self.Btn_path_master.setObjectName("Btn_path_master")
        self.verticalLayout_3.addWidget(self.Btn_path_master)
        self.Btn_path_slave = QtWidgets.QPushButton(Dialog)
        self.Btn_path_slave.setObjectName("Btn_path_slave")
        self.verticalLayout_3.addWidget(self.Btn_path_slave)
        self.Btn_path_output = QtWidgets.QPushButton(Dialog)
        self.Btn_path_output.setObjectName("Btn_path_output")
        self.verticalLayout_3.addWidget(self.Btn_path_output)
        self.horizontalLayout_2.addLayout(self.verticalLayout_3)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 6, 0, 6)
        self.horizontalLayout_3.setSpacing(29)

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.radio_filter_Nl = QtWidgets.QRadioButton(Dialog)
        self.radio_filter_Nl.setObjectName("radio_filter_Nl")
        self.horizontalLayout_3.addWidget(self.radio_filter_Nl)
        self.radio_filter_Nl_2 = QtWidgets.QRadioButton(Dialog)
        self.radio_filter_Nl_2.setObjectName("radio_filter_Nl_2")
        self.horizontalLayout_3.addWidget(self.radio_filter_Nl_2)
        self.lineEdit = ClickableLineEdit()
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_3.addWidget(self.lineEdit)
        self.verticalLayout_4.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.Btn_OK = QtWidgets.QPushButton(Dialog)
        self.Btn_OK.setObjectName("Btn_OK")
        self.horizontalLayout.addWidget(self.Btn_OK)
        self.progressBar = QtWidgets.QProgressBar(Dialog)
        self.progressBar.setObjectName("progressBar")
        # self.progressBar.setFixedSize(300,20)

        self.horizontalLayout.addWidget(self.progressBar)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.Btn_Cancel = QtWidgets.QPushButton(Dialog)
        self.Btn_Cancel.setObjectName("Btn_Cancel")
        self.horizontalLayout.addWidget(self.Btn_Cancel)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_4, 0, 0, 1, 1)
        self.horizontalLayout.setContentsMargins(70, 0, 70, 0)
        self.horizontalLayout.setSpacing(20)

        self.progressBar.setVisible(False)
        self.progressBar.setMaximum(0)

        self.label_2.setVisible(False)


        self.Btn_path_master.clicked.connect(self.Btn_path_master_click)
        self.Btn_path_slave.clicked.connect(self.Btn_path_slave_click)
        self.Btn_path_output.clicked.connect(self.Btn_path_output_click)

        self.lineEdit.clicked.connect(self.set_window_size)
        self.radio_filter_Nl_2.click()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "滤波参数设置"))
        self.label_width.setText(_translate("Dialog", "影像宽度"))
        self.label_height.setText(_translate("Dialog", "影像高度"))
        self.label_path_master.setText(_translate("Dialog", "主影像路径"))
        self.label_path_slave.setText(_translate("Dialog", "从影像路径"))
        self.label_paht_output.setText(_translate("Dialog", "输出路径"))
        self.Btn_path_master.setText(_translate("Dialog", "更改"))
        self.Btn_path_slave.setText(_translate("Dialog", "更改"))
        self.Btn_path_output.setText(_translate("Dialog", "更改"))
        self.label.setText(_translate("Dialog", "滤波方式"))
        self.radio_filter_Nl.setText(_translate("Dialog", "NL滤波"))
        self.radio_filter_Nl_2.setText(_translate("Dialog", "Lee滤波"))
        self.lineEdit.setText(_translate("Dialog", "请设置Lee滤波窗口"))
        self.Btn_OK.setText(_translate("Dialog", "确定"))
        self.label_2.setText(_translate("Dialog", "程序运行中"))
        self.Btn_Cancel.setText(_translate("Dialog", "退出"))

    def Btn_path_master_click(self):
        print("master selection")
        fileDir, filetype = QFileDialog.getOpenFileName(None, "选取影像(*.tif)", "D:/workspace/","Amp Files (*.mli);;All Files (*)")
        if fileDir != '':
            self.line_path_master.setText(fileDir)

    def Btn_path_slave_click(self):
        print("slave selection")
        fileDir, filetype = QFileDialog.getOpenFileName(None, "选取影像(*.tif)", "D:/workspace/","Amp Files (*.mli);;All Files (*)")
        if fileDir != '':
            self.line_path_slave.setText(fileDir)

    def Btn_path_output_click(self):
        print("output selection")
        file_path = QtWidgets.QFileDialog.getExistingDirectory(None, "选取文件路径", "")
        if file_path != '':
            file_path = file_path+'/'
            self.line_path_output.setText(file_path)

    def set_window_size(self):
        self.lineEdit.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())