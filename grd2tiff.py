'''
将grd文件转为tiff格式文件
xuhang

20210622
'''

import numpy as np
from osgeo import gdal, osr, gdal_array
import sys
import os


#######Load a GMT grd file
def load_grd(fname, var='z', shape=None):
    '''Load a GMT grd file.

    Args:

        * fname         Name of the file

    Kwargs:

        * var           Variable name to be loaded, not currently used


    Returns:

        * data          2D array of the data'''

    try:
        import gdal
        from gdalconst import GA_ReadOnly
    except ImportError:
        raise Exception('GDAL python bindings must be installed for GMTSAR support')

    gdal.UseExceptions()
    dataset = gdal.Open(fname, GA_ReadOnly)
    #try:
    #    dataset = gdal.Open(fname, GA_ReadOnly)
    #except (RuntimeError):
    #    print('Error: GDAL library failed to open GMT file: ' + fname)
    #    #print(e)
    #    sys.exit(1)

    #print 'Size is ',dataset.RasterXSize,'x',dataset.RasterYSize, 'x',dataset.RasterCount

    #here we should get the band name instead of just assuming band #1
    band = dataset.GetRasterBand(1)

    #read the data
    data=band.ReadAsArray()

    #close the dataset
    dataset = None

    return data

def getCoordinate(trans_dat):
    trans_size = os.path.getsize(trans_dat)
    trans_width = 5
    trans_height = trans_size/(5*8)   #5为宽度，8为字节数（double）
    trans_dat_data = np.fromfile(trans_dat,'d')
    trans_dat_data = trans_dat_data.reshape(int(trans_height), int(trans_width))
    LonMin = trans_dat_data[:, 3].min()
    LonMax = trans_dat_data[:, 3].max()
    LatMin = trans_dat_data[:, 4].min()
    LatMax = trans_dat_data[:, 4].max()

    return [LonMin, LonMax, LatMin, LatMax]

def grd2tiff(in_filename, out_filename,coord):

    '''
    if fileName == 'realfilt.grd':
        cmd = convertPath + ' -ZTLf ' + fileDir + '/realfilt.grd > ' + fileDir + '/realfilt.dat'
        os.popen(cmd).read()
    生成裸格式
    '''

    src_ds = gdal.Open(in_filename)
    if src_ds is None:
        print("open failed")
        sys.exit()

    width = src_ds.RasterXSize
    height = src_ds.RasterYSize
    print(str(src_ds.RasterXSize))   #宽度 1090
    print(str(src_ds.RasterYSize))   #高度 1530


    #data_Array = np.fromfile('D:\\tt.dat','f')
    data_Array = load_grd(in_filename, shape=(height, width))
    data_Array = data_Array.reshape(height,width)
    #data_Array = np.flipud(data_Array)

    [LonMin, LonMax, LatMin, LatMax] = coord
    #LonMin,LatMax,LonMax,LatMin = [Lon.min(),Lat.max(),Lon.max(),Lat.min()]
    #LonMin,LatMax,LonMax,LatMin = [119.676388889,40.17361111111176,119.827777778,39.961111111111755]
    N_Lon = width
    N_Lat = height

    Lon_Res = (LonMax - LonMin) /(float(N_Lon)-1)
    Lat_Res = (LatMax - LatMin) / (float(N_Lat)-1)
    spei_ds = gdal.GetDriverByName('Gtiff').Create(out_filename,N_Lon,N_Lat,1,gdal.GDT_Float32)

     # 设置影像的显示范围
    geotransform = (LonMin,Lon_Res, 0, LatMin, 0, Lat_Res)
    spei_ds.SetGeoTransform(geotransform)

    # 地理坐标系统信息
    srs = osr.SpatialReference() #获取地理坐标系统信息，用于选取需要的地理坐标系统
    print(type(srs))
    print(srs)
    srs.ImportFromEPSG(4326) # 定义输出的坐标系为"WGS 84"，AUTHORITY["EPSG","4326"]
    spei_ds.SetProjection(srs.ExportToWkt()) # 给新建图层赋予投影信息

     # 数据写出
    spei_ds.GetRasterBand(1).WriteArray(data_Array) # 将数据写入内存
    spei_ds.FlushCache() # 将数据写入硬盘
    spei_ds = None # 关闭spei_ds指针

if __name__ == '__main__':
    in_filename = r'D:\phasefilt_mask_ll.grd'
    out_filename = r'D:\phasefilt_mask_ll.tif'
    trans_dat = r'D:\trans.dat'
    coord = getCoordinate(trans_dat)

    grd2tiff(in_filename, out_filename, coord)