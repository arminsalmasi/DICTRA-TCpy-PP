import copy
import os
import pickle
from tkinter import Tk, filedialog

import numpy as np
from tc_python import *
from copy import deepcopy



def data_reader(path,settings):
    #'''load TXT files and Setting'''
    rData = get_values_from_textfiles(path)    
    # '''get values of timesteps'''
    for timeflag in settings['timeflags']:
        VLUs = rData
        tS, nearestTime = get_timeStamp(VLUs['times'], timeflag)
        tS_VLUs = get_tS_VLUs(VLUs, tS, nearestTime)
        with open('rawdata_{}.pickle'.format(timeflag), 'wb') as f:
            pickle.dump(tS_VLUs, f)
#********************************************************************************************
def get_values_from_textfiles(*argv):
    '''Reads all values from a given path, 
    input:
        path(optional)
    output:dict{path, all_mfs, elnames, all_pts, times, n_pts, DICT_all_npms, 
                 DICT_phnames, DICT_all_mus, T, interstitials, substitutionals}
    '''
    data = {}
    if len(argv) == 1:
        data['path'] = argv[0]
        os.chdir(data['path'])
    else:
        data['path'] = get_path()
    #print('******** Reading DICTRA data from path:{}'.format(data['path']))
    print('>>>>>>> Reading DICTRA data from path:{}'.format(os.getcwd()))
    data['all_mfs'] = np.loadtxt('MOLE_FRACTIONS.TXT', dtype = float)
    data['elnames'] = np.loadtxt('EL_NAMES.TXT', dtype = str)
    data['all_pts'] = np.loadtxt('VOLUME_MIDPOINTS.TXT', dtype = float)
    data['times'] = np.loadtxt('TIME.TXT', dtype = float)
    data['n_pts'] = np.loadtxt('VOLUMES_PER_REGION.TXT', dtype = float)
    data['DICT_all_npms'] = np.loadtxt('PHASE_FRACTIONS.TXT', dtype = float)
    phnames = []
    with open('PH_NAMES.TXT', 'r')as f:
        for line in f:
            phnames.append(line.strip())
    data['DICT_phnames'] = np.array(phnames)
    data['DICT_all_mus'] = np.loadtxt('CHEMICAL_POTENTIALS.TXT', dtype = float)
    data['T'] = np.loadtxt('T.DAT', dtype = int)
    int_idx = []
    if 'N' in data['elnames']:
        Nidx = np.where(data['elnames']  ==  'N')[0]
        int_idx.append(Nidx[0])
    if 'C' in data['elnames']:
        Cidx = np.where(data['elnames']  ==  'C')[0]
        int_idx.append(Cidx[0])
    if 'H' in data['elnames']:
        Hidx = np.where(data['elnames']  ==  'H')[0]
        int_idx.append(Hidx[0])
    if 'O' in data['elnames']:
        Oidx = np.where(data['elnames']  ==  'O')[0]
        int_idx.append(Oidx[0])
    if 'VA' in data['elnames']:
        VAidx = np.where(data['elnames']  ==  'VA')[0]
        int_idx.append(VAidx[0])
    sub_idx = list(np.arange(len(data['elnames'])))
    data['interstitials'] = [data['elnames'][int_idx], int_idx]
    for idx in data['interstitials'][1]: 
        sub_idx.pop(idx)
    data['substitutionals'] = [data['elnames'][sub_idx], sub_idx]
    return data
#********************************************************************************************
def get_path():
    '''change path to the designated folder, root is users home
    output:
        path
    '''
    flag = True
    while flag:
        root = Tk() # pting root to Tk() to use it as Tk() in program.
        root.withdraw() # Hides small tkinter window.
        root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
        open_file = filedialog.askdirectory(initialdir = '~') # Returns opened path as str
        if open_file:
            flag = False
    os.chdir(open_file)
    return os.getcwd()
#********************************************************************************************
def get_timeStamp(times,timeflag):
    '''timeflag: 'first', 'last', number(float or int)'''
    if timeflag == "first":
        tS = 0
        nearestTime = times[1]
    elif timeflag == "last":
        tS = len(times)-1
        nearestTime = times[-1]
    elif (type(timeflag) == int or type(timeflag) == float) and timeflag>0 and timeflag <times[-1]:
        tS=timeflag
        _, nearestTime=find_nearest(times, tS)
    else:
        time1 = float(input('Time to plot/{}/timesteps/{}/:'.format(times[-1], len(times))))
        if time1>= 0 and time1 <= times[-1]:
            tS, nearestTime = find_nearest(times, time1)
    print('timeflag:{}, timestep:{}, nearest time:{}'.format(timeflag,tS,nearestTime))
    return tS, nearestTime
#********************************************************************************************                      
def find_nearest(array, value):
    '''output: index, nearest value'''
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]                      
#********************************************************************************************                      
def calculate_u_fractions(*argv):
    mf, sub_idx, elnames =  argv
    sub_sum = np.sum(mf[:, sub_idx], axis = 1)
    uf = []
    for nel, el in enumerate(elnames):
        uf.append(mf[:, nel]/sub_sum[:]) 
    return np.array(uf)
#********************************************************************************************
def get_tS_VLUs(dict_input, tS, nearestTime):
    '''get value of a given timestamp
    input: dict{all_values}, tS 
    output: dict{'tS_mfs', 'tS_DICT_npms', 'tS_DICT_mus', 'tS_pts', 'tS_DICT_phnames'}
    '''
    dict = copy.deepcopy(dict_input)
    if tS == 0:
        tS +=1
    dict['tS'] = tS
    dict['nearestTime'] = nearestTime
    mfs  = dict['all_mfs']
    elnames = dict['elnames']
    pts = dict['all_pts']
    n_pts  = dict['n_pts']
    npms = dict['DICT_all_npms']
    phnames = dict['DICT_phnames']
    mus = dict['DICT_all_mus']
    subs  = dict['substitutionals']   
    '''gets molefractions, chemicalpotentials, phasefractions, volumemidpts and time of the timeindex
    removes ZZDICT from phasenames, calculate u-fractions'''
    dict['tS_pts'] = pts[int(np.sum(n_pts[:tS-1])):int(np.sum(n_pts[:tS]))]*1e6    
    idx1 = int(np.sum(n_pts[:tS-1]))*int(len(phnames))
    idx2 = int(np.sum(n_pts[:tS]))*int(len(phnames))
    dict['tS_DICT_npms'] = npms[idx1:idx2].reshape((-1, int(len(phnames))))
    if 'ZZDICT_GHOST' in phnames[-1]:
        dict['tS_DICT_phnames'] = deepcopy(phnames[:-1])
    else:
        dict['tS_DICT_phnames'] = deepcopy(phnames)
    idx1 = int(np.sum(n_pts[:tS-1]))*len(elnames)
    idx2 = int(np.sum(n_pts[:tS]))*len(elnames)
    dict['tS_DICT_mfs'] = mfs[idx1:idx2].reshape((-1, len(elnames)))
    dict['tS_DICT_mus'] = mus[idx1:idx2].reshape((-1, len(elnames)))
    dict['tS_DICT_ufs'] = calculate_u_fractions(dict['tS_DICT_mfs'], subs[1], elnames).T 
    for key in ['all_mfs', 'all_pts', 'times', 'n_pts', 'DICT_all_npms' , 'DICT_phnames', 'DICT_all_mus']:
        dict.pop(key) 
    return dict
#********************************************************************************************