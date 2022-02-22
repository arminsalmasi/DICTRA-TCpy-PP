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
    print('******* plots from {}'.format(DIR2))
    with open(DIR2+'/'+filename, 'rb') as f:
        data = pickle.load(f)
    plt_settings['xlims'] = [150,400]
    lst = [('tS_TC_NEAT_G', '$Permeability$', 'elnames'),('tS_TC_NEAT_M', '$Mobility$$', 'elnames')]
    for phase in data['tS_TC_NEAT_G'].keys():
        if 'BCC' in phase:
            for k in lst:
                plt_settings['filename'] = DIR2 + "/" + k[0] + '_{}'.format(int(data['nearestTime']))
                plt_settings['title'] = phase
                plt_settings['legend'] = data[k[2]]
                plt_settings['ylab'] = k[1]
                x,y =[],[]                
                for nel in range(data[k[0]][phase].shape[1]):
                    ynel = []
                    xnel =[]
                    for npt in range(data[k[0]][phase].shape[0]):
                        if data[k[0]][phase][npt,nel] !=0 :
                            ynel.append(np.log10([data[k[0]][phase][npt,nel]]))
                            xnel.append(data['tS_pts'][npt])
                    x.append(xnel)
                    y.append(ynel)
                phase_mg_plot(x, y, plt_settings)
    k = ('tS_TC_NEAT_phXs', '$Fraction$', 'elnames')
    for phase in data['tS_TC_NEAT_phXs'].keys():
        if 'BCC' in phase:
            plt_settings['filename'] = DIR2 + "/" + k[0] + '_{}'.format(int(data['nearestTime']))
            plt_settings['title'] = phase
            plt_settings['legend'] = data[k[2]]
            plt_settings['ylab'] = k[1]
            x,y =[],[]                
            phase_x_plot(data['tS_pts'], data[k[0]][phase], plt_settings)
#*********************************************************************************************
def phase_mg_plot(x, y, settings):
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    for nel in range(len(y)):
        ax.plot(x[nel],y[nel],linewidth = settings['lineW'])
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
#*********************************************************************************************
def phase_x_plot(x, y, settings):
    fig,ax = plt.subplots(1,1,figsize = settings["figsize"])
    for nel in range(y.shape[1]):
        ax.plot(x,y[:,nel],linewidth = settings['lineW'])
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
#*********************************************************************************************
DIR1 = '/Volumes/exFAT/LUND/WC15Co-Ti64-200um200um/'
DIR2 =["DONE-1300C", "1300C-2ndrun", "DONE-1000C", "DONE-1000C-2ndrun", "DONE-1200C", "DONE-1200C-2ndrun", "DONE-1200C-570sec"]    
DIRs = [DIR1+d+'/' for d in DIR2]
for DIR in DIRs:
    for files in os.listdir(DIR):
        if files.endswith('.pickle') :
            [single_plotter(DIR1, DIR, filename) for filename in files.split("\n") if "uncorrected" not in filename]
        else:
            continue

plt.show()