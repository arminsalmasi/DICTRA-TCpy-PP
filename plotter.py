import copy
import glob
import json
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
from tc_python import *

from clibv2 import *  # %matplotlib qt#user_path = !eval echo ~$USER


#********************************************************************************************
def ol_plotter(*argv):
    DIR1=argv[0]
    DIR2 = argv[1]
    tflags=argv[2]
    print(DIR2)
    with open(DIR1+'plot_settings.json', 'r') as f:
        plt_settings = json.load(f)
    datalist=[]
    
    for tflag in tflags:
        with open(DIR2+'/results_{}.pickle'.format(tflag), 'rb') as f:
            datalist.append(pickle.load(f))
    
    if not(plt_settings['xlims']):
        for t,tflag in enumerate(argv[1]):
            tmpxlims =[]    
            tmpxlims.append(get_xlims(datalist[t]))
        plt_settings['xlims'] = [min(tmpxlims[0]),max(tmpxlims[1])]
    else:
        pass
    
    plt_settings['ylims'] = get_ylims(0, 1)    
    lst = [('tS_DICT_ufs', '$U \: fraction$', 'elnames'), ('tS_DICT_mfs', '$Mole \: Fraction$' ,'elnames') ,('tS_DICT_npms', '$Phase \: Fractions$', 'tS_DICT_phnames') ]
    for i in lst:
        ks=['tS_pts', i[0], i[2], i[1]]
        overlaied_list_plotter(datalist, ks, plt_settings, DIR2, tflags)
    
    lst = [('tS_TC_ws', '$Mass \: Fraction$'), ('tS_TC_NEAT_npms', '$Phase \: Fraction$'), ('tS_TC_NEAT_vpvs', '$Volume \: Fraction$'), 
    ('nameChanged_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$'), ('sum_tS_DICT_npms', '$Phase \: Fraction$'), ('sum_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$')]
    for i in lst:
        ks=['tS_pts', i[0], i[1] ]
        overlaied_dict_plotter(datalist, ks, plt_settings, DIR2, tflags)
    plt.close('all')
#********************************************************************************************
def plotter(DIR1, DIR2, filename):
    
    with open(DIR1+'plot_settings.json', 'r') as f:
        print(DIR1+'plot_settings.json')
        plt_settings = json.load(f)
    
    with open(DIR2+'/'+filename, 'rb') as f:
        tS_tc_VLUs = pickle.load(f)
    
    if not(plt_settings['xlims']):
        plt_settings['xlims'] = get_xlims(tS_tc_VLUs)
    plt_settings['ylims'] = get_ylims(0, 1)

    lst = [('tS_DICT_ufs', '$U \: fraction$', 'elnames'), ('tS_DICT_mfs', '$Mole \: Fraction$' ,'elnames') ,('tS_DICT_npms', '$Phase \: Fraction$', 'tS_DICT_phnames') ]
    for i in lst:
        ks=['tS_pts', i[0], i[2], i[1], DIR2 + "/" + i[0] + '_{}'.format(int(tS_tc_VLUs['nearestTime']))]
        list_plotter(tS_tc_VLUs, ks, plt_settings)
    
    lst = [('tS_TC_ws', '$Mass \:Fraction$'), ('tS_TC_NEAT_npms', '$Phase \: Fraction$'), ('tS_TC_NEAT_vpvs', '$Volume \: Fraction$'), 
    ('nameChanged_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$'), ('sum_tS_DICT_npms' ,'Phase Fraction'), ('sum_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$')]
    for i in lst:
        ks=['tS_pts', i[0], i[1], DIR2+ "/" + i[0] + '_{}'.format(int(tS_tc_VLUs['nearestTime']))]
        dict_plotter(tS_tc_VLUs, ks, plt_settings)
    plt.close('all')
#********************************************************************************************
def list_plotter(data,ks,settings):
    settings['legend'] = data[ks[2]]
    settings['ylab'] = ks[3]
    settings['filename'] = ks[4]
    plot_list(data[ks[0]], data[ks[1]], settings)
#********************************************************************************************
def dict_plotter(data,ks,settings):
    settings['legend'] = data[ks[1]].keys()
    settings['ylab'] = ks[2]
    settings['filename'] = ks[3]
    plot_dict(data[ks[0]], data[ks[1]], settings)
#********************************************************************************************
def plot_list(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    ax.set_title(os.getcwd()) 
    ax.plot(x, y, linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
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
def overlaied_list_plotter(datalist, ks, settings, DIR, tflags):
    settings['ylab'] = ks[3]
    tmpstr=DIR+"/"+ks[1]+"_{}_{}".format(tflags[0],tflags[1])
    settings['filename']=tmpstr
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    ax.set_title(os.getcwd()) 
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        settings['legend'] = data[ks[2]]
        ax.plot(data[ks[0]],data[ks[1]],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
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
    ax.set_title(os.getcwd()) 
    lstyle=[':','-']
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
def overlaied_dict_plotter(datalist, ks, settings, DIR, tflags):
    settings['ylab'] = ks[2]
    tmpstr=DIR+"/"+ks[1]+"_{}_{}".format(tflags[0],tflags[1])
    settings['filename']=tmpstr
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    ax.set_title(DIR) 
    lstyle=[':','-']
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        settings['legend'] = list(data[ks[1]].keys())
        for leg in settings['legend']:
            ax.plot(data[ks[0]],data[ks[1]][leg],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
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
