# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 14:29:09 2024

@author: WatabeT
"""
import os
import glob
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rc('pdf', fonttype=42)
matplotlib.rc('font',size = 8)
plt.rcParams["font.family"] = "Arial"
import math
from read_flimagecsv import arrange_for_multipos3, csv_to_df, detect_uncaging, value_normalize, everymin_normalize

save_True = True


one_of_filepath = r"G:\ImagingData\Tetsuya\20250506\onHarp\Analysis\copy\E4_roomair_LTP1_23um_align_TimeCourse.csv"
one_of_filepath = r"G:\ImagingData\Tetsuya\20250506\onHarp\Analysis\auto_ltp_copy\E4_roomair_lowmag_1__highmag_1_align_TimeCourse.csv"
# one_of_filepath = r"G:\ImagingData\Tetsuya\20250331\B6_cut0319_FlxGC6sTom_0322\highmag_RFP50ms100p\tpem2\Analysis\copy\lowmag2__highmag_1_concat_TimeCourse.csv"
one_of_filepath = r"G:\ImagingData\Tetsuya\20250508\Analysis\copy\LTP2_15um_align_TimeCourse.csv"


csvlist = glob.glob(one_of_filepath[:one_of_filepath.rfind("\\")]+"\\*_TimeCourse.csv")
one_of_filepath = csvlist[0]
allcombined_df_savepath= one_of_filepath[:-4] + "_combined.csv"
summarized_df_savepath= one_of_filepath[:-4] + "_combined_summarized.csv"

allcombined_df=pd.DataFrame()

for csvpath in csvlist:
    print(csvpath)
    resultdf=csv_to_df(csvpath,
                       ch_list=[2])
    
    if len(resultdf)<2:
        print("len = ",len(resultdf),"   less than 2")
        continue
    
    if len(resultdf)<36:
        print("len = ",len(resultdf),"   less than 38")
        continue
    
    df = detect_uncaging(resultdf) 
    
    # Step 1: Identify rows before the 0 -> 1 transition
    df['label_trigger'] = (df['during_uncaging'] == 0) & (df['during_uncaging'].shift(-1) == 1)
    
    # Step 2: Assign group labels
    df['group_label'] = df['label_trigger'].cumsum()
    
    # Drop the helper column (optional)
    df = df.drop(columns=['label_trigger'])
    for NthFrame in df["NthFrame"].unique():
        NthFrame_df = df[df["NthFrame"] == NthFrame]
        df.loc[NthFrame_df.index, "group"] = NthFrame_df['group_label'].max()


    allcombined_df=pd.concat([allcombined_df,df],
                             ignore_index=True)

allcombined_df.to_csv(allcombined_df_savepath)


spine_vol_list = []
time_aligned_df = pd.DataFrame()
summarized_df = pd.DataFrame()
unique_spine_label = 0
for each_filepath in allcombined_df["FilePath"].unique():
    each_file_df = allcombined_df[allcombined_df["FilePath"] == each_filepath]

    # break

    # if each_filepath == r"Z:\Users\WatabeT\20250420\Analysis\copy\0326FlxGC6stdTom_n3_d1_align_TimeCourse.csv":
    #     break
    # else:    continue


    # for each_group in each_file_df["group"].unique()[1:]:
    # each_group = 1
    # for each_group in each_file_df["group"].unique()[1:]:
    for each_group in each_file_df["group"].unique():
        
        each_group_df = each_file_df[(each_file_df["group"] == each_group)&
                                     (each_file_df["ROInum"] == each_group)]
        if len(each_group_df) < 3:
            continue
        
        each_group_df["NormFrame"] = each_group_df["NthFrame"] - each_group_df["NthFrame"].min()
        each_group_df["Norm_time_min"] = each_group_df["Time_min"] - each_group_df["Time_min"].min()
        
        intensity_numerator = each_group_df[each_group_df["NormFrame"] == 0 ]["sumIntensity-ROI"].values[0]
        each_group_df["Norm_intensity"] = each_group_df["sumIntensity-ROI"] / intensity_numerator
        each_group_df["unique_spine_label"] = str(unique_spine_label)
        
        each_group_df = arrange_for_multipos3(each_group_df)
        
        time_aligned_df = pd.concat([time_aligned_df,
                                     each_group_df],
                                    ignore_index=True)
        
        unique_spine_label +=1
        
        try:
        
            norm_time_of_interest = each_group_df[each_group_df["Norm_time_min"] > 25]["Norm_time_min"].min()
            spine_vol = each_group_df[each_group_df["Norm_time_min"] == norm_time_of_interest]["Norm_intensity"].values[0]
            
            filename = os.path.basename(each_group_df["FilePath"].values[0])
            
            each_result = pd.DataFrame({
                            "filename":[filename],
                            "spine_vol":[spine_vol],
                            "spine_label":[each_group],
                            "norm_time_of_interest":[norm_time_of_interest],
                                  })
            
            if spine_vol < 10:
                spine_vol_list.append(spine_vol)
                summarized_df = pd.concat([summarized_df,each_result])
        except:
            print("Try -> Except")
            print(each_filepath)
            continue

allcombined_df=  everymin_normalize(time_aligned_df,
                                    bin_percent_median=0.99,
                                    time_threshold = 5)

summarized_df.to_csv(summarized_df_savepath)
        
plt.figure(figsize = [3,2])
# ##################################
sns.lineplot(x="Norm_time_min", y="Norm_intensity",
                legend=False, hue = "unique_spine_label", #marker='o',
                data = time_aligned_df
                )

np.array(spine_vol_list).mean()
savepath = summarized_df_savepath[:-4]+"_plot_all.png"
plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
ymin, ymax = plt.ylim()
xmin, xmax = plt.xlim()
plt.show()

each_save_folder = "\\".join(summarized_df_savepath.split("\\")[:-1]+["each_spine"])
os.makedirs(each_save_folder, exist_ok=True)
for each_hue in time_aligned_df["unique_spine_label"].unique():
    print(each_hue)
    each_df = time_aligned_df[time_aligned_df["unique_spine_label"] == each_hue]
    
    plt.title(os.path.basename(each_df["FilePath"].values[0])+"  spine "+ 
              str(each_df["ROInum"].values[0]))
    plt.plot(each_df["Norm_time_min"],
             each_df["Norm_intensity"],
                      )
    plt.plot([xmin, xmax],[1,1],"gray")
    plt.ylim([ymin, ymax])
    plt.xlim([xmin, xmax])
    savepath = os.path.join(each_save_folder,
                            os.path.basename(each_df["FilePath"].values[0][:-4])
                            +f"_spine_{each_df["ROInum"].values[0]}.png")
    plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
    plt.show()
    
    
def arrange_for_multipos3(resultdf, exclude_first = False,
                          time_min_range=[-20, 60]):
    
    newdf = pd.DataFrame()

    for ROInum in resultdf["ROInum"].unique(): 
        eachROIdf = resultdf[resultdf["ROInum"] ==  ROInum]
        zerotime = eachROIdf[eachROIdf["first_uncaging"] == 1]["time_sec"].values[0]
        eachROIdf["time_sec_norm"] = eachROIdf["time_sec"] - zerotime
        eachROIdf["time_min_norm"] = eachROIdf["time_sec_norm"]/60
        
        if exclude_first == True:
            eachROIdf = eachROIdf[~ (eachROIdf["NthFrame"] == 0)]
            
        eachROIdf = eachROIdf[(eachROIdf["time_min_norm"] >= time_min_range[0])&
                              (eachROIdf["time_min_norm"] <= time_min_range[1])]
 
        newdf = pd.concat([newdf,eachROIdf]) 
    
    return newdf

    
    

plt.figure(figsize = [3,2])
# ##################################
sns.lineplot(x="binned_min", y="Norm_intensity",
                # legend=False, hue = "unique_spine_label", #marker='o',
                data = time_aligned_df[time_aligned_df["binned_min"]<30],
                errorbar = 'se'
                )

np.array(spine_vol_list).mean()
savepath = summarized_df_savepath[:-4]+"_plot_Mean_with_SEM.png"
plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
ymin, ymax = plt.ylim()
xmin, xmax = plt.xlim()
plt.show()

# bin_sec = allcombined_df[allcombined_df['delta_sec']>time_threshold]['delta_sec'].median()*bin_percent_median    
# allcombined_df["binned_sec"] = bin_sec*(allcombined_df["time_sec_norm"]//bin_sec)
# allcombined_df["binned_min"] = allcombined_df["binned_sec"]/60
# return allcombined_df
