# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filter_NL.ui'
#
# Created by: PyQt5 UI code generator 5.15.0
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import sys

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(261, 350)
        self.label_title = QtWidgets.QLabel(Dialog)
        self.label_title.setGeometry(QtCore.QRect(90, 0, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        self.label_title.setFont(font)
        self.label_title.setObjectName("label_title")
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setGeometry(QtCore.QRect(10, 100, 231, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(10, 300, 93, 28))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setGeometry(QtCore.QRect(150, 300, 93, 28))
        self.pushButton_2.setObjectName("pushButton_2")
        self.line_3 = QtWidgets.QFrame(Dialog)
        self.line_3.setGeometry(QtCore.QRect(10, 234, 231, 20))
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.label_path_output = QtWidgets.QLabel(Dialog)
        self.label_path_output.setGeometry(QtCore.QRect(13, 262, 90, 16))
        self.label_path_output.setObjectName("label_path_output")
        self.line_path_output = QtWidgets.QLineEdit(Dialog)
        self.line_path_output.setGeometry(QtCore.QRect(90, 260, 151, 24))
        self.line_path_output.setObjectName("line_path_output")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 122, 122, 101))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_search_radius = QtWidgets.QLabel(self.layoutWidget)
        self.label_search_radius.setObjectName("label_search_radius")
        self.verticalLayout.addWidget(self.label_search_radius)
        self.label_adjacent_radius = QtWidgets.QLabel(self.layoutWidget)
        self.label_adjacent_radius.setObjectName("label_adjacent_radius")
        self.verticalLayout.addWidget(self.label_adjacent_radius)
        self.label_gaussian_para = QtWidgets.QLabel(self.layoutWidget)
        self.label_gaussian_para.setObjectName("label_gaussian_para")
        self.verticalLayout.addWidget(self.label_gaussian_para)
        self.layoutWidget1 = QtWidgets.QWidget(Dialog)
        self.layoutWidget1.setGeometry(QtCore.QRect(140, 116, 101, 111))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.line_search_radius = QtWidgets.QLineEdit(self.layoutWidget1)
        self.line_search_radius.setObjectName("line_search_radius")
        self.verticalLayout_3.addWidget(self.line_search_radius)
        self.line_adjacent_radius = QtWidgets.QLineEdit(self.layoutWidget1)
        self.line_adjacent_radius.setObjectName("line_adjacent_radius")
        self.verticalLayout_3.addWidget(self.line_adjacent_radius)
        self.line_gaussian_para = QtWidgets.QLineEdit(self.layoutWidget1)
        self.line_gaussian_para.setObjectName("line_gaussian_para")
        self.verticalLayout_3.addWidget(self.line_gaussian_para)
        self.label_image_stretch = QtWidgets.QLabel(Dialog)
        self.label_image_stretch.setGeometry(QtCore.QRect(13, 30, 71, 16))
        self.label_image_stretch.setObjectName("label_image_stretch")
        self.Btn_image_stretch = QtWidgets.QPushButton(Dialog)
        self.Btn_image_stretch.setGeometry(QtCore.QRect(179, 27, 61, 21))
        font = QtGui.QFont()
        font.setFamily("Agency FB")
        font.setPointSize(8)
        self.Btn_image_stretch.setFont(font)
        self.Btn_image_stretch.setObjectName("Btn_image_stretch")
        self.text_image_stretch = QtWidgets.QTextEdit(Dialog)
        self.text_image_stretch.setGeometry(QtCore.QRect(10, 50, 231, 51))
        self.text_image_stretch.setObjectName("text_image_stretch")

        self.Btn_image_stretch.clicked.connect(self.Btn_image_stretch_click)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_title.setText(_translate("Dialog", "NL滤波"))
        self.pushButton.setText(_translate("Dialog", "OK"))
        self.pushButton_2.setText(_translate("Dialog", "Cancle"))
        self.label_path_output.setText(_translate("Dialog", "输出文件路径"))
        self.label_search_radius.setText(_translate("Dialog", "搜索窗口半径"))
        self.label_adjacent_radius.setText(_translate("Dialog", "邻域窗口半径"))
        self.label_gaussian_para.setText(_translate("Dialog", "滤波强度"))
        self.label_image_stretch.setText(_translate("Dialog", "待滤波影像"))
        self.Btn_image_stretch.setText(_translate("Dialog", "打开"))

    def Btn_image_stretch_click(self):
        fileDir, filetype = QFileDialog.getOpenFileNames(None, "选取影像(*.tif)", "D:/workspace/","TIFF Files (*.tif);;All Files (*)")
        fileList_str = ''
        if fileDir != '':
            for file in fileDir:
                fileList_str = fileList_str+file+'\n'
            self.text_image_stretch.setText(fileList_str)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())