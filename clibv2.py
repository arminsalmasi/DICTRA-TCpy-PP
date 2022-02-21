import copy
import glob
import json
import os
import pdb
import pickle
import random
import sys
import tkinter as ttk
from collections import defaultdict
from copy import deepcopy
from tkinter import Tk, filedialog, font

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import clear_output
from scipy.ndimage.filters import gaussian_filter1d
from scipy.optimize import brentq as find_root
from tc_python import *

from clibv2 import *  # %matplotlib qt#user_path = !eval echo ~$USER

#********************************************************************************************
def plotter(DIR, filename):
    # ''' Plotting/get plot limits '''
    # '''read files'''
    with open(DIR+'/'+filename, 'rb') as f:
        tS_tc_VLUs = pickle.load(f)
    with open(DIR+'plot_settings.json', 'r') as f:
        plt_settings = json.load(f)
    #del_pngs()
    # '''get xlimits'''
    if not(plt_settings['xlims']):
        plt_settings['xlims'] = get_xlims(tS_tc_VLUs)
    plt_settings['ylims'] = get_ylims(0, 1)

    plt_settings['legend'] = tS_tc_VLUs['elnames']
    #plt_settings['title'] ='MFs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Mole Fraction'
    plt_settings['filename'] = DIR+"/"+'MF_{}'.format(
        int(int(tS_tc_VLUs['nearestTime'])))
    plot_list(tS_tc_VLUs['tS_pts'], tS_tc_VLUs['tS_DICT_mfs'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['elnames']
    #plt_settings['title'] = 'UFs , t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'U-Fraction'
    plt_settings['filename'] = DIR+"/"+'UF_{}'.format(int(tS_tc_VLUs['nearestTime']))
    plot_list(tS_tc_VLUs['tS_pts'], tS_tc_VLUs['tS_DICT_ufs'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['tS_TC_ws'].keys()
    #plt_settings['title'] = 'WFs , t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Weight Fraction'
    plt_settings['filename'] = DIR+"/"+'WF_{}'.format(int(tS_tc_VLUs['nearestTime']))
    plot_dict(tS_tc_VLUs['tS_pts'], tS_tc_VLUs['tS_TC_ws'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['tS_DICT_phnames']
    #plt_settings['title'] = 'DICTRA NPMs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'tS_DICT_npms_{}'.format(
        int(tS_tc_VLUs['nearestTime']))
    plot_list(tS_tc_VLUs['tS_pts'], tS_tc_VLUs['tS_DICT_npms'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['tS_TC_NEAT_npms'].keys()
    #plt_settings['title'] = 'TC NPMs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'tS_TC_NEAT_npms_{}'.format(
        int(tS_tc_VLUs['nearestTime']))
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['tS_TC_NEAT_npms'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['tS_TC_NEAT_vpvs'].keys()
    #plt_settings['title'] = 'TC VPVs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'tS_TC_NEAT_vpvs_{}'.format(
        int(tS_tc_VLUs['nearestTime']))
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['tS_TC_NEAT_vpvs'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['nameChanged_CQT_tS_TC_NEAT_npms'].keys()
    #plt_settings['title'] = 'TC summed NPMs changed names, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'nameChanged_CQT_tS_TC_NEAT_npms_{}'.format(
        int(tS_tc_VLUs['nearestTime']))
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['nameChanged_CQT_tS_TC_NEAT_npms'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['sum_CQT_tS_TC_NEAT_npms'].keys()
    #plt_settings['title'] = 'TC summed corrected neat NPMs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'sum_CQT_tS_TC_NEAT_npms_{}'.format(
        int(tS_tc_VLUs['nearestTime']))
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['sum_CQT_tS_TC_NEAT_npms'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['sum_tS_DICT_npms'].keys()
    #plt_settings['title'] = 'DICTRA NPMs, summed composition sets, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'sum_tS_DICT_npms_{}'.format(tS_tc_VLUs['tS'])
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['sum_tS_DICT_npms'], plt_settings)

    plt_settings['legend'] = tS_tc_VLUs['CQT_tS_TC_NEAT_npms'].keys()
    #plt_settings['title'] = 'TC corrected neat NPMs, t = {}'.format(int(tS_tc_VLUs['nearestTime']))
    plt_settings['ylab'] = 'Phase Fraction'
    plt_settings['filename'] = DIR+"/"+'CQT_tS_TC_NEAT_npms_{}'.format(
        tS_tc_VLUs['tS'])
    plot_dict(tS_tc_VLUs['tS_pts'],
              tS_tc_VLUs['CQT_tS_TC_NEAT_npms'], plt_settings)
    plt.close('all')
#********************************************************************************************
def get_xlims(*argv):
    if len(argv) == 3:
        dict_in,x1,x2 = argv[0],argv[1],argv[2]
        flag = True
    elif len(argv)==1:
        dict_in = argv[0]
        flag = False
    dict = copy.deepcopy(dict_in)
    if flag:
        pass
    else:
        x1 = float(input('xlims = /{}, {}/x1?/:\n'.format(dict['tS_pts'][0], dict['tS_pts'][-1])))
        x2 = float(input('xlims = /{}, {}/x2?/:\n'.format(dict['tS_pts'][0], dict['tS_pts'][-1])))
    return [x1, x2]
#********************************************************************************************
def get_ylims(y1,y2):
    if (type(y1) == float and type(y2)==float) or (type(y1) == int and type(y2)==int):
        pass
    else:
        y1 = 0
        y2 = 1
        y1 = float(input('ylims = /{}, {}/y1?/:\n'.format(y1,y2)))
        y2 = float(input('ylims = /{}, {}/y2?/:\n'.format(y1,y2)))
    return [y1, y2]
#********************************************************************************************
def del_pngs():
    '''Deleting png files'''
    fileList = glob.glob('*.png', recursive = True)
    # Iterate over the list of filepaths & remove each file.
    for filePath in fileList:
        try:
            os.remove(filePath)
        except OSError:
            print("Error while deleting file")  
#********************************************************************************************
def plot_list(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    ax.plot(x, y, linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    #plt.rcParams['axes.linewidth'] = settings["boxLW"] 
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#********************************************************************************************
def overlaied_plot_list(keys,datalist,settings,DIR,tflags):
    settings['legend'] = datalist[0][keys[2]]
    settings['ylab'] = keys[3]
    tmpstr=DIR+"/"+keys[4]
    for t in tflags:
        tmpstr = keys[4]+'_{}_'.format(t)
    settings['filename']=tmpstr
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        ax.plot(data[keys[0]],data[keys[1]],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
    print(np.append(settings['legend'],settings['legend']))
    ax.set_xlim(settings['xlims'])
    ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#********************************************************************************************
def plot_dict(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    for key in settings['legend']:
        ax.plot(x, y[key], linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    #plt.rcParams['axes.linewidth'] = settings["boxLW"] 
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'], dpi=200, bbox_inches ='tight')
#********************************************************************************************
def overlaied_plot_dict(keys,datalist,settings,DIR,tflags):
    settings['legend'] = datalist[0][keys[2]]
    settings['ylab'] = keys[3]
    tmpstr=DIR+"/"+keys[4]
    for t in tflags:
        tmpstr = keys[4]+'_{}_'.format(t)
    settings['filename']=tmpstr
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        for key in settings['legend']:
            ax.plot(data[keys[0]],data[keys[1]][key],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
    print(np.append(settings['legend'],settings['legend']))
    ax.set_xlim(settings['xlims'])
    ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#********************************************************************************************
def overlaidplot(*argv):
    DIR = argv[0]
    tflags=argv[1]
    with open(DIR+'plot_settings.json', 'r') as f:
        plt_settings = json.load(f)
    datalist=[]
    for tflag in tflags:
        with open(DIR+'/results_{}.pickle'.format(tflag), 'rb') as f:
            datalist.append(pickle.load(f))
    # '''get xlimits'''
    if not(plt_settings['xlims']):
        for t,tflag in enumerate(argv[1]):
            tmpxlims =[]    
            tmpxlims.append(get_xlims(datalist[t]))
        plt_settings['xlims'] = [min(tmpxlims[0]),max(tmpxlims[1])]
    else:
        pass
    plt_settings['ylims'] = get_ylims(0, 1)    
    keys =['tS_pts','tS_DICT_mfs','elnames', 'Mole Fractions', DIR+'ol_MF']
    overlaied_plot_list(keys,datalist,plt_settings,DIR,tflags)
    keys =['tS_pts','tS_DICT_ufs','elnames', 'U-Fractions', DIR+'ol_UF']
    overlaied_plot_list(keys,datalist,plt_settings,DIR,tflags)
    keys =['tS_pts','tS_TC_ws','elnames', 'MASS Fractions', DIR+'ol_WF']
    overlaied_plot_dict(keys,datalist,plt_settings,DIR,tflags)