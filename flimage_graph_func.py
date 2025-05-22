# -*- coding: utf-8 -*-
"""
Created on Fri May  9 16:09:00 2025

@author: yasudalab
"""

import sys
sys.path.append(r"C:\Users\yasudalab\Documents\Tetsuya_GIT\controlFLIMage")
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from skimage.draw import disk, polygon
from scipy.ndimage import median_filter
from FLIMageFileReader2 import FileReader
from multidim_tiff_viewer import read_xyz_single

def color_fue(savefolder = r"C:\Users\yasudalab\Documents\Tetsuya_GIT\controlFLIMage\ForUse",
              vmin =1, vmax=10, cmap='inferno', label_text = "F/F0",fontsize = 48,
              savefig = True
              ):
    norm = Normalize(vmin=vmin, vmax=vmax)
    sm = ScalarMappable(norm=norm, cmap=cmap)
    
    # ===== Vertical Right =====
    fig, ax = plt.subplots(figsize=(2, 6), facecolor='none')
    cbar = plt.colorbar(sm, cax=ax, orientation='vertical')
    cbar.ax.set_yticks([])
    cbar.ax.tick_params(size=0)
    for spine in cbar.ax.spines.values():
        spine.set_visible(False)
    
    # Add value labels
    cbar.ax.text(0.5, 1.02, str(vmax), ha='center', va='bottom', fontsize=fontsize, transform=cbar.ax.transAxes)
    cbar.ax.text(0.5, -0.02, str(vmin), ha='center', va='top', fontsize=fontsize, transform=cbar.ax.transAxes)
    
    # Add F/F₀ label to right side
    cbar.ax.text(1.3, 0.5, label_text, ha='left', va='center', fontsize=fontsize, rotation=90, transform=cbar.ax.transAxes)
    
    plt.tight_layout()
    savepath = os.path.join(savefolder, f"vert_rt_{vmin}to{vmax}.png")
    if savefig:
        plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
        plt.close(); plt.clf();
    else:
        plt.show()
        
    # ===== Vertical Left =====
    fig, ax = plt.subplots(figsize=(2, 6), facecolor='none')
    cbar = plt.colorbar(sm, cax=ax, orientation='vertical')
    cbar.ax.set_yticks([])
    cbar.ax.tick_params(size=0)
    for spine in cbar.ax.spines.values():
        spine.set_visible(False)
    
    # Value labels
    cbar.ax.text(0.5, 1.02, str(vmax), ha='center', va='bottom', fontsize=fontsize, transform=cbar.ax.transAxes)
    cbar.ax.text(0.5, -0.02, str(vmin), ha='center', va='top', fontsize=fontsize, transform=cbar.ax.transAxes)
    
    # Label on left side
    cbar.ax.text(-0.3, 0.5, label_text, ha='right', va='center', fontsize=fontsize, rotation=90, transform=cbar.ax.transAxes)
    
    plt.tight_layout()
    savepath = os.path.join(savefolder, f"vert_lt_{vmin}to{vmax}.png")
    if savefig:
        plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
        plt.close(); plt.clf();
    else:
        plt.show()
    
    
    
    
    # ===== Horizontal =====
    fig, ax = plt.subplots(figsize=(6, 2), facecolor='none')
    cbar = plt.colorbar(sm, cax=ax, orientation='horizontal')
    cbar.ax.set_xticks([])
    cbar.ax.tick_params(size=0)
    for spine in cbar.ax.spines.values():
        spine.set_visible(False)
    
    # Value labels
    cbar.ax.text(-0.02, 0.5, str(vmin), ha='right', va='center', fontsize=fontsize, transform=cbar.ax.transAxes)
    cbar.ax.text(1.02, 0.5, str(vmax), ha='left', va='center', fontsize=fontsize, transform=cbar.ax.transAxes)
    
    # Label below bar
    cbar.ax.text(0.5, -0.1, label_text, ha='center', va='top', fontsize=fontsize, transform=cbar.ax.transAxes)
    
    plt.tight_layout()
    savepath = os.path.join(savefolder, f"hori_{vmin}to{vmax}.png")
    if savefig:
        plt.savefig(savepath, dpi = 150, bbox_inches = "tight")
        plt.close(); plt.clf();
    else:
        plt.show()




