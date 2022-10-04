#coding=utf-8
'''
    将shp文件转为SAR变化监测平台可读取的mask文件
    xuhang
    2021.11.10
'''
import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from shapely.geometry import mapping
import configparser
import sys
import hdf5storage


# Extract raster values and connectivity from shapefile
def StatExtract(img, n, class_number):

    pgeoms = [mapping(trngeoms[n])]
    #out_image, _ = mask(img, pgeoms, crop=True, filled=False) # out_image is a minimum enclosing rectangle of a polygon, but the values outside the polygon are 0

    #应该是这段代码出了问题，明天好好调整，应该就可以了
    out_image, _ = mask(img, pgeoms, crop=False, filled=True)  # out_image is a minimum enclosing rectangle of a polygon, but the values outside the polygon are 0
    out_image = np.array(out_image[0,:,:])

    # 显示图片
    #new_im = Image.fromarray(out_image)
    # 显示图片
    #new_im.show()

    #将像素值转为对应的类号
    out_image = np.array(out_image, dtype=bool)  #转为bool值
    #out_image = out_image.astype('int')
    #imgvalue = out_image*class_number
    imgvalue = out_image.astype('int')

    return imgvalue

# # ------------------------------ Main function begins-------------------------------------------
if __name__=="__main__":

    '''
    path = r"D:\project\change_detection\demo_nanjing\TerraSAR_proj_2"
    imgpath = path + r"\composed\composed_geo.tif"
    trnpath = path + r"\extraction\label.shp"
    outpath = path + r"\extraction\mask_out.mat"
    
    D:/gf3/To/project/filter.ini
    '''
    #'''
    configini = sys.argv[1]
    cf = configparser.ConfigParser(allow_no_value=True)
    cf.read(configini)
    base_path = cf.get('PARAMETER-PRE', 'output_path')
    imgpath = base_path + r"\composed\composed_geo.tif"
    shp_flag = int(cf.get('PARAMETER-PRE', 'shp_flag'))
    if shp_flag == 0:
        print("No need to extract shp file, please check your config data")
    elif shp_flag == 1:
        trnpath = cf.get('PARAMETER-PRE', 'shp_GF')
        outmask_path = base_path +  '\extraction\mask_GF.mat'
    elif shp_flag == 2:
        trnpath = cf.get('PARAMETER-PRE', 'shp_manual')
        outmask_path = base_path +  '\extraction\mask_manual.mat'
    #'''

    trnpath = cf.get('PARAMETER-PRE', 'shp_manual')
    #outmask_path = base_path + '\extraction\mask_manual.mat'
    outmask_path = base_path + 'extraction\mask_manual.mat'
    #fd = "Class_name"
    fd = "class"
    src = rasterio.open(imgpath)    # Read raster image
    #raster = src.read()
    trnshape = gpd.read_file(trnpath)
    trngeoms = trnshape.geometry.values

    #clsstr = list(set(trnshape.get(fd)))
    #clsstr.sort()  # Order class code
    #trn_cls = [clsstr.index(trnshape.get(fd)[i]) for i in range(trngeoms.size)]

    hsize_src = src.shape[0]
    wsize_src = src.shape[1]
    trn_v = np.zeros((hsize_src,wsize_src,trngeoms.size)) #构建label_mask矩阵
    #trn_v = []
    for n in range(trngeoms.size):
        class_number = trnshape.get(fd)[n]
        #trn_v.append(StatExtract(src, n, class_number))
        imgvalue = StatExtract(src, n, class_number)
        #trn_v.append(imgvalue)
        #trn_v[:,:,n] = imgvalue
        trn_v[:, :, class_number-1] = imgvalue  #按照类别来赋值
        #if n % 100 == 0:
        print("Constructing " + str(n+1) + " / " + str(trngeoms.size))

    # 输出trn_v为mat格式，供matlab读取
    ##sio.savemat(outmask_path, {'mask': trn_v},do_compression=True)
    hdf5storage.savemat(outmask_path, {'mask': trn_v}, appendmat=False,do_compression=False, format='7.3')
    print("end")
