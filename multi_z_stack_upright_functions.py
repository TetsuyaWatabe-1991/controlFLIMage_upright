from time import sleep
import datetime
import os
from pathlib import Path
import glob
import tifffile
import numpy as np
from after_click_image_func import export_pos_dict_as_csv, get_abs_mm_pos_3d_from_click_list, \
    save_pix_pos_from_click_list, save_image_with_assigned_pos_3d, get_ZYX_pix_list_from_csv, \
    get_abs_um_pos_from_center_3d, save_um_pos_from_click_list
from multidim_tiff_viewer import z_stack_multi_z_click
from FLIMageFileReader2 import FileReader

def sleep_countdown(sleep_sec, 
                    define_starttime = False,
                    start_time = -1):
    count_dict = {301:20,
                  61:10,
                  16:5,
                  0:1}
    
    if define_starttime == True:
        if type(start_time) != datetime.datetime:
            print("\n\n  please use datetime.datetime type for start_time. \n")
            start_time = datetime.datetime.now()
    else:
        start_time = datetime.datetime.now()
    while True:
        now = datetime.datetime.now()
        elapsed_time_sec = (now - start_time).total_seconds()
        if elapsed_time_sec >= sleep_sec:
            break
        remaining_sec = sleep_sec - elapsed_time_sec
        print(int(remaining_sec), end = " ")
        for each_threshold_sec in count_dict:            
            if remaining_sec > each_threshold_sec:
                sleep(count_dict[each_threshold_sec])
                break


def click_zstack_for_all_in_dir(parent_path):
    dir_list = glob.glob(os.path.join(parent_path,"*\\"))
    for each_dir in dir_list:
        click_zstack_export_pos(each_dir)

def click_zstack_export_pos(dir_name, use_predefined_pos = True):
    tif_path = os.path.join(dir_name, "stitched_each_z.tif")
    tiling_setting_jsonpath = os.path.join(dir_name, "setting.json")
    stack_array = tifffile.imread(tif_path)
    
    pos_csv_path = os.path.join(dir_name, "assigned_pixel_pos.csv")
    ZYX = []
    if use_predefined_pos:
        if os.path.exists(pos_csv_path):
            ZYX = get_ZYX_pix_list_from_csv(pos_csv_path)
    
    pix_zyx_list = z_stack_multi_z_click(stack_array = stack_array, 
                                         pre_assigned_pix_zyx_list=ZYX,
                                         show_text=dir_name)
    
    get_abs_mm_pos_dict = get_abs_mm_pos_3d_from_click_list(tiling_setting_jsonpath, 
                                                            pix_zyx_list)
    export_pos_dict_as_csv(get_abs_mm_pos_dict, 
                           csv_savepath = os.path.join(dir_name, "assigned_pos_highmag_widefield.csv"))
    save_pix_pos_from_click_list(pix_zyx_list, csv_savepath = pos_csv_path)
    
    eachpos_export_path = os.path.join(dir_name, "each_pos_export")
    os.makedirs(eachpos_export_path, exist_ok=True)
    for eachpng in glob.glob(os.path.join(eachpos_export_path, "*.png")):
        os.remove(eachpng)
    save_image_with_assigned_pos_3d(tif_path = tif_path,
                                    pix_pos_csv_path = os.path.join(dir_name, "assigned_pixel_pos.csv"),
                                    png_savefolder = eachpos_export_path)

def click_zstack_flimfile(flim_file_path, use_predefined_pos = True):
    iminfo = FileReader()
    iminfo.read_imageFile(flim_file_path, True)
    ZYXarray = np.array(iminfo.image).sum(axis=tuple([1,2,5]))

    eachpos_export_path = os.path.join(Path(flim_file_path).parent,
                                       Path(flim_file_path).stem)    
    os.makedirs(eachpos_export_path, exist_ok=True)
    for eachpng in glob.glob(os.path.join(eachpos_export_path, "*.png")):
        os.remove(eachpng)
    pos_csv_path = os.path.join(eachpos_export_path, "assigned_pixel_pos.csv")
    ZYX = []
    if use_predefined_pos:
        if os.path.exists(pos_csv_path):
            ZYX = get_ZYX_pix_list_from_csv(pos_csv_path)
        else:
            print("could not find file pos info file.")
    
    pix_zyx_list = z_stack_multi_z_click(stack_array = ZYXarray, 
                                         pre_assigned_pix_zyx_list=ZYX,
                                         show_text=flim_file_path)
    
    save_pix_pos_from_click_list(pix_zyx_list, csv_savepath = pos_csv_path)
    
    ZYX_um_dict = get_abs_um_pos_from_center_3d(statedict = iminfo.statedict,
                                                pix_zyx_list = pix_zyx_list)
    pos_rel_um_csv_path = os.path.join(eachpos_export_path, "assigned_relative_um_pos.csv")
    save_um_pos_from_click_list(ZYX_um_dict = ZYX_um_dict, 
                                csv_savepath = pos_rel_um_csv_path)
    save_image_with_assigned_pos_3d(tif_path = "",
                                    pix_pos_csv_path = pos_csv_path,
                                    png_savefolder = eachpos_export_path,
                                    input_arr=True, array=ZYXarray)



    
if __name__ == "__main__":
    filepath = r"G:\ImagingData\Tetsuya\20240626\multipos_3\e_001.flim"
    click_zstack_flimfile(filepath)
    
    pass
    
    
    
    