def plot_GCaMP_F_F0(each_file, slope = 0, intercept = 0, 
                    from_Thorlab_to_coherent_factor = 1/3,
                    vmin = 1, vmax = 10, cmap='inferno', 
                    acceptable_image_shape_0th_list = [4,33,34]):
    uncaging_iminfo = FileReader()
    uncaging_iminfo.read_imageFile(each_file, True) 
    
    imagearray=np.array(uncaging_iminfo.image)
    
    if (imagearray.shape)[0] not in acceptable_image_shape_0th_list:
        print("Image shape is not expected size.  ",imagearray.shape)
        return
    
    uncaging_x_y_0to1 = uncaging_iminfo.statedict["State.Uncaging.Position"]
    uncaging_pow = uncaging_iminfo.statedict["State.Uncaging.Power"]
    pulseWidth = uncaging_iminfo.statedict["State.Uncaging.pulseWidth"]
    center_y = imagearray.shape[-2] * uncaging_x_y_0to1[1]
    center_x = imagearray.shape[-3] * uncaging_x_y_0to1[0]
       
    GCpre = imagearray[0,0,0,:,:,:].sum(axis = -1)
    GCunc = imagearray[3,0,0,:,:,:].sum(axis = -1)
 
    GC_pre_med = median_filter(GCpre, size=3)
    GC_unc_med = median_filter(GCunc, size=3)
    
    GCF_F0 = (GC_unc_med/GC_pre_med)
    GCF_F0[GC_pre_med == 0] = 0
       
    pow_mw = slope * uncaging_pow + intercept
    pow_mw_coherent = pow_mw/3
    pow_mw_round = round(pow_mw_coherent,1)
       
    plt.imshow(GCF_F0, cmap = cmap, vmin = vmin, vmax = vmax)
    plt.plot(center_x, center_y, 'co', markersize=4)   
    
    if pow_mw_round > 0:
        plt.title(f"{pow_mw_round} mW, {pulseWidth} ms")  
    else:
        plt.title(f"{uncaging_pow} %, {pulseWidth} ms")  
    plt.axis('off')
    
    folder = os.path.dirname(each_file)
    savefolder = os.path.join(folder,"plot")
    os.makedirs(savefolder, exist_ok=True)
    basename = os.path.basename(each_file)                
    savepath = os.path.join(savefolder, basename[:-5] + ".png")
    plt.savefig(savepath, dpi=150, bbox_inches = "tight")
    
    plt.show()
    
    color_fue(savefolder = savefolder,
              vmin =vmin, vmax=vmax, cmap=cmap, label_text = "F/F0")
                  

    
    
def calc_point_on_line_close_to_xy(x, y, slope, intercept):   
    x_c = (x + slope * (y - intercept)) / (slope**2 + 1)
    y_c = slope * x_c + intercept
    return y_c, x_c


