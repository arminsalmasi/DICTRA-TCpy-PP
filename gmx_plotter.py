import json
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from tc_python import *

#******************************************************************************************************
def single_plotter(DIR1, DIR2, filename):
    with open(DIR1+'plot_settings.json', 'r') as f:
        print('*****reading {}plot_settings.json'.format(DIR1))
        plt_settings = json.load(f)
    with open(DIR2+'/'+filename, 'rb') as f:
        data = pickle.load(f)
        print('******* plots from {}'.format(DIR2))
    plt_settings['figsize'] = [11,11]
    
    lst1 = [('tS_TC_NEAT_G', '$log_{10}(\Gamma ^{BCC} _{ \\alpha })$', 'elnames'),('tS_TC_NEAT_M', '$log_{10}(M^{BCC}_{\\alpha})$', 'elnames')]
    phase = 'BCC_A2#1'
    plt_settings['title'] = phase
    leglist = [nel for nel,el in enumerate(data['elnames']) if el in ['W','CO','C']]
    plt_settings['legend'] = data['elnames'][leglist]
    for k in lst1:
        plt_settings['filename'] = DIR2 + "/" + k[0] + '_{}'.format(int(data['nearestTime']))
        plt_settings['ylab'] = k[1]
        x,y = remove_undifined_logs(data, phase, k)
        phase_mg_plot(x, y, plt_settings,leglist)
    
    lst2 = ('tS_TC_NEAT_phXs', '$X^{BCC} _{ \\alpha }$', 'elnames')
    plt_settings['filename'] = DIR2 + "/" + lst2[0] + '_{}'.format(int(data['nearestTime']))
    plt_settings['legend'] = data['elnames']
    plt_settings['ylab'] = lst2[1]
    phase_x_plot(data['tS_pts'], data[lst2[0]][phase], plt_settings)
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
def phase_mg_plot(x, y, settings,leglist):
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    for nel in leglist:
        ax.plot(x[nel,:],y[nel,:],linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#*********************************************************************************************
def phase_x_plot(x, y, settings):
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    for nel in range(y.shape[1]):
        ax.plot(x,y[:,nel],linewidth = settings['lineW'])
    ax.legend(settings['legend'], fontsize = settings['legF'])
    ax.set_xlim(settings['xlims'])
    #ax.set_title(settings['title'])
    ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
    ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
    ax.tick_params(axis = "both", labelsize = settings['tickS'])
    ax.locator_params(axis = 'y', nbins = settings['bins'])
    ax.locator_params(axis = 'x', nbins = settings['bins'])
    [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
    plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#*********************************************************************************************
def all_GMX_plotter(DIR1, DIRs):
    with open(DIR1+'plot_settings.json', 'r') as f:
        print('*****reading {}plot_settings.json'.format(DIR1))
        settings = json.load(f)
    
    phase = 'BCC_A2#1'
    settings['title'] = phase
    settings['figsize'] = [13,13]
    k1 = ('tS_TC_NEAT_G', '$log_{10}(\Gamma ^{BCC} _{ \\alpha })$', 'elnames')
    k2 = ('tS_TC_NEAT_M', '$log_{10}(M^{BCC}_{\\alpha})$', 'elnames')
    ks = [k1,k2]
    for nk,k in  enumerate(ks):
        fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
        #settings['ylims'] = ylims[nk]
        settings['ylab'] = k[1]
        legplotlist =[]
        target_els = ['W','CO','C']
        markers = ["X","P","s"]
        settings['lineW'] = 3
        settings['filename'] = DIR1+k[0]+"_ol"
        for DIR in DIRs:
            for files in os.listdir(DIR):
                if files.endswith('results_last.pickle') :
                    for filename in files.split("\n"):
                        if "uncorrected" not in filename:
                            with open(DIR+'/'+filename, 'rb') as f:
                                data = pickle.load(f)
                                print('******* plots from {}'.format(DIR))
                            leglist = [nel for nel,el in enumerate(data['elnames']) if el in target_els]
                            print(leglist)
                            settings['legend'] = data['elnames'][leglist]
                            x,y = remove_undifined_logs(data, phase, k)
                            n=0
                            for nel in leglist:
                                ax.plot(x[nel,:],y[nel,:],linewidth = settings['lineW'],marker=markers[n],markersize=13,fillstyle='none')
                                n+=1
                            legplotlist.append([el+' {}K'.format(data["T"]-273) for el in data['elnames'][leglist]])
                        else:
                            continue
                else:
                    continue
        legplotlist = np.array(legplotlist).ravel()
        ax.legend(legplotlist, fontsize = settings['legF'],loc=4)
        ax.set_xlim(settings['xlims'])
        #ax.set_ylim(settings['ylims'])
        #ax.set_title(settings['title'])
        ax.set_ylabel(settings['ylab'], fontsize = settings['labF'])
        ax.set_xlabel(settings['xlab'], fontsize = settings['labF'])
        ax.tick_params(axis = "both", labelsize = settings['tickS'])
        ax.locator_params(axis = 'y', nbins = settings['bins'])
        ax.locator_params(axis = 'x', nbins = settings['bins'])
        [x.set_linewidth(settings["boxLW"]) for x in ax.spines.values()]
        plt.savefig(settings['filename'],dpi=200, bbox_inches ='tight')
#*********************************************************************************************
DIR1 = '/Volumes/exFAT/LUND/PCD/'
DIR2 =["DONE-1000C", "DONE-1200C"]    
DIRs = [DIR1+d+'/' for d in DIR2]
all_GMX_plotter(DIR1, DIRs)


