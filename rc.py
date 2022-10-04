# _*_ coding:utf-8 _*_
# author: wangcheng
# data: 2021/3/9 13:20
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
import os, shutil, sys, configparser, re, struct
import select_files, select_master
import filter_selection,filter_pre,filter_NL,filter_Lee
import sample_selection
import datetime, time
import xml.dom.minidom
import cv2
import numpy as np
import win32api,win32con
from PIL import Image
import subprocess
from osgeo import gdal, osr, gdal_array
import sys
import scipy


def getCoordinate(trans_dat):
    trans_size = os.path.getsize(trans_dat)
    trans_width = 5
    trans_height = trans_size / (5 * 8)  # 5为宽度，8为字节数（double）
    trans_dat_data = np.fromfile(trans_dat, 'd')
    trans_dat_data = trans_dat_data.reshape(int(trans_height), int(trans_width))
    LonMin = trans_dat_data[:, 3].min()
    LonMax = trans_dat_data[:, 3].max()
    LatMin = trans_dat_data[:, 4].min()
    LatMax = trans_dat_data[:, 4].max()

    return [LonMin, LonMax, LatMin, LatMax]

def geoCodeTiff(in_filename, out_filename, coord):
    bands = 3
    src_ds = gdal.Open(in_filename)
    if src_ds is None:
        print("open failed")
        sys.exit()

    width = src_ds.RasterXSize
    height = src_ds.RasterYSize
    print(str(src_ds.RasterXSize))  # 宽度 1090
    print(str(src_ds.RasterYSize))  # 高度 1530

    data_Array = cv2.imread(in_filename, -1)
    data_Array = np.asarray(data_Array)
    # data_Array = load_grd(in_filename, shape=(height, width))
    # data_Array = data_Array.reshape(height,width)
    data_Array = np.flipud(data_Array)  #翻转图像
    #data_Array = np.fliplr(data_Array)  #翻转图像

    [LonMin, LonMax, LatMin, LatMax] = coord
    N_Lon = width
    N_Lat = height
    density_lat = (LatMax - LatMin) / (N_Lat-1)
    density_lon = (LonMax - LonMin) / (N_Lon-1)
    #M = [LatMin:-density_lat: LatMax]
    #N = [LonMax:density_lon: LonMax]
    M = np.linspace(LatMax, LatMin, density_lat)
    N = np.linspace(LonMin, LonMax, density_lon)
    [lon_n, lat_n] = np.meshgrid(N, M)
    data_Array = scipy.interpolate.griddata(data_Array,lat_n,lon_n,'linear')

    Lon_Res = (LonMax - LonMin) / (float(N_Lon) - 1)
    Lat_Res = (LatMax - LatMin) / (float(N_Lat) - 1)
    spei_ds = gdal.GetDriverByName('Gtiff').Create(out_filename, N_Lon, N_Lat, bands, gdal.GDT_Float32)
    # ("fdem_new.tif", 栅格矩阵的列数, 栅格矩阵的行数, 波段数, 数据类型)

    # 设置影像的显示范围
    geotransform = (LonMin, Lon_Res, 0, LatMin, 0, Lat_Res)
    spei_ds.SetGeoTransform(geotransform)

    # 地理坐标系统信息
    srs = osr.SpatialReference()  # 获取地理坐标系统信息，用于选取需要的地理坐标系统
    print(type(srs))
    print(srs)
    srs.ImportFromEPSG(4326)  # 定义输出的坐标系为"WGS 84"，AUTHORITY["EPSG","4326"]
    spei_ds.SetProjection(srs.ExportToWkt())  # 给新建图层赋予投影信息

    # 数据写出
    if bands == 1:
        spei_ds.GetRasterBand(1).WriteArray(data_Array)  # 将数据写入内存
    else:
        for i in range(bands):
            spei_ds.GetRasterBand(bands-i).WriteArray(data_Array[:,:,i])  # 将数据写入内存
    spei_ds.FlushCache()  # 将数据写入硬盘
    spei_ds = None  # 关闭spei_ds指针

def nearest(in_filename_lon, out_filename_lon, nline_in, width_in):
    # 0：读取数据
    line_scale_factor = 4 # 高度过采样因子
    width_scale_factor = 2 #宽度过采样因子
    nlines_out = nline_in * line_scale_factor  #高度
    width_out = width_in * width_scale_factor  #宽度

    data_file = np.fromfile(in_filename_lon, 'f')
    data_file = data_file.reshape(nline_in, width_in)

    # 1：按照尺寸创建目标图像
    target_image = np.zeros((nlines_out, width_out))

    # 2:计算height和width的缩放因子
    #alpha_h = target_size[0] / image.shape[0]
    #alpha_w = target_size[1] / image.shape[1]
    alpha_h = line_scale_factor
    alpha_w = width_scale_factor

    #for tar_x in range(target_image.shape[0] - 1):
        #for tar_y in range(target_image.shape[1] - 1):
    for tar_x in range(target_image.shape[0]):
        for tar_y in range(target_image.shape[1]):
            # 3:计算目标图像人任一像素点
            # target_image[tar_x,tar_y]需要从原始图像
            # 的哪个确定的像素点image[src_x, xrc_y]取值
            # 也就是计算坐标的映射关系
            src_x = round(tar_x / alpha_h)
            src_y = round(tar_y / alpha_w)

            # 4：对目标图像的任一像素点赋值
            if (src_x == nline_in) and (src_y == width_in):
                target_image[tar_x, tar_y] = data_file[nline_in - 1, width_in - 1]
            elif (src_x == nline_in):
                target_image[tar_x, tar_y] = data_file[nline_in - 1, src_y]
            elif (src_y == width_in):
                target_image[tar_x, tar_y] = data_file[src_x, width_in - 1]
            else:
                target_image[tar_x, tar_y] = data_file[src_x, src_y]

    # 输出数据
    out_data = target_image.astype('<f')
    out_data.tofile(out_filename_lon)
    #return target_image


def readTrans(trans_dat):
    trans_size = os.path.getsize(trans_dat)
    trans_width = 5
    trans_height = trans_size / (5 * 8)  # 5为宽度，8为字节数（double）
    trans_dat_data = np.fromfile(trans_dat, 'd')
    trans_dat_data = trans_dat_data.reshape(int(trans_height), int(trans_width))

    return trans_dat_data

def getCoordinate(trans_dat_data):
    LonMin = trans_dat_data[:, 3].min()
    LonMax = trans_dat_data[:, 3].max()
    LatMin = trans_dat_data[:, 4].min()
    LatMax = trans_dat_data[:, 4].max()

    return [LonMin, LonMax, LatMin, LatMax]


def geoCodeTiff_new(base_dir, master):
    configini = base_dir + '/filter.ini'
    cf = configparser.ConfigParser(allow_no_value=True)
    cf.read(configini)

    trans_dat = base_dir + r'\RSLC\trans.dat'
    #topo_ra = base_dir + r'\RSLC\20170223\topo_ra.grd'
    topo_ra = base_dir + r'\RSLC' + '\\' +str(master) + r'\topo_ra.grd'

    # 复制文件
    compose_dir = base_dir + r'\composed'
    shutil.copyfile(trans_dat, compose_dir + r'\trans.dat')
    shutil.copyfile(topo_ra, compose_dir + r'\topo_ra.grd')

    # 调用cmd处理 生成longitude和latitude吻技安
    out_cf_name = base_dir
    cmd = "D:/cygwin64/project/cmd/geocode_xu.bat  " + out_cf_name  # cmd执行滤波预处理
    # os.system(cmd)
    tmp = os.popen(cmd).readlines()
    print(tmp)

    # 生成longitude_osp和latitude_osp
    #nline_in = 934
    #width_in = 1292
    width = int(float(cf.get('PARAMETER-PRE', 'width')))
    height = int(float(cf.get('PARAMETER-PRE', 'height')))
    width_in = int(width/2)
    nline_in = int(height/4)
    in_filename_lon = compose_dir + r'\longitude'
    out_filename_lon = compose_dir + r'\longitude_osp'
    in_filename_lat = compose_dir + r'\latitude'
    out_filename_lat = compose_dir + r'\latitude_osp'
    nearest(in_filename_lon, out_filename_lon, nline_in, width_in)
    nearest(in_filename_lat, out_filename_lat, nline_in, width_in)

    # 调用matlab代码地理编码
    print("geocoding...")
    inifile = configini
    cmd = "D:/cygwin64/project/rc/tiff2geotiff.exe  " + inifile  # cmd执行滤波预处理
    # os.system(cmd)
    tmp = os.popen(cmd).readlines()
    print(tmp)



