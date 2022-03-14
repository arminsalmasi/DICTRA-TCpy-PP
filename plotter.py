import copy
import glob
import os
import pickle

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tc_python import *
#******************************************************************************************************
def single_plotter(path, settings):
    for tflag in settings['timeflags']:
        filename = 'results_{}.pickle'.format(tflag)
        plt_settings = settings["plot_settings"]
        print('>>>>>> plotting tstp {} from {}'.format(tflag,path))
        with open(path+filename, 'rb') as f:
            data = pickle.load(f)
        
        if not(plt_settings['xlims']):
            plt_settings['xlims'] = get_xlims(data)
        plt_settings['ylims'] = get_ylims(0, 1)
    
        lst = [('tS_DICT_ufs', '$U \: fraction$', 'elnames'), 
                ('tS_DICT_mfs', '$Mole \: Fraction$' ,'elnames')]
                #('tS_DICT_npms', '$Phase \: Fraction$', 'tS_DICT_phnames') ]
        for i in lst:
            plt_settings['filename'] = path + i[0] + '_{}'.format(int(data['nearestTime']))
            plt_settings['title'] = path
            plt_settings['legend'] = data[i[2]]
            plt_settings['ylab'] = i[1]
            plot_list(data['tS_pts'], data[i[0]], plt_settings)
        
        lst = [('tS_TC_ws', '$Mass \:Fraction$'), 
                ('nameChanged_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$')]
                #('tS_TC_NEAT_vpvs', '$Volume \: Fraction$'), 
                #('sum_tS_DICT_npms' ,'Phase Fraction'), 
                #('sum_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$')]
                #('tS_TC_NEAT_npms', '$Phase \: Fraction$'), 
        for i in lst:
            plt_settings['filename'] = path+ i[0] + '_{}'.format(int(data['nearestTime']))
            plt_settings['title'] = path
            plt_settings['legend'] = data[i[0]].keys()
            plt_settings['ylab'] = i[1]
            plot_dict(data['tS_pts'], data[i[0]], plt_settings)
    
        lst = [('tS_TC_acSER', "$Log_{10}}(Activity) \: (SER)$")]
        for i in lst:
            plt_settings['filename'] = path + i[0] + '_{}'.format(int(data['nearestTime']))
            plt_settings['title'] = path
            plt_settings['legend'] = plt_settings["acSERleg"]#data[i[0]].keys()
            plt_settings['ylab'] = i[1]
            plot_ylog_dict(data['tS_pts'], data[i[0]], plt_settings)
        plt.close('all')
#*********************************************************************************************
def ol_plotter(*argv):
    path = argv[0]
    plt_settings = argv[1]["plot_settings"]
    tflags = argv[1]['timeflags']
    datalist=[]
    print('>>>>> overlaied plots in {}'.format(path))
    for tflag in tflags:
        with open(path+'/results_{}.pickle'.format(tflag), 'rb') as f:
            datalist.append(pickle.load(f))
    
    if not(plt_settings['xlims']):
        for t,tflag in enumerate(argv[1]):
            tmpxlims =[]    
            tmpxlims.append(get_xlims(datalist[t]))
        plt_settings['xlims'] = [min(tmpxlims[0]),max(tmpxlims[1])]
    else:
        pass
    
    plt_settings['ylims'] = get_ylims(0, 1)    
    lst = [('tS_DICT_ufs', '$U \: fraction$', 'elnames'), 
    ('tS_DICT_mfs', '$Mole \: Fraction$' ,'elnames')]
    #('tS_DICT_npms', '$Phase \: Fractions$', 'tS_DICT_phnames') ]
    for i in lst:
        ks = ['tS_pts', i[0], i[2]]
        plt_settings['ylab'] = i[1]
        plt_settings['filename'] = path+i[0]+"_{}_{}".format(tflags[0],tflags[1])
        plt_settings['title'] = path
        overlaied_list_plotter(datalist, ks, plt_settings)
    
    lst = [('tS_TC_ws', '$Mass \: Fraction$'), 
            ('nameChanged_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$')]
            #('tS_TC_NEAT_npms', '$Phase \: Fraction$'), 
            #('tS_TC_NEAT_vpvs', '$Volume \: Fraction$'),
            # ('sum_tS_DICT_npms', '$Phase \: Fraction$'), 
            # ('sum_CQT_tS_TC_NEAT_npms', '$Phase \: Fraction$') 
    for i in lst:
        ks = ['tS_pts', i[0]]
        plt_settings['ylab'] = i[1]
        plt_settings['filename'] = path+i[0]+"_{}_{}".format(tflags[0],tflags[1])
        plt_settings['title'] = path
        plot_keys=[]
        overlaied_dict_plotter(datalist, ks, plt_settings,plot_keys)
    
    lst = [('tS_TC_acSER', "$log_{10}(Activity)\: [SER]$")]
    for i in lst:
        ks = ['tS_pts', i[0], path]
        plt_settings['ylab'] = i[1]
        plt_settings['filename'] = path+i[0]+"_{}_{}".format(tflags[0],tflags[1])
        #plt_settings['title'] = dir2
        plt_settings['title'] = ''
        plot_keys = []#["C","CO","TI"]
        overlaied_dict_ylog_plotter(datalist, ks, plt_settings, plot_keys)
    plt.close('all')
