# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Description:
    merge the polygons in the same shapefile

@author:Hang Xu
@file:merge_shp.py
@time:2022/01/08
"""


import sys
import os
import geopandas as gpd


def main():

    shp_path = sys.argv[1]
    # shp_path = r'D:\RC_vec.shp'
    shp_path_out = shp_path
    dirname = os.path.dirname(shp_path)
    basename = os.path.basename(shp_path)
    shp_path_out_prj = dirname + '\\proj_' + basename

    shp_input = gpd.read_file(shp_path)
    geoms = shp_input['geometry'].tolist()

    print("merge the polygons in the same shapefile")

    # 将重叠的数据合并为一个
    skip_index = []
    geoms_new = []
    count_num = 0

    for i in range(len(geoms) - 1):
        if i in skip_index:
            continue
        data_i = geoms[i]

        for j in range(i + 1, len(geoms)):
            if j in skip_index:
                continue
            data_j = geoms[j]
            if data_i.intersects(data_j):
                data_i = data_i.union(data_j)
                skip_index.append(j)  # 已经合并的矩形不再合并
        count_num += 1
        geoms_new.append(data_i)

    intersection_iter = gpd.GeoDataFrame(gpd.GeoSeries(geoms_new), columns=['geometry'], crs=shp_input.crs)
    intersection_iter.to_file(shp_path_out)

    # 投影（测试中，尚未完善）
    shp_input_proj = intersection_iter.to_crs("EPSG:3395")  # 墨卡托投影
    shp_input_proj.to_file(shp_path_out_prj)


if __name__ == '__main__':

    main()
