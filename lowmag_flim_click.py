#%%
import os, glob
import datetime
from multi_z_stack_upright_functions import click_zstack_flimfile

def click_flim_list(folder, filename_example):
    print("click_flim_list")
    print("filename_example: ", os.path.join(folder,filename_example))
    filelist = glob.glob(os.path.join(folder,filename_example))
    if len(filelist) == 0:
        print("No files found")
        print("check the folder and filename_example")
        return
    for each_flim in filelist:
        now = datetime.datetime.now()
        modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(each_flim))
        delta = (now - modified_date).total_seconds()
        if delta > 20:
            click_zstack_flimfile(each_flim, use_predefined_pos = True)
        else:
            print("skipping: ", each_flim)
            print("this file was modified less than 20 seconds ago")
    for each_flim in filelist:
        print('r"'+each_flim+'",')


if __name__ == "__main__":
    folder = r"C:\Users\Yasudalab\Documents\Tetsuya_Imaging\20250520\E4bufferMNI4Ca"
    filename_example = "lowmag*_001.flim"
    click_flim_list(folder, filename_example)
# %%