def calc_spine_dend_GCaMP(
    each_file,
    spine_y = -1,
    spine_x = -1,    
    drift_y_pix = 0,
    drift_x_pix = 0,
    dend_slope = 0,
    dend_intercept = 0,
    each_ini = "",
    from_ini = True,
    circle_radius = 3,  # Set as needed
    rect_length = 10,  # along the line
    rect_height = 2   # perpendicular to the line
    ):
    
    if from_ini:
        spine_zyx, dend_slope, dend_intercept, excluded = read_xyz_single(each_ini,
                                                          return_excluded = True)
        spine_x = spine_zyx[2]
        spine_y = spine_zyx[1]
    
    
    #drift correction
    spine_x -= drift_x_pix
    spine_y -= drift_y_pix
    dend_intercept -=  -dend_slope * drift_x_pix + drift_y_pix
    
    y_c, x_c = calc_point_on_line_close_to_xy(x = spine_x, y = spine_y, 
                                   slope = dend_slope, 
                                   intercept = dend_intercept)
    
    
    
    uncaging_iminfo = FileReader()
    uncaging_iminfo.read_imageFile(each_file, True) 
    
    imagearray=np.array(uncaging_iminfo.image)
    GCpre = imagearray[0,0,0,:,:,:].sum(axis = -1)
    GCunc = imagearray[3,0,0,:,:,:].sum(axis = -1)
    GC_pre_med = median_filter(GCpre, size=3)
    GC_unc_med = median_filter(GCunc, size=3)
    
    GCF_F0 = (GC_unc_med/GC_pre_med)
    GCF_F0[GC_pre_med == 0] = 0
    # print(f"Closest point on the line: ({x_c:.3f}, {y_c:.3f})")
      
    ### circle
    
    rr_circ, cc_circ = disk((spine_y, spine_x), circle_radius, shape=GC_unc_med.shape)
    spine_mean_pre = GC_pre_med[rr_circ, cc_circ].mean()
    spine_mean_unc = GC_unc_med[rr_circ, cc_circ].mean()
        
    ### rectangle
    
    # 2. Rectangle ROI aligned with the dendrite line
    theta = np.arctan(dend_slope)
    dx = (rect_length / 2) * np.cos(theta)
    dy = (rect_length / 2) * np.sin(theta)
    px = (rect_height / 2) * -np.sin(theta)
    py = (rect_height / 2) * np.cos(theta)
    
    # Rectangle corners
    corners_x = [x_c - dx - px, x_c - dx + px, x_c + dx + px, x_c + dx - px]
    corners_y = [y_c - dy - py, y_c - dy + py, y_c + dy + py, y_c + dy - py]
    
    rr_rect, cc_rect = polygon(corners_y, corners_x, shape=GC_unc_med.shape)
    shaft_mean_pre = GC_pre_med[rr_rect, cc_rect].mean()
    shaft_mean_unc = GC_unc_med[rr_rect, cc_rect].mean()
    
    
    # Plot
    plt.figure(figsize=(4, 4))
    vmax=np.percentile(GCunc,99.9)
    GCunc8bit=(GCunc/vmax * 255).astype(np.uint8)
    GCunc8bit[GCunc>vmax] = 255
    GCunc_24bit = np.zeros((GC_unc_med.shape[0], GC_unc_med.shape[1], 3), dtype=np.uint8)
    
    GCunc_24bit[:,:,0]=GCunc8bit
    GCunc_24bit[:,:,1]=GCunc8bit
    GCunc_24bit[:,:,2]=GCunc8bit
    GCunc_24bit[rr_circ, cc_circ,0] = 255
    GCunc_24bit[rr_circ, cc_circ,1] = 0
    GCunc_24bit[rr_circ, cc_circ,2] = 0
    GCunc_24bit[rr_rect, cc_rect,0] = 0
    GCunc_24bit[rr_rect, cc_rect,1] = 0
    GCunc_24bit[rr_rect, cc_rect,2] = 255
    plt.imshow(GCunc_24bit)
    plt.title("ROIs on Image")
    plt.axis("off")
    folder = os.path.dirname(each_file)
    savefolder = os.path.join(folder,"plot")
    os.makedirs(savefolder, exist_ok=True)
    basename = os.path.basename(each_file)                
    savepath = os.path.join(savefolder, basename[:-5] + ".png")
    plt.savefig(savepath, dpi=150, bbox_inches = "tight")
    
    plt.show()
    
    spineF_F0 = spine_mean_unc/spine_mean_pre
    shaftF_F0 = shaft_mean_unc/shaft_mean_pre
    print("spine",round(spine_mean_pre,1), round(spine_mean_unc,1), " F_F0",round(spineF_F0,1))
    print("shaft",round(shaft_mean_pre,1), round(shaft_mean_unc,1), " F_F0",round(shaftF_F0,1))

    return spineF_F0, shaftF_F0
    
    
if __name__ == "__main__":
    
    each_file   =  r"G:\ImagingData\Tetsuya\20250508\titration_dend1_31um_006.flim"
    slope = 0.210
    intercept = 0.1145
    # from_Thorlab_to_coherent_factor = 1/3
    plot_GCaMP_F_F0(each_file = each_file)
    # plot_GCaMP_F_F0(each_file = each_file,
    #                 slope = slope, intercept = intercept)