#********************************************************************************************
def overlaied_list_plotter(datalist, ks, settings):
    _,ax = plt.subplots(1,1,figsize = settings["figsize"])
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        settings['legend'] = data[ks[2]]
        ax.plot(data[ks[0]],data[ks[1]],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def overlaied_list_ylog_plotter(datalist, ks, settings):
    _,ax = plt.subplots(1,1,figsize = settings["figsize"])
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        settings['legend'] = data[ks[2]]
        ax.plot(data[ks[0]],np.log10(data[ks[1]]),lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def overlaied_dict_plotter(datalist, ks, settings, plot_keys):
    _,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    lstyle=[':','-']
    lstyle=[':','-']
    for t,data in enumerate(datalist):
        if not plot_keys:
            settings['legend'] = list(data[ks[1]].keys())
        else:
            settings['legend'] = plot_keys
        for leg in settings['legend']:
            ax.plot(data[ks[0]],data[ks[1]][leg],lstyle[t],linewidth = settings['lineW'])
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'],loc=2,ncol=2)
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def overlaied_dict_ylog_plotter(datalist, ks, settings, plot_keys):
    _,ax = plt.subplots(1,1,figsize = settings["figsize"]) 
    lstyle=[':','-']
    lstyle=[':','-']
    dir = ks[2]
    for t,data in enumerate(datalist):
        if not plot_keys:
            settings['legend'] = list(data[ks[1]].keys())
        else:
            settings['legend'] = plot_keys
        for leg in settings['legend']:
            ax.plot(data[ks[0]],np.log10(data[ks[1]][leg]),lstyle[t],linewidth = settings['lineW'])
            tmp = pd.DataFrame() #temp
            if t==0: #temp 2nd ittertion
                tmp['x{}'.format(t+1)]= data[ks[0]] #temp
                tmp[leg+'{}'.format(t+1)] = np.log10(data[ks[1]][leg]) #temp
            tmp.to_csv(dir+'/log10_AC_first_SER.csv',index=False,sep=',')
            tmp = pd.DataFrame() #temp
            if t==1: #temp 2nd ittertion
                tmp['x{}'.format(t+1)]= data[ks[0]] #temp
                tmp[leg+'{}'.format(t+1)] = np.log10(data[ks[1]][leg]) #temp
            tmp.to_csv(dir+'/log10_AC_last_SER.csv',index=False,sep=',')
    ax.legend(np.append(settings['legend'],settings['legend']), fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def plot_list(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    _, ax = plt.subplots(1,1,figsize = settings["figsize"])
    ax.plot(x, y, linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def plot_dict(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    _, ax = plt.subplots(1,1,figsize = settings["figsize"])
    #lstyle=[':','-']
    for key in settings['legend']:
        ax.plot(x, y[key], linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'],loc=settings["locLegSing"],ncol=settings["ncolLegSing"])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def plot_ylog_list(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    _, ax = plt.subplots(1,1,figsize = settings["figsize"])
    ax.plot(x, np.log10(y), linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
#********************************************************************************************
def plot_ylog_dict(*argv):
    '''input: x, y, legend, title, xlims '''
    x = argv[0]
    y = argv[1]
    settings = argv[2]
    _, ax = plt.subplots(1,1,figsize = settings["figsize"])
    #lstyle=[':','-']
    for key in settings['legend']:
        ax.plot(x, np.log10(y[key]), linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlims'][0],settings['xlims'][1]),dpi=400, bbox_inches ='tight')
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
def all_GMX_plotter(path, allsettings):
    dirs = allsettings['dirList'] 
    settings = allsettings["plot_settings"]
    target_els = settings["MPlotlegs"]
    phase = settings["MPlotPhase"]
    settings['title'] = settings["MPlotPhase"]
    ks = settings["MPlotK"]
    for _,k in  enumerate(ks):
        _, ax = plt.subplots(1,1,figsize = settings["figsize"])
        #settings['ylims'] = ylims[nk]
        settings['ylab'] = k[1]
        legplotlist =[]
        markers = ["X","P","s","p","H","h"]
        cls = ['red','green','blue','k','magneta','c']
        settings['lineW'] = 3
        settings['filename'] = path+k[0]+"_ol"
        cln=0
        for dir in dirs:
            with open(path+dir+'/'+'results_last.pickle', 'rb') as f:
                data = pickle.load(f)
                print('>>>>>> plots GM from {}'.format(dir))
            leglist = [nel for nel,el in enumerate(data['elnames']) if el in target_els]
            settings['legend'] = data['elnames'][leglist]
            x,y = remove_undifined_logs(data, phase, k)
            n=0
            for nel in leglist:
                ax.plot(x[nel,:],y[nel,:],linewidth = settings['lineW'],color=cls[cln],marker=markers[n],markersize=13,fillstyle='none')
                n+=1
            legplotlist.append([el+'$ \: {}\degree C $'.format(data["T"]-273) for el in data['elnames'][leglist]])
            cln+=1
        legplotlist = np.array(legplotlist).ravel()
        ax.legend(legplotlist, fontsize = settings['legF'],loc=2)
        ax.set_xlim(settings['xlimsGM'])
        #ax.set_ylim(settings['ylims'])
        #ax.set_title(settings['title'])
        ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
        ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
        ax.tick_params(axis = "both", labelsize = settings['tickS'])
        ax.locator_params(axis = 'y', nbins = settings['bins'])
        ax.locator_params(axis = 'x', nbins = settings['bins'])
        [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
        plt.savefig(settings['filename']+'_{}_{}'.format(settings['xlimsGM'][0],settings['xlimsGM'][1]),dpi=400, bbox_inches ='tight')
#*********************************************************************************************
def remove_undifined_logs(data, phase, k):
    x,y=[],[]
    for nel in range(data[k[0]][phase].shape[1]):
        ynel, xnel =[], []
        for npt in range(data[k[0]][phase].shape[0]):
            if data[k[0]][phase][npt,nel] !=0 :
                ynel.append(np.log10([data[k[0]][phase][npt,nel]]))
                xnel.append(data['tS_pts'][npt])
        x.append(xnel)
        y.append(ynel)
    y=np.array(y)
    x=np.array(x)
    return x,y
#*********************************************************************************************


                    #for files in os.listdir(dir):
                    #if files.endswith('results_last.pickle') :
                    #    for filename in files.split("\n"):
                    #        if "uncorrected" not in filename:
                    #            with open(dir+'/'+filename, 'rb') as f:
                    #                data = pickle.load(f)
                    #                print('******* plots from {}'.format(dir))
                    #else:
                    #    continue
                    #else:
                        #continue