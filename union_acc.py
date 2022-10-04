import geopandas as gpd
import numpy as np

shp1 = gpd.read_file(r"D:\shp\change_sample.shp")
shp2 = gpd.read_file(r"D:\shp\label.shp")
#shp1 = gpd.read_file("acc/int_KL_chg.shp")
#shp2 = gpd.read_file("acc/int_all_class.shp")
shp1['ID'] = np.arange(1, shp1.shape[0]+1)
shp2['ID'] = np.arange(1, shp2.shape[0]+1)
combined = gpd.overlay(shp1, shp2, how="union")

shparea = combined.area.values * 100
thr = 0.001
inxdel = np.where(shparea < thr)[0]

FID1 = np.array(combined.get('ID_1')).astype('int')
FID2 = np.array(combined.get('ID_2')).astype('int')
comb_FID = np.array([FID1, FID2]).transpose()
comb_FID_del = np.array([comb_FID[i] for i in range(len(comb_FID)) if i not in inxdel])
shparea_del = np.array([shparea[i] for i in range(len(comb_FID)) if i not in inxdel])
prd, ref = comb_FID_del[:,0], comb_FID_del[:,1]
TP, FP, FN, TN = 0, 0, 0, 0
TP_a, FP_a, FN_a, TN_a = 0, 0, 0, 0
for i in range(len(prd)):
    if prd[i] > 0 and ref[i] > 0:
        TP += 1
        TP_a += shparea_del[i]
    elif prd[i] <= 0 and ref[i] <= 0:
        TN += 1
        TN_a += shparea_del[i]
    elif prd[i] <= 0 and ref[i] > 0:
        FN += 1
        FN_a += shparea_del[i]
    elif prd[i] > 0 and ref[i] <= 0:
        FP += 1
        FP_a += shparea_del[i]
precision = TP / (TP+FP)
recall = TP / (TP+FN)
FalseAlarm = 1 - precision
MissingAlarm = 1 - recall
Fscore = 2*precision*recall/(precision+recall)
precision, recall

precision_a = TP_a / (TP_a+FP_a)
recall_a = TP_a / (TP_a+FN_a)
FalseAlarm_a = 1 - precision_a
MissingAlarm_a = 1 - recall_a
Fscore_a = 2*precision_a*recall_a/(precision_a+recall_a)
precision_a, recall_a