class Ui_Dialog(QtWidgets.QDialog):

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(216, 264)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.pushButton_1 = QtWidgets.QPushButton(Dialog)
        self.pushButton_1.setObjectName("pushButton_1")
        self.gridLayout.addWidget(self.pushButton_1, 5, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(Dialog)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 6, 0, 1, 1)
        self.progressBar_3 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_3.setMaximumSize(QtCore.QSize(40, 16777215))
        self.progressBar_3.setProperty("value", 0)
        self.progressBar_3.setTextVisible(False)
        self.progressBar_3.setObjectName("progressBar_3")
        self.gridLayout.addWidget(self.progressBar_3, 7, 1, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMaximumSize(QtCore.QSize(16777215, 15))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.progressBar_4 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_4.setMaximumSize(QtCore.QSize(40, 16777215))
        self.progressBar_4.setProperty("value", 0)
        self.progressBar_4.setTextVisible(False)
        self.progressBar_4.setObjectName("progressBar_4")
        self.gridLayout.addWidget(self.progressBar_4, 8, 1, 1, 1)
        self.progressBar_2 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.progressBar_2.setProperty("value", 0)
        self.progressBar_2.setTextVisible(False)
        self.progressBar_2.setObjectName("progressBar_2")
        self.gridLayout.addWidget(self.progressBar_2, 6, 1, 1, 1)
        self.pushButton_4 = QtWidgets.QPushButton(Dialog)
        self.pushButton_4.setObjectName("pushButton_4")
        self.gridLayout.addWidget(self.pushButton_4, 8, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(Dialog)
        self.pushButton_3.setObjectName("pushButton_3")
        self.gridLayout.addWidget(self.pushButton_3, 7, 0, 1, 1)
        self.line = QtWidgets.QFrame(Dialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.gridLayout.addWidget(self.line, 4, 0, 1, 2)
        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 1, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setMaximumSize(QtCore.QSize(40, 16777215))
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 1, 1, 1)
        self.pushButton_5 = QtWidgets.QPushButton(Dialog)
        self.pushButton_5.setObjectName("pushButton_5")
        self.gridLayout.addWidget(self.pushButton_5, 9, 0, 1, 1)
        self.progressBar_5 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_5.setMaximumSize(QtCore.QSize(40, 16777215))
        self.progressBar_5.setProperty("value", 0)
        self.progressBar_5.setTextVisible(False)
        self.progressBar_5.setObjectName("progressBar_5")
        self.gridLayout.addWidget(self.progressBar_5, 9, 1, 1, 1)
        self.progressBar_1 = QtWidgets.QProgressBar(Dialog)
        self.progressBar_1.setMaximumSize(QtCore.QSize(40, 16777215))
        self.progressBar_1.setProperty("value", 0)
        self.progressBar_1.setTextVisible(False)
        self.progressBar_1.setObjectName("progressBar_1")
        self.gridLayout.addWidget(self.progressBar_1, 5, 1, 1, 1)

        #设置button为不可用
        self.pushButton_1.setEnabled(False)
        self.pushButton_2.setEnabled(False)
        self.pushButton_3.setEnabled(False)
        self.pushButton_4.setEnabled(False)
        self.pushButton_5.setEnabled(False)

        self.pushButton.clicked.connect(self.change_workspace)
        self.pushButton_1.clicked.connect(self.pushbutton_1_click)
        self.pushButton_2.clicked.connect(self.pushbutton_2_click)
        self.pushButton_3.clicked.connect(self.pushbutton_3_click)
        self.pushButton_4.clicked.connect(self.pushbutton_4_click)
        self.pushButton_5.clicked.connect(self.pushbutton_5_click)

        self.retranslateUi(Dialog)
        #self.buttonBox.rejected.connect(Dialog.reject)
        #self.buttonBox.accepted.connect(Dialog.accept)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "高分SAR变化监测"))
        #self.groupBox.setTitle(_translate("Dialog", "数据处理流"))
        self.pushButton_1.setText(_translate("Dialog", "导入数据"))
        self.pushButton_2.setText(_translate("Dialog", "影像配准"))
        self.pushButton_3.setText(_translate("Dialog", "影像裁剪"))
        self.pushButton_4.setText(_translate("Dialog", "滤波"))
        self.pushButton_5.setText(_translate("Dialog", "半自动提取"))

        self.pushButton.setText(_translate("Dialog", "更改"))
        self.label.setText(_translate("Dialog", "设置工程目录："))

    def change_workspace(self):
        '''
        global workspace, input_txt_path
        dir , filetype= QFileDialog.getOpenFileName(self, "选取工程文件(*.ini)", "D:/workspace/")
        self.configfile = dir
        if os.path.exists(dir):
            self.lineEdit.setText(dir)
            self.set_params()
        else:
            buttonReply = QMessageBox.question(self, '错误信息', "请选择正确的项目工程", QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')
            else:
                print('No clicked.')
        '''

        # 选取工程文件夹
        directory = QtWidgets.QFileDialog.getExistingDirectory(None, "选取工程文件夹", "D:/workspace/")  # 起始路径
        print(directory)
        config_file = directory + '/config.ini'
        batch_dir = directory + '/data'
        batch_file = batch_dir + '/batch.ini'
        dir = config_file
        conf = configparser.ConfigParser(allow_no_value=True)
        #if os.path.exists(config_file) and os.path.exists(batch_file):
        if os.path.exists(config_file):
            print("file exiets, skip this step")
        else:
            shutil.copyfile("D:/cygwin64/project/cmd/config_GF.ini", config_file)
            #if not os.path.exists(batch_dir):
            #    os.mkdir(batch_dir)
            #shutil.copyfile("D:/cygwin64/project/cmd/batch_GF.ini", batch_file)

            conf.read(config_file)
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conf.set("项目", "项目名称", config_file)
            conf.set("项目", "项目路径", directory)
            conf.set("项目", "创建时间", now_time)
            conf.write(open(config_file, "w"))

        print("更改目录为：", dir)
        self.configfile = dir
        if os.path.exists(dir):
            print('-----1------')
            # self.lineEdit.setText(dir)
            self.lineEdit.setText(directory)
            self.set_params()
            global filepath2ini
            filepath2ini = directory

            '''
            self.parseconfig()
            self.groupBox.setVisible(True)
            self.filepath = os.path.abspath(os.path.join(dir, "../"))
            self.batchfile = self.filepath + '/data/batch.ini'
            global batchfile
            batchfile = self.batchfile
            global filepath2ini
            filepath2ini = self.filepath
            print(filepath2ini)
            '''
        else:
            print('-----3------')
            buttonReply = QMessageBox.question(self, '错误信息', "请选择正确的项目工程", QMessageBox.Yes | QMessageBox.No,
                                               QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                print('Yes clicked.')
            else:
                print('No clicked.')

    def set_params(self):
        global workspace, input_txt_path
        self.parseconfig()
        #self.groupBox.setVisible(True)
        # 设置button为可用
        self.pushButton_1.setEnabled(True)
        self.pushButton_2.setEnabled(True)
        self.pushButton_3.setEnabled(True)
        self.pushButton_4.setEnabled(True)
        self.pushButton_5.setEnabled(True)

        workspace = os.path.abspath(os.path.join(self.configfile, "../"));
        self.workspace = workspace
        self.datafile = self.workspace + '/data/'
        input_txt_path = self.datafile + '/input.txt';
        self.input_txt_path = input_txt_path
        self.image_date = []
        #self.set_config("other", "method", "SBAS")
        self.set_config("other", "method", "Process")

    def change_txt(self):
        txt_file = ["input2.txt", "input3.txt"]
        for i in range(len(txt_file)):
            swath_txt_path = self.workspace + "/data/" + txt_file[i]
            lines = open(swath_txt_path).readlines()
            input_txt_modify = open(swath_txt_path, 'w')
            for date in self.image_date:
                for line in lines:
                    if line.split("_")[1] == date:
                        input_txt_modify.write(line)
                        lines.remove(line)
                        break
            input_txt_modify.close()

    def change_status(self, status):
        status_text = ["", "导入数据", "影像配准", "影像裁剪", "滤波", "半自动提取"]
        for i in range(status, len(status_text)):
            self.set_config("Process", status_text[i], "0")
            progressBar_name = "self.progressBar_" + str(i) + ".setValue(0)"
            eval(progressBar_name)

    def create_tsx_input(self, file_path):  # 筛选terrasar数据cos和xml文件，生成input.txt文件
        contents = []
        input_txt = open(self.input_txt_path, "w")
        for maindir, subdir, file_name in os.walk(file_path):
            if maindir.endswith('IMAGEDATA'):
                cos_path = os.path.join(maindir, str(file_name[0]))
                mode = cos_path.split("_")[-2]
                filepath = os.path.abspath(os.path.join(cos_path, "../.."))
                date = os.path.basename(filepath).split('_')[12][:8]
                self.image_date.append(date)
                xml_file = os.path.basename(filepath) + '.xml'
                xml_path = os.path.join(filepath, xml_file)
                Elements = xml.dom.minidom.parse(xml_path).documentElement
                orbitdirection = Elements.getElementsByTagName('orbitDirection')[0].firstChild.data
                polar = Elements.getElementsByTagName('polLayer')[0].firstChild.data
                name = "tsx" + '_' + str(date) + '_' + polar.lower() + '_' + orbitdirection[0].lower() + '_' + mode
                content = [name, xml_path, cos_path]
                contents.append(content)
        files = sorted(contents, key=lambda y: y[0][4:12])
        for file in files:
            input_txt.write(file[0] + '#' + file[1] + '#' + file[2] + '\n')
        input_txt.close()
        return True

    def create_csk_input(self, file_path):  ##筛选cosmo数据的h5文件，生成input.txt文件
        contents = []
        input_txt = open(self.input_txt_path, "w")
        for maindir, subdir, file_name_list in os.walk(file_path):
            for file in file_name_list:
                if file.endswith("h5"):
                    image_path = os.path.join(maindir, str(file))
                    self.image_date.append(file.split("_")[8][0:8])
                    name = "csk_" + file.split("_")[8][0:8] + "_" + str(image_path.split("_")[-5]).lower() + "_" + str(
                        image_path.split("_")[-4])
                    contents.append([name, image_path])
        files = sorted(contents, key=lambda y: y[0][4:11])
        for file in files:
            input_txt.write(file[0] + '#' + file[1] + '\n')
        input_txt.close()
        return True

    def create_sentinel_input(self, raw_paths, file_filter, orbits_path):  # 筛选哨兵数据中的tiff xml 和轨道文件，生成input文件
        subwath = file_filter.split('-')[1]
        polar = file_filter.split('-')[3]
        if "123" in subwath:
            file_filter = ["-iw1-slc-" + polar + "-", "-iw2-slc-" + polar + "-", "-iw3-slc-" + polar + "-"]
            txt_file = ["input.txt", "input2.txt", "input3.txt"]
        else:
            file_filter = [file_filter]
            txt_file = ["input.txt"]
        for i in range(len(file_filter)):
            selector = file_filter[i]
            swath_txt_path = self.datafile + txt_file[i]
            xml_path = [];
            tiff_path = [];
            eof_path = [];
            filepath_name = [];
            for maindir, subdir, file_name_list in os.walk(raw_paths):
                if maindir.endswith('measurement'):
                    for f in file_name_list:
                        if f[3:].startswith(selector):
                            current_tiff_path = os.path.join(maindir, str(f))
                            tiff_path.append(current_tiff_path)
                            abspath = os.path.dirname(os.path.dirname(current_tiff_path))
                            f = f.split('.')[0] + ".xml"
                            date = re.findall(".*v*-(.*)t.*t.*x", f)
                            current_xml_path = abspath + "/annotation/" + f
                            Elements = xml.dom.minidom.parse(current_xml_path).documentElement
                            orbitdirection = Elements.getElementsByTagName('pass')[0].firstChild.data
                            name = str(f[0:3]) + '_' + str(date[0]) + '_' + polar + '_' + orbitdirection[
                                0].lower() + '_F' + selector.split('-')[1][2]
                            filepath_name.append(name)
                            self.image_date.append(date)
                            xml_path.append(current_xml_path)
                            for or_maindir, or_subdir, or_file_name_list in os.walk(orbits_path):
                                for or_f in or_file_name_list:
                                    date1 = re.findall(".*V(.*)T.*_", or_f)
                                    if "EOF" in or_f:
                                        date1 = self.getdate(date1)
                                        if date[0] == date1:
                                            current_orbots_path = os.path.join(or_maindir, str(or_f))
                                            eof_path.append(current_orbots_path)
                                    elif "eof" in or_f:
                                        if date[0] == date1[0]:
                                            current_orbots_path = os.path.join(or_maindir, str(or_f))
                                            eof_path.append(current_orbots_path)
            file = open(swath_txt_path, "w")
            for r in range(len(filepath_name)):
                file.write(filepath_name[r] + "#" + xml_path[r] + "#" + tiff_path[r] + "#" + eof_path[r])
                file.write('\n')
            file.close()
        return True

    def create_master_mli(self, file, row, column):  # 生成主影像的图片，用于选取裁剪范围
        SLC_file = open(file, "rb")
        GB = 0.01 * 1024 * 1024 * 1024 / 4
        total = row * column
        out = np.ones((1, total))
        if GB < total:
            limit_row = int(GB // column)
            left = int(np.mod(row, limit_row))
            iters = int(row // limit_row)
        else:
            iters = 1
            limit_row = row
            left = 0
        for i in range(iters):
            total = limit_row * column
            origin_data = SLC_file.read(4 * total)
            rule = "<" + "hh" * total
            data_unpack = struct.unpack(rule, origin_data)
            data_unpack = np.array(data_unpack).reshape(total, 2)
            real_pow = data_unpack[:, 0] * data_unpack[:, 0]
            imag_pow = data_unpack[:, 1] * data_unpack[:, 1]
            out[:, i * total:(i + 1) * total] = np.sqrt(real_pow + imag_pow)
            del origin_data;
            del data_unpack;
            del real_pow;
            del imag_pow
        total = left * column
        origin_data = SLC_file.read(4 * total)
        rule = "<" + "hh" * total
        data_unpack = struct.unpack(rule, origin_data)
        data_unpack = np.array(data_unpack).reshape(total, 2)
        real_pow = data_unpack[:, 0] * data_unpack[:, 0]
        imag_pow = data_unpack[:, 1] * data_unpack[:, 1]
        out[:, -total:] = np.sqrt(real_pow + imag_pow)
        out_image = cv2.pyrDown(cv2.pyrDown(cv2.pyrDown(out.reshape([row, column]))))
        cv2.imwrite(self.datafile + '/master.png', out_image)
        del origin_data;
        del data_unpack;
        del real_pow;
        del imag_pow
        SLC_file.close()

    def getdate(self, date):
        a1 = datetime.datetime.strptime(date[0], "%Y%m%d")
        # 计算偏移量
        offset = datetime.timedelta(days=1)
        # 获取想要的日期的时间
        re_date = (a1 + offset).strftime('%Y%m%d')
        return str(re_date)

    def get_config(self, section1, section2):
        cf = configparser.ConfigParser()
        cf.read(self.configfile)
        result = cf.get(section1, section2)
        return result

    def set_config(self, section1, section2, num):
        cf = configparser.ConfigParser()
        cf.read(self.configfile)
        cf.set(section1, section2, num)
        cf.write(open(self.configfile, "w"))

    def parseconfig(self):
        status_text = ["", "导入数据", "影像配准", "影像裁剪", "滤波", "半自动提取"]
        for i in range(1, len(status_text)):
            if self.get_config("Process", status_text[i]) == "1":
                progressBar_name = "self.progressBar_" + str(i) + ".setValue(100)"
                pushButton_name  = "self.pushButton_" + str(i) + ".setEnabled(True)"
                eval(pushButton_name)
                eval(progressBar_name)

    def pushbutton_1_click(self):  # 导入数据
        #global SENSOR
        flag = False
        configDir = self.lineEdit.text()
        self.configfile = configDir + '/config.ini'
        self.set_params()
        status = self.get_config("Process", "导入数据")
        if status == "1":
            rec = QMessageBox.question(self, "提示", "继续将重新生成本步骤文件", QMessageBox.Yes | QMessageBox.No)
            if rec == QMessageBox.No:
                flag = True
            else:
                self.change_status(1)
        if flag == False:
            if os.path.exists(self.workspace + "/data/"):
                shutil.rmtree(self.workspace + "/data/")
            os.makedirs(self.workspace + "/data/")
            raw_paths = QFileDialog.getExistingDirectory(self, "选取影像数据文件夹", "D:/workspace/")
            dir_grd, filetype = QFileDialog.getOpenFileName(self, "选取dem文件(*.grd)", "D:/workspace/","Grd Files (*.grd)")
            shutil.copyfile(dir_grd, self.datafile + "dem.grd")
            # 确定所选数据的类型
            for maindir, subdir, file_name_list in os.walk(raw_paths):
                for f in file_name_list:
                    if '.xml' in f:
                        if 's1' in f:
                            self.data_type = 'Sentinel'
                        if 'TSX' in f or 'TDX' in f:
                            self.data_type = 'TSX'
                    if 'CSK' in f:
                        self.data_type = 'COSMO'
                    if 'ALOS' in f:
                        self.data_type = 'ALOS'
            #SENSOR = self.data_type
            self.set_config('other', 'data_type', self.data_type)
            if self.data_type == 'Sentinel':  # 处理哨兵数据的输入
                # 设置筛选条件
                my1 = child1Window()
                my1.exec_()
                text2 = my1.child1_ui.comboBox_2.currentText()
                text3 = my1.child1_ui.comboBox_3.currentText()
                file_filter = "-"+text2+"-slc-"+text3+"-"
                orbits_path = QFileDialog.getExistingDirectory(self, "选取轨道数据文件夹", "D:/workspace/")  # 起始路径
                dir_xml, filetype1 = QFileDialog.getOpenFileName(self, "选取定标文件(*.xml)", "D:/workspace/","xml Files (*.xml)")
                shutil.copyfile(dir_xml, self.datafile + "/s1a-aux-cal.xml")
                datafile = self.workspace + "\data"
                if not os.path.exists(datafile):
                    os.makedirs(datafile)
                Bool = self.create_sentinel_input(raw_paths, file_filter, orbits_path)
                if Bool == True:
                    flag = True
            if self.data_type == 'TSX':  # 处理TerraSAR数据的输入
                flag = self.create_tsx_input(raw_paths)
            if self.data_type == 'COSMO':  # 处理COSMO数据的输入
                flag = self.create_csk_input(raw_paths)
        if flag == True:
            print("数据导入成功")
            self.set_config("Process", "导入数据", "1")
            self.pushButton_1.setEnabled(True)
            self.progressBar_1.setValue(100)
        else:
            print("数据导入失败")

    def pushbutton_2_click(self):  # 影像配准
        global merge_swaths
        flag = False
        #self.configfile = self.lineEdit.text()
        configDir = self.lineEdit.text()
        self.configfile = configDir + '/config.ini'
        self.set_params()
        status = self.get_config("Process", "影像配准")
        self.data_type = self.get_config("other", "data_type")

        if status == "1":
            rec = QMessageBox.question(self, "提示", "继续将重新生成本步骤文件", QMessageBox.Yes | QMessageBox.No)
            if rec == QMessageBox.No:
                flag = True
            else:
                self.change_status(2)
        if flag == False:
            # 选取主影像
            if os.path.exists(self.datafile + "/input1.txt"):
                os.rename(self.datafile + "/input1.txt", self.input_txt_path)
            if self.data_type == "Sentinel":
                if os.path.exists(self.workspace + "/para_setting"):
                    shutil.rmtree(self.workspace + "/para_setting")
                if os.path.exists(self.workspace + "/xml_temp"):
                    shutil.rmtree(self.workspace + "/xml_temp")
                os.mkdir(self.workspace + "/para_setting")
                os.mkdir(self.workspace + "/xml_temp")

            lines = open(self.input_txt_path).readlines()
            self.image_date = [lines[i].split("#")[0].split("_")[1] for i in range(len(lines))]
            merge_swaths = os.path.exists(self.datafile + "/input3.txt")

            my2 = child2Window()
            my2.child2_ui.comboBox.addItems(sorted(self.image_date))
            my2.child2_ui.comboBox.setCurrentIndex(0)
            my2.exec_()

            master_date_select = my2.child2_ui.comboBox.currentText()
            self.master_image = open(self.input_txt_path).readline().split("#")[0]
            master_date_origin = self.master_image.split("_")[1]
            if master_date_origin == master_date_select:
                pass
            else:
                my2.show()
                self.master_image = self.master_image.replace(master_date_origin, master_date_select)

            #####调用配准脚本
            if merge_swaths == True:
                command_set = []
                txt_file = ["input.txt", "input2.txt", "input3.txt"]
                lines = np.array(sum(
                    [open(self.datafile + "/" + txt_file[index], "r").readlines() for index in range(len(txt_file))],
                    []))
                num = int(len(lines) / 3)
                lines = lines.reshape((3, num)).transpose().reshape((len(lines),))
                swath_index = 1
                for index in range(len(lines)):
                    self.master_image = self.master_image.split("F")[0] + "F" + str(swath_index)
                    command_set.append(
                        "D:/cygwin64/project/cmd/sentinel_align.bat  " + self.workspace + " " + self.master_image + " " +
                        lines[index].replace("\n", ''))
                    swath_index += 1
                    if np.mod((index + 1), 3) == 0:
                        swath_index = 1
            else:
                lines = open(self.input_txt_path, "r").readlines()
                if self.data_type == "Sentinel":
                    bat_shell = "D:/cygwin64/project/cmd/sentinel_align.bat " + self.workspace
                    command = bat_shell + " " + self.master_image + " " + lines[0].replace("\n", "")
                    os.popen(command).read()
                    command_set = list(
                        bat_shell + " " + self.master_image + " " + lines[index].replace("\n", "") for index in
                        range(1, len(lines)))
                else:
                    bat_shell = "D:/cygwin64/project/cmd/align_image.bat " + self.workspace
                    command_set = list(
                        bat_shell + " " + self.master_image + " " + lines[index].split("#")[0] for index in
                        range(1, len(lines)))

            # start = time.time()
            # pool = mp.Pool(processes = 3)
            # pool.map(Ui_Dialog.muliti_work,command_set)
            # pool.close()
            # print(time.time() - start)

            for cmd in command_set:
                os.popen(cmd).read()

            if merge_swaths == True:
                merge_command = "D:/cygwin64/project/cmd/master_merge.bat  " + self.workspace
                os.popen(merge_command).read()
                self.master_image = self.master_image.split("F")[0] + "F123"

            # 获取影像行列
            for line in open(self.datafile + 'master.PRM'):
                if 'num_valid_az' in line:
                    num_valid_az = int(line.split('=')[1])
                if 'num_rng_bins' in line:
                    num_rng_bins = int(line.split('=')[1])

            # 生产master文件的png图像\
            print ("开始生成强度影像")
            slc_file = self.datafile + "master.SLC"
            self.create_master_mli(slc_file, num_valid_az, num_rng_bins)

            # 参数文件设置
            self.set_config("other", "num_valid_az", str(num_valid_az))
            self.set_config("other", "num_rng_bins", str(num_rng_bins))
            self.set_config('other', 'master_image', str(self.master_image))

            if os.path.exists(self.workspace + "/DEM"):
                shutil.rmtree(self.workspace + "/DEM")
            flag = True

        if flag == True:
            self.set_config("Process", "影像配准", "1")
            self.pushButton_2.setEnabled(True)
            self.progressBar_2.setValue(100)
            print("影像配准完成")
        else:
            print("影像配准失败")

    def pushbutton_3_click(self):  # 影像裁剪
        flag = False
        #self.configfile = self.lineEdit.text()
        configDir = self.lineEdit.text()
        self.configfile = configDir + '/config.ini'
        self.set_params()
        status = self.get_config("Process", "影像裁剪")
        self.data_type = self.get_config("other", "data_type")
        merge_swaths = os.path.exists(self.datafile + "/input3.txt")

        if status == "1":
            rec = QMessageBox.question(self, "提示", "继续将重新生成本步骤文件", QMessageBox.Yes | QMessageBox.No)
            if rec == QMessageBox.No:
                flag = True
            else:
                self.change_status(3)
        if flag == False:
            if os.path.exists(self.workspace + "/RSLC"):
                shutil.rmtree(self.workspace + "/RSLC")
            os.mkdir(self.workspace + "/RSLC")
            os.mkdir(self.workspace + "/RSLC/mli/")

            #此处强制限定多视参数为1:1
            self.set_config("other", "range_dec", "1")
            self.set_config("other", "azimuth_dec", "1")

            select_roi = "D:\cygwin64\project\select_roi\select_roi.exe " + self.workspace
            os.system(select_roi)
            region_cut = self.get_config("other", "region_cut")
            if region_cut != '///':
                num_valid_az = int(region_cut.split("/")[1]) - int(region_cut.split("/")[0])
                num_rng_bins = int(region_cut.split("/")[3]) - int(region_cut.split("/")[2])
                self.set_config("other", "num_valid_az", str(num_valid_az))
                self.set_config("other", "num_rng_bins", str(num_rng_bins))

            command_set = []
            command_set1 = []
            lines = open(self.input_txt_path).readlines()
            if merge_swaths == True:
                os.mkdir(self.workspace + "/RSLC/swaths/")
                for index in range(len(lines)):
                    date = lines[index].split("_")[1]
                    os.mkdir(self.workspace + "/RSLC/" + date)
                    command_set1.append("D:/cygwin64/project/cmd/image_merge.bat " + self.workspace + " " + date)
                    for i in range(1, 4):
                        PRM = lines[index].split("F")[0] + "F" + str(i) + "_ALL.PRM"
                        command_set.append("D:/cygwin64/project/cmd/image_cut.bat " + self.workspace + " " + PRM)
            else:
                for index in range(len(lines)):
                    os.mkdir(self.workspace + "/RSLC/" + lines[index].split("_")[1])
                    command_set.append(
                        "D:/cygwin64/project/cmd/image_cut.bat " + self.workspace + " " + lines[index].split("#")[
                            0] + "_ALL.PRM")

            for command in command_set:
                os.popen(command).read()
            for command in command_set1:
                os.popen(command).read()

            #生成topo_ra
            command = "D:/cygwin64/project/cmd/generate_topo.bat " + self.workspace
            os.popen(command).read()

            flag = True

        if flag == True:
            self.set_config("Process", "影像裁剪", "1")
            self.pushButton_3.setEnabled(True)
            self.progressBar_3.setValue(100)
            print("影像裁剪完成")

    def pushbutton_4_click(self):
        print('滤波!')
        my6 = child6Window()
        my6.exec_()  ##设置方向时间向 roi区域

        # 进入参数界面，并传递默认参数
        my7 = child_filter_Window()
        my7.exec_()
        self.progressBar_4.setValue(100)
        self.set_config("Process", "滤波", "1")

    def pushbutton_5_click(self):
        #样本点选取窗口
        my9 = child_sample_Window()
        my9.exec_()

        #self.pushButton_5.setEnabled(True)
        win32api.MessageBox(0, "半自动提取完成！", "进度说明", win32con.MB_OK)
        self.progressBar_5.setValue(100)
        self.set_config("Process", "半自动提取", "1")




class child1Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child1_ui = select_files.Ui_Dialog()
        self.child1_ui.setupUi(self)

class child2Window(QDialog):  # 选取主影像界面
    def __init__(self):
        QDialog.__init__(self)
        self.child2_ui = select_master.Ui_Dialog()
        self.child2_ui.setupUi(self)
        self.child2_ui.buttonBox.accepted.connect(self.show)

    def show(self):
        global workspace, merge_swaths
        self.workspace = workspace
        self.input_txt_path = self.workspace + "/data/input.txt"
        self.configfile = self.workspace + "/config.ini"
        data_type = Ui_Dialog.get_config(self, "other", "data_type")
        lines = open(self.input_txt_path).readlines()
        self.image_date = [lines[i].split("#")[0].split("_")[1] for i in range(len(lines))]
        text = self.child2_ui.comboBox.currentText()
        self.image_date.remove(text)
        self.image_date.insert(0, text)
        input_txt_modify = open(input_txt_path, 'w')
        for line in lines:
            if line.split('_')[1] == text:
                input_txt_modify.write(line)
                lines.remove(line)
                break
        for line in lines:
            input_txt_modify.write(line)
        input_txt_modify.close()
        if data_type == 'Sentinel':
            os.rename(input_txt_path, self.workspace + "/data/input1.txt")
            if merge_swaths == True:
                Ui_Dialog.change_txt(self)
                txt_file = ["input1.txt", "input3.txt", "input2.txt"]
            else:
                txt_file = ["input1.txt"]
            for index in range(len(txt_file)):
                swath_txt_path = self.workspace + "/data/" + txt_file[index]
                os.rename(swath_txt_path, input_txt_path)
                lines = open(self.input_txt_path).readlines()
                command_set = []
                for line in lines:
                    command_set.append("D:/cygwin64/project/cmd/make_slc.bat  " + self.workspace + " " + lines[0].replace("\n","") + " " + line.replace("\n",""))
                os.popen(command_set[0]).read()
                del command_set[0]
                for cmd in command_set:
                    os.popen(cmd).read()
                command = "D:/cygwin64/project/cmd/generate_baseline_sentinel.bat  " + self.workspace
                os.popen(command).read()
                os.rename(input_txt_path, swath_txt_path)
            os.rename(self.workspace + "/data/input1.txt", input_txt_path)
        else:
            command = "D:/cygwin64/project/cmd/generate_baseline.bat  " + self.workspace
            os.popen(command).read()
            command = "D:/cygwin64/project/cmd/preproc_align.bat " + self.workspace
            os.popen(command).read()

        #无需产生基线文件
        # cmd = "D:/cygwin64/project/cmd/select_pairs_sbas.bat  " + self.workspace + " " + str(1000) + " " + str(
        #     1000)  ##确定基线对，并显示
        # os.popen(cmd).read()
        # showps = "D:\cygwin64\Ghostgum\gsview\gsview64.exe " + self.workspace + "\\para_setting\\baseline.ps"
        # os.system(showps)
        self.child2_ui.buttonBox.setEnabled(True)


#滤波预处理窗口
class child6Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child6_ui = filter_pre.Ui_Dialog()
        self.child6_ui.setupUi(self)
        #self.child6_ui.Btn_OK.clicked.connect(self.Btn_OK_click)
        self.child6_ui.Btn_Cancel.clicked.connect(self.close)
        self.child6_ui.Btn_OK.clicked.connect(self.Btn_OK_click)
        global batchfile
        global filepath2ini

        #读取参数并写入界面
        #  读取长、宽（region_cut）
        #  影像路径（filepath2ini+'\RSLC\mli'）
        #  输出路径（filepath2ini）
        configini = filepath2ini + '/config.ini'
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.read(configini)
        master_image=cf.get('other','master_image')
        region_cut = cf.get('other','region_cut')
        region_temp = region_cut.split('/')
        #width = float(region_temp[1])-float(region_temp[0])
        #height = float(region_temp[3])-float(region_temp[2])
        width = float(region_temp[3]) - float(region_temp[2])
        height = float(region_temp[1])-float(region_temp[0])
        master_image_path = ''
        slave_image_path = ''
        #若存在mli路径，则读取
        mli_path = filepath2ini + '\\RSLC\\mli'
        image_path = []
        if(os.path.exists(mli_path)):

            #获取mli路径，若和主影像不匹配，则为从影像
            for root, dirs, files in os.walk(mli_path):
                if len(files) > 2:
                    # 说明文件数超过了两个，此处留白，为以后扩展批量处理做准备
                    print('warning! The size of files is larger than 2, program will skip this step.');
                    continue

                for file in files:
                    fileInfo = os.path.splitext(file)  #[20161114, .mli]
                    image_path.append(root+'/'+file)

        #设置界面上的默认参数
        self.child6_ui.line_width.setText(str(width))
        self.child6_ui.line_height.setText(str(height))
        if (len(image_path)>1):
            self.child6_ui.line_path_master.setText(image_path[0])
            self.child6_ui.line_path_slave.setText(image_path[1])
        self.child6_ui.line_path_output.setText(filepath2ini+'\\')

        print('configfile=', configini)

    def Btn_OK_click(self):
        configini_config = filepath2ini + '/config.ini'
        cf_config = configparser.ConfigParser(allow_no_value=True)
        cf_config.read(configini_config)
        SENSOR = cf_config.get('other', 'data_type')

        # 读入轨道方向数据
        for line in open(filepath2ini + '/data/master.PRM'):
            if 'orbdir' in line:
                #orbdir = line.split('=')[1]
                orbdir = line[9:10]   #'A'或'D'

        print('Btn_OK_click')
        self.child6_ui.Btn_OK.setEnabled(False)
        #获取UI界面的参数
        cf = configparser.ConfigParser()
        configini = filepath2ini + '/data/batch.ini'
        cf.read(configini)
        width = self.child6_ui.line_width.text()
        height = self.child6_ui.line_height.text()
        master_image_path = self.child6_ui.line_path_master.text()
        slave_image_path = self.child6_ui.line_path_slave.text()
        output_path = self.child6_ui.line_path_output.text()

        print('width=', width)
        print('height=', height)
        print('master_image_path=', master_image_path)
        print('slave_image_path=', slave_image_path)
        print('output_path=', output_path)

        # 创建filter.ini参数文件
        config = configparser.ConfigParser()
        out_cf_name = filepath2ini + '/filter.ini'
        config.read(out_cf_name)
        config["PARAMETER-PRE"] = {'Width': width,
                               'Height': height,
                               'Master_image_path': master_image_path,
                               'Slave_image_path': slave_image_path,
                               'Output_path': output_path,
                                'Sensor': SENSOR,
                                'orbdir': orbdir}
        out_cf_name = filepath2ini+'/filter.ini'
        with open(out_cf_name, 'w') as configfile:
            config.write(configfile)

        #调用cmd处理
        #cmd = "D:/cygwin64/project/rc/rs_stage1.exe  " + out_cf_name  #cmd执行滤波预处理
        cmd = "D:/cygwin64/project/cmd/for_rc_pre_filter.bat  " + out_cf_name  #cmd执行滤波预处理
        #os.system(cmd)
        tmp = os.popen(cmd).readlines()
        print(tmp)
        #self.child6_ui.Btn_OK.setEnabled(True)

        win32api.MessageBox(0, "滤波预处理完成！", "进度说明", win32con.MB_OK)
        self.close()


#NL滤波窗口
class child7Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child7_ui = filter_NL.Ui_Dialog()
        self.child7_ui.setupUi(self)

        self.child7_ui.pushButton_2.clicked.connect(self.close)  #Cancle
        self.child7_ui.pushButton.clicked.connect(self.Btn_OK_click)  #OK

        global filepath2ini

        #读取参数并写入界面
        #  搜索窗口半径：1
        #  邻域窗口半径：12
        #  高斯函数平滑参数：0.7
        #  输出路径（filepath2ini）
        configini = filepath2ini + '/filter.ini'
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.read(configini)
        width = float(cf.get('PARAMETER-PRE','width'))
        height = float(cf.get('PARAMETER-PRE','height'))

        stretch_path = filepath2ini+'\\stretch'
        image_name_list = ''
        #设置stretch文件的默认路径
        if(os.path.exists(stretch_path)):
            #遍历stretch下的文件，获取影像文件的信息
            for root, dirs, files in os.walk(stretch_path):
                for file in files:
                    fileInfo = os.path.splitext(file)  #[20161114, .tif]
                    if fileInfo[1] == '.tif':  #找到影像文件
                        image_name_list = image_name_list+os.path.join(root, file)+'\n'
        else:
            print("找不到指定的影像文件夹！")

        #设置滤波默认参数
        search_radius = '10'
        adjacent_radius = '4'
        gaussian_para = '20'
        if cf.has_section('PARAMETER-FILTER'):
            filter_paramter = cf.options('PARAMETER-FILTER')
            try:
                search_radius = cf.get('PARAMETER-FILTER', 'search_radius')
                adjacent_radius = cf.get('PARAMETER-FILTER', 'adjacent_radius')
                gaussian_para = cf.get('PARAMETER-FILTER', 'gaussian_para')
            except Exception:
                print("滤波参数缺失，请检查filter.ini文件")
            finally:
                print("完成滤波参数读取")

        #设置界面上的默认参数
        self.child7_ui.text_image_stretch.setText(image_name_list)
        self.child7_ui.line_search_radius.setText(search_radius)
        self.child7_ui.line_adjacent_radius.setText(adjacent_radius)
        self.child7_ui.line_gaussian_para.setText(gaussian_para)
        self.child7_ui.line_path_output.setText(filepath2ini + '\\')
        print('configfile=', configini)

    def Btn_OK_click(self):
        print('Btn_OK_click')
        self.child7_ui.pushButton.setEnabled(False)

        # 获取UI界面的参数
        #  搜索窗口半径：1
        #  邻域窗口半径：1
        #  gamma：0.7
        #  输出路径（filepath2ini）
        image_name_list = self.child7_ui.text_image_stretch.toPlainText()
        image_name_list_new = image_name_list.replace("\n", " ")

        search_radius = self.child7_ui.line_search_radius.text()
        adjacent_radius = self.child7_ui.line_adjacent_radius.text()
        gaussian_para = self.child7_ui.line_gaussian_para.text()
        output_path = self.child7_ui.line_path_output.text()

        # 扩展filter.ini参数文件
        out_cf_name = filepath2ini + '/filter.ini'
        config = configparser.ConfigParser()
        config.read(out_cf_name)

        if config.has_section("PARAMETER-FILTER") == False:
            # config.remove_section("PARAMETER-FILTER")
            config.add_section("PARAMETER-FILTER")
        config.set("PARAMETER-FILTER", 'image_name_list', image_name_list_new)
        config.set("PARAMETER-FILTER", 'search_radius', search_radius)
        config.set("PARAMETER-FILTER", 'adjacent_radius', adjacent_radius)
        config.set("PARAMETER-FILTER", 'gaussian_para', gaussian_para)
        config.set("PARAMETER-FILTER", 'output_path', output_path)

        config.write(open(out_cf_name, "w"))  # 写入batch.ini文件
        # 调用cmd处理
        cd_command = "cd D:/cygwin64/project/rc/ & d:"  # cd到目标文件夹
        cmd = cd_command + " & " + "D:/cygwin64/project/rc/rs_stage2.exe  " + out_cf_name  # cmd执行滤波预处理
        os.system('cd D:/cygwin64/project/rc/')
        tmp = os.popen(cmd).read()
        # cmd = "D:/cygwin64/project/cmd/for_rc_pre_filter.bat  " + out_cf_name  # cmd执行滤波预处理
        # tmp = os.popen(cmd).readlines()

        # 读入主影像数据
        #master = '20160124'
        configini = filepath2ini + '/config.ini'
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.read(configini)
        master_image_name = cf.get('other', 'master_image')
        master_image_name_temp = master_image_name.split('_')
        master = master_image_name_temp[1]  #'20160124'

        #地理编码
        geoCodeTiff_new(filepath2ini, master)

        '''
        composed_outPath = filepath2ini + "/composed/"
        in_filename = composed_outPath + "composed.tif"
        out_filename = composed_outPath + "composed_geo.tif"
        trans_dat = filepath2ini + "/RSLC/trans.dat"

        coord = getCoordinate(trans_dat)
        geoCodeTiff(in_filename, out_filename, coord)
        '''

        win32api.MessageBox(0, "滤波处理完成！", "进度说明", win32con.MB_OK)
        self.child7_ui.pushButton.setEnabled(True)
        self.close()


#Lee滤波
class child8Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child8_ui = filter_Lee.Ui_Dialog()
        self.child8_ui.setupUi(self)

        self.child8_ui.Button_cancle .clicked.connect(self.close)  #Cancle
        self.child8_ui.Button_OK.clicked.connect(self.Btn_OK_click)  #OK
        global filepath2ini

        stretch_path = filepath2ini+'\\stretch'
        stretch_name_list = ''

        #读取参数并写入界面
        #  噪声影像文件（filepath2ini+'\RSLC\rat'）
        #  窗口大小：12
        #  输出路径（filepath2ini）
        configini = filepath2ini + '/filter.ini'
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.read(configini)

        image_name_list = ''

        #设置stretch文件的默认路径
        if(os.path.exists(stretch_path)):
            #遍历stretch下的文件，并区分影像文件和噪声文件
            for root, dirs, files in os.walk(stretch_path):
                for file in files:
                   if os.path.exists(root+"/"+file[:-4]+'_match.tif'):   #跳过没有直方图匹配的数据
                        continue
                   elif file.split('.')[-1] == 'tif':
                       image_name_list = image_name_list+os.path.join(root, file)+'\n'
        else:
            print("找不到指定的stretch文件夹！")

        # 设置滤波默认参数
        filter_window = '12'

        # 设置界面上的默认参数
        self.child8_ui.text_image.setPlainText(image_name_list)
        self.child8_ui.line_filter_window.setText(filter_window)
        self.child8_ui.line_path_output.setText(filepath2ini + '\\')
        print('configfile=', configini)


    def Btn_OK_click(self):
        print('Btn_OK_click')
        self.child8_ui.Button_OK.setEnabled(False)

        filter_window = self.child8_ui.line_filter_window

        #读取参数并写入界面
        #  噪声影像文件（filepath2ini+'\RSLC\rat'）
        #  窗口大小：12
        #  输出路径（filepath2ini）

        image_name_list = self.child8_ui.text_image.toPlainText()
        image_name_list_new = image_name_list.replace("\n", " ")

        filter_window = self.child8_ui.line_filter_window.text()
        output_path = self.child8_ui.line_path_output.text()

        # 扩展filter.ini参数文件
        out_cf_name = filepath2ini + '/filter.ini'
        config = configparser.ConfigParser()
        config.read(out_cf_name)

        if config.has_section("PARAMETER-FILTER") == False:
            # config.remove_section("PARAMETER-FILTER")
            config.add_section("PARAMETER-FILTER")
        config.set("PARAMETER-FILTER", 'image_name_list', image_name_list_new)
        config.set("PARAMETER-FILTER", 'filter_window', filter_window)
        config.set("PARAMETER-FILTER", 'output_path', output_path)
        config.write(open(out_cf_name, "w"))  # 写入batch.ini文件

        # 调用Lee滤波函数处理
        # 定义文件路径
        pgmDir_list = []
        datDir_list = []
        Height = 0
        Width = 0
        image_name_list_new_2 = image_name_list.split('\n')
        output_path = output_path + "filter\\"
        for imagePath in image_name_list_new_2:
            if imagePath == '':
                continue
            img = cv2.imread(imagePath, cv2.IMREAD_GRAYSCALE)
            Height, Width = img.shape

            filter_window_float = float(filter_window)
            img_filter = self.lee_filter(img, filter_window_float)

            out_fileName = os.path.basename(imagePath)
            if(out_fileName[-9:] == 'match.tif'):  #判断是否有_match后缀
                out_fileName = out_fileName[:-10]

            if not os.path.exists(output_path):
                os.makedirs(output_path)

            outPath_temp = output_path + out_fileName.split('.')[0] + '/'
            if not os.path.exists(outPath_temp):
                os.mkdir(outPath_temp)
            img_filter = img_filter.astype(np.float32)
            img_filter.tofile(outPath_temp + out_fileName.split('.')[0] + '_Lee.dat')

            datDir_list.append(outPath_temp + out_fileName.split('.')[0] + '_Lee.dat')

            #***************生成pgm文件*********************************************
            im  = Image.fromarray(img_filter)
            im.convert('L').save(outPath_temp + out_fileName.split('.')[0] + '_final.pgm')  # 如果是rgb图，要转为单通道的灰度图；如果是灰度图，那么去掉convert，保持灰度图
            pgmDir_list.append(outPath_temp + out_fileName.split('.')[0] + '_final.pgm')

        # *************************生成彩色波段组合文件********************************
        im1 = np.fromfile(datDir_list[0],'f')  # 读取文件
        im1 = im1.reshape(Height, Width)
        im2 = np.fromfile(datDir_list[1],'f')
        im2 = im2.reshape(Height, Width)

        # 波段合成
        #synthesis = np.zeros((Height, Width, 3));

        # % 波段2 % 线性拉伸
        # band1_stretch = linear_stretch(pgm_image1(:,:, 1));
        # band2_stretch = linear_stretch(pgm_imag2_match(:,:, 1));
        # band3_stretch = linear_stretch(pgm_imag2_match(:,:, 1));

        # % 按照顺序存储
        #synthesis[:,:, 0] = np.asarray(im1);
        #synthesis[:,:, 1] = np.asarray(im2);
        #synthesis[:,:, 2] = np.asarray(im2);

        r = np.asarray(im1);
        g = np.asarray(im2);
        b = np.asarray(im2);

        bgr = cv2.merge([b, g, r])
        bgr_stretch = self.TwoPercentLinear(bgr)

        composed_outPath = filepath2ini+"/composed/"
        if not os.path.exists(composed_outPath):
            os.mkdir(composed_outPath)

        cv2.imwrite(composed_outPath + "composed.tif", bgr_stretch)  # 保存图片

        #bug出在这，明天找找如何把多维矩阵组合tiff文件就可以了
        #composed = Image.fromarray(synthesis)
        #composed.save("D:\\tt.tif")

        #在此加入地理编码的代码
        # 读入主影像数据
        # master = '20160124'
        configini = filepath2ini + '/config.ini'
        cf = configparser.ConfigParser(allow_no_value=True)
        cf.read(configini)
        master_image_name = cf.get('other', 'master_image')
        master_image_name_temp = master_image_name.split('_')
        master = master_image_name_temp[1]  # '20160124'
        #master = '20160124'
        geoCodeTiff_new(filepath2ini, master)

        '''
        in_filename = composed_outPath + "composed.tif"
        out_filename = composed_outPath + "composed_geo.tif"
        trans_dat = filepath2ini+"/RSLC/trans.dat"
        coord = getCoordinate(trans_dat)
        geoCodeTiff(in_filename, out_filename, coord)
        '''

        win32api.MessageBox(0, "滤波处理完成！", "进度说明", win32con.MB_OK)
        self.child8_ui.Button_OK.setEnabled(True)
        self.close()


    def lee_filter(self, img, size):
        from scipy.ndimage.filters import uniform_filter
        from scipy.ndimage.measurements import variance


        img_mean = uniform_filter(img, (size, size))
        img_sqr_mean = uniform_filter(img ** 2, (size, size))
        img_variance = img_sqr_mean - img_mean ** 2

        overall_variance = variance(img)

        img_weights = img_variance / (img_variance + overall_variance)
        img_output = img_mean + img_weights * (img - img_mean)
        return img_output

    def TwoPercentLinear(self, image, max_out=255, min_out=0):
        b, g, r = cv2.split(image)  # 分开三个波段

        def gray_process(gray, maxout=max_out, minout=min_out):
            high_value = np.percentile(gray, 98)  # 取得98%直方图处对应灰度
            low_value = np.percentile(gray, 2)  # 同理
            truncated_gray = np.clip(gray, a_min=low_value, a_max=high_value)
            processed_gray = ((truncated_gray - low_value) / (high_value - low_value)) * (maxout - minout)  # 线性拉伸嘛
            return processed_gray

        r_p = gray_process(r)
        g_p = gray_process(g)
        b_p = gray_process(b)
        result = cv2.merge((b_p, g_p, r_p))  # 合并处理后的三个波段
        return np.uint8(result)

#滤波选择窗口
class child_filter_Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child_filter_ui = filter_selection.Ui_Dialog()
        self.child_filter_ui.setupUi(self)

        self.child_filter_ui.Button_cancle .clicked.connect(self.close)  #Cancle
        self.child_filter_ui.Button_OK.clicked.connect(self.Btn_OK_click)  #OK

        global filepath2ini

    def Btn_OK_click(self):
        print('Btn_OK_click')
        self.child_filter_ui.Button_OK.setEnabled(False)

        if self.child_filter_ui.radio_filter_Nl.isChecked():
            print("NL filter")
            my7 = child7Window()
            my7.exec_()
            self.close()
        elif self.child_filter_ui.radio_filter_Lee.isChecked():
            print("Lee filter")
            my8 = child8Window()
            my8.exec_()
            self.close()
        elif self.child_filter_ui.radio_filter_Lee_E.isChecked():
            print("Enhanced Lee filter")
            win32api.MessageBox(0, "该功能还在完善中，敬请期待", "说明", win32con.MB_OK)
            self.child8_ui.pushButton.setEnabled(True)

        self.child_filter_ui.Button_OK.setEnabled(True)
        self.close()

#样本选择窗口 sample_selection
class child_sample_Window(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.child_sample_ui = sample_selection.Ui_Dialog()
        self.child_sample_ui.setupUi(self)

        self.child_sample_ui.Button_cancle .clicked.connect(self.close)  #Cancle
        self.child_sample_ui.Button_OK.clicked.connect(self.Btn_OK_click)  #OK

        #self.child_sample_ui.radio_shp_GF.setEnabled(False)
        #self.child_sample_ui.radio_shp_manual.setEnabled(False)


        global filepath2ini


    def Btn_OK_click(self):
        print('Btn_OK_click')
        self.child_sample_ui.Button_OK.setEnabled(False)

        if self.child_sample_ui.radio_shp_SAR.isChecked():
            print("基于SAR平台选取样本")
            #设置shp_flag
            out_cf_name = filepath2ini + '/filter.ini'
            config = configparser.ConfigParser()
            config.read(out_cf_name)
            if config.has_section("PARAMETER-PRE") == False:
                win32api.MessageBox(0, "config文件没有PRE目录，请检查", "错误", win32con.MB_OK)
                exit(0)
            config.set("PARAMETER-PRE", 'shp_flag', '0')
            config.write(open(out_cf_name, "w"))  # 写入batch.ini文件

        elif self.child_sample_ui.radio_shp_GF.isChecked():
            print("基于GF平台选取样本")

            # 设置shp_flag
            out_cf_name = filepath2ini + '/filter.ini'
            config = configparser.ConfigParser()
            config.read(out_cf_name)
            if config.has_section("PARAMETER-PRE") == False:
                win32api.MessageBox(0, "config文件没有PRE目录，请检查", "错误", win32con.MB_OK)
                exit(0)
            config.set("PARAMETER-PRE", 'shp_flag', '1')
            config.write(open(out_cf_name, "w"))  # 写入batch.ini文件

            #崔师姐处理后需要提供shp文件的路径
            win32api.MessageBox(0, "以预留接口，等待和崔师姐对接", "说明", win32con.MB_OK)

        elif self.child_sample_ui.radio_shp_manual.isChecked():
            print("用户输入样本")
            #获取shp文件路径
            shp_manual_path = self.child_sample_ui.lineEdit_shp.text()

            #设置shp_flag和输出文件路径
            out_cf_name = filepath2ini + '/filter.ini'
            config = configparser.ConfigParser()
            config.read(out_cf_name)
            if config.has_section("PARAMETER-PRE") == False:
                win32api.MessageBox(0, "config文件没有PRE目录，请检查", "错误", win32con.MB_OK)
                exit(0)
            config.set("PARAMETER-PRE", 'shp_flag', '2')
            config.set("PARAMETER-PRE", 'shp_manual', shp_manual_path)
            config.write(open(out_cf_name, "w"))  # 写入batch.ini文件

        self.classification()

        self.child_sample_ui.Button_OK.setEnabled(True)
        self.close()

    def classification(self):
        # 半自动提取
        print('半自动提取!')
        #self.pushButton_5.setEnabled(False)
        # 直接调用matlab界面
        out_cf_name = filepath2ini + '/filter.ini'
        # cd_command = "cd D:/cygwin64/project/rc/ & d:"
        # cmd = cd_command+" & "+"D:/cygwin64/project/rc/rs_stage3.exe  " + out_cf_name  # cmd执行滤波预处理
        cmd = "D:/cygwin64/project/cmd/for_rc_after_filter.bat  " + out_cf_name  # cmd执行滤波预处理
        # tmp = os.popen(cmd).read()

        # 执行cmd并等待其运行完毕
        ex = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        out, err = ex.communicate()
        status = ex.wait()
        print("cmd in:", cmd)
        # print("cmd out: ", out.decode())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = QDialog()
    ui = Ui_Dialog()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
