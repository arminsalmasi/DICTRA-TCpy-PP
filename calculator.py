import copy
import json
import os
import pickle
import sys
from collections import defaultdict
from copy import deepcopy
from tkinter import Tk, filedialog

import numpy as np
from IPython.display import clear_output
from tc_python import *

from clibv2 import *  # %matplotlib qt#user_path = !eval echo ~$USER


def calculator(DIR1, DIR2, timeflags):
    for timeflag in timeflags:
        #'''load TXT files and Setting'''
        VLUs = None
        VLUs = get_values_from_textfiles(DIR2)
        with open(DIR1+'setting.json') as f:
            setting = json.load(f)
        VLUs['phase_changes'], VLUs['tc_setting'], VLUs['name_pairs'] = \
            setting['phase_changes'], setting['tc_setting'], setting['name_pairs']
    # '''get values of timesteps'''
        tS, nearestTime = get_timeStamp(VLUs['times'], timeflag)
        tS_VLUs = get_tS_VLUs(VLUs, tS, nearestTime)
    #''' TC calculations of tS_VLUs'''
        tS_tc_VLUs0 = tccalc(tS_VLUs)  # todo : automatic alternating
        tS_tc_VLUs = value_correction_rutines(tS_tc_VLUs0)
    #'''dump to file'''
        with open('results_{}.pickle'.format(timeflag), 'wb') as f:
            pickle.dump(tS_tc_VLUs, f)
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
    print('path:{}'.format(data['path']))
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
    data['T'] = np.loadtxt('T.DAT', dtype = int)+273
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
    #uf_dict = {}
    uf = []
    for nel, el in enumerate(elnames):
        #uf_dict[el] = mf[:, nel]/sub_sum[:]
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
def tccalc(dict_input):
    ''' Calculate single equilibrium pt by pt with input condition
        input: dict{'path', 'elnames', 'T', 'interstitials', 'substitutionals', 
                    'tS', 'nearestTime', 'tS_pts', 'tS_DICT_npms', 
                    'tS_DICT_phnames', 'tS_mfs', 'tS_mus', 'tS_ufs', 
                    'xlim1', 'xlim2', 'phase_change', 'tc_Setting', 'name_paires'}
        output: dict{tS_TC_phnames, tS_TC_npms, tS_TC_vpvs, tS_TC_phXs, 
            tS_TC_acRef, tStmp_TC_acSER, tS_TC_mus, tS_TC_ws}
    '''
    try:
        dict = copy.deepcopy(dict_input)
        mfs = dict['tS_DICT_mfs']
        database = dict['tc_setting']['database']
        n_pts = len(dict['tS_pts'])
        phsToSus = dict['tc_setting']['phsToSus']
        acsRef = dict['tc_setting']['acRefs']
        T = dict['T']
        elnames = dict['elnames']
        pth = dict['path']
        p3flag = dict['tc_setting']['p3flag']
    except:
        print('error in TC input data')
        sys.exit()
    else:
        print('calculating thermodynaics')
    
    with TCPython() as start:
        if p3flag and os.path.isfile('{}/p.POLY3'.format(pth)):
            poly = start.select_database_and_elements(database, elnames).get_system().with_single_equilibrium_calculation()
            poly.run_poly_command('read {}/p.POLY3'.format(pth))
            #poly.run_poly_command('list-status , cps, ')
            poly.remove_all_conditions()
            poly.set_condition('N', 1)
            poly.set_condition('P', 1e5)
        else:
            print('read poly3 file, calculating')
            poly = start.set_cache_folder( "./_cache2").select_database_and_elements(database, elnames).get_system().with_single_equilibrium_calculation()
        if len(phsToSus)>0:
            for phase in phsToSus:
                poly.set_phase_to_suspended(phase)
        poly.set_condition("T", T)
        tc_phnames, tc_npms, tc_vpvs, tc_phXs = {}, {}, {}, {}
        tc_acRefs, tc_acSER, tc_mus, tc_ws = defaultdict(list), defaultdict(list), defaultdict(list), defaultdict(list)
        for pt in range(n_pts):
            for nel, el in enumerate(elnames[:-1]):
                poly.set_condition("X({})".format(el), mfs[pt, nel])
            pntEq = poly.calculate()
            stablePhs = pntEq.get_stable_phases()
            tc_phnames[pt] = stablePhs        
            if 'C' in elnames:
                for reference in acsRef:
                    tc_acRefs['ac(C, '+reference+')'].append(pntEq.get_value_of('ac(C, {})'.format(reference)))  
            for nel, el in enumerate(elnames[:]):
                tc_acSER[el].append(pntEq.get_value_of('ac({})'.format(el)))
                tc_mus[el].append(pntEq.get_value_of('mu({})'.format(el)))
                tc_ws[el].append(pntEq.get_value_of('w({})'.format(el)))
            for ph in stablePhs:      
                tc_npms['{}, {}'.format(pt, ph)] = pntEq.get_value_of('npm({})'.format(ph))
                tc_vpvs['{}, {}'.format(pt, ph)] = pntEq.get_value_of('vpv({})'.format(ph))
                temp1 = []
                for el2 in elnames[:]:
                    temp1.append(pntEq.get_value_of('X({}, {})'.format(ph, el2)))
                tc_phXs['{}, {}'.format(pt, ph)] = np.array(temp1)
    clear_output(wait = False)
    dict['tS_TC_phnames'] = tc_phnames
    dict['tS_TC_npms'] = tc_npms
    dict['tS_TC_vpvs'] = tc_vpvs
    dict['tS_TC_phXs'] = tc_phXs
    dict['tS_TC_acRef'] = tc_acRefs
    dict['tS_TC_acSER'] = tc_acSER
    dict['tS_TC_mus'] = tc_mus
    dict['tS_TC_ws'] = tc_ws
    ### trimming
    tc_NEAT_mfs, tc_NEAT_npms, tc_NEAT_vpvs, tc_NEAT_phXs = {}, {}, {}, {}
    tc_NEAT_phnames = []
    for nel, el in enumerate(elnames):
        tc_NEAT_mfs[el] = mfs[:, nel]
    for i in range(n_pts):
        for j in tc_phnames[i]:
               if j not in tc_NEAT_phnames:
                    tc_NEAT_phnames.append(j)
    for ph in tc_NEAT_phnames:
        tc_NEAT_npms[ph] = np.zeros([n_pts])
        tc_NEAT_vpvs[ph] = np.zeros([n_pts])
        tc_NEAT_phXs[ph] = np.zeros([n_pts, len(elnames)])
    for nph, ph in enumerate(tc_NEAT_phnames):
        for pt in range(n_pts):
            if '{}, {}'.format(str(pt), ph) in tc_npms:
                tc_NEAT_npms[ph][pt] = tc_npms['{}, {}'.format(str(pt), ph)]
                tc_NEAT_vpvs[ph][pt] = tc_vpvs['{}, {}'.format(str(pt), ph)]    
                for nel, el in enumerate(elnames):
                    tc_NEAT_phXs[ph][pt, nel] = tc_phXs['{}, {}'.format(str(pt), ph)][nel]
    dict['tS_TC_NEAT_phnames'] = tc_NEAT_phnames
    dict['tS_TC_NEAT_npms'] = tc_NEAT_npms
    dict['tS_TC_NEAT_vpvs'] = tc_NEAT_vpvs
    dict['tS_TC_NEAT_phXs'] = tc_NEAT_phXs
    dict['tS_TC_NEAT_mfs'] = tc_NEAT_mfs
    return dict
# #********************************************************************************************
def correct_phase_indices(dict_input):
    '''input:{'elnames', 'tS_TC_NEAT_phnames', 'tS_TC_NEAT_npms', 'tS_TC_NEAT_vpvs', 'tS_TC_NEAT_phXs} ''' 
    try: 
        dict = copy.deepcopy(dict_input)
        n_pts = len(dict['tS_pts']) 
        tS_TC_NEAT_npms = dict['tS_TC_NEAT_npms'] 
        tS_TC_NEAT_phXs = dict['tS_TC_NEAT_phXs'] 
        elnames = dict['elnames'] 
        nelements = len(elnames) 
        tS_TC_NEAT_phnames = dict['tS_TC_NEAT_phnames']
        phase_changes = dict['phase_changes'] 
    except:                     
        print('input error, correcting phase indices')
        sys.exit()    
    else:                       
        print('correcting indices')
    CQT_tS_TC_NEAT_phXs = copy.deepcopy(tS_TC_NEAT_phXs)
    CQT_tS_TC_NEAT_npms = copy.deepcopy(tS_TC_NEAT_npms)
    for change in phase_changes:
        phase_to_change, search_element, cutoff = change
        for phase in tS_TC_NEAT_phnames:
            if phase_to_change in phase:
                for pt in range(n_pts):
                    phXs = tS_TC_NEAT_phXs[phase][pt, :]
                    if any(phXs>0):
                        sorted_indices = np.flip(sorted(range(len(tS_TC_NEAT_phXs[phase][pt, :])), key = lambda k: tS_TC_NEAT_phXs[phase][pt, k]))                               
                        sorted_phXs = np.flip(sorted(tS_TC_NEAT_phXs[phase][pt, :]))
                        sorted_elnames = elnames[sorted_indices]
                        sorted_searchElidx = np.where( sorted_elnames ==  search_element )[0][0]
                        if cutoff > 0 and cutoff<1:
                            if sorted_phXs[sorted_searchElidx] >  cutoff:
                                    st = phase_to_change+'-'
                                    for nel, el in enumerate(sorted_elnames[:2]):
                                        st +=  el
                                    if st not in CQT_tS_TC_NEAT_npms:
                                        CQT_tS_TC_NEAT_phXs[st] = np.zeros((n_pts, nelements))
                                        CQT_tS_TC_NEAT_npms[st] = np.zeros(n_pts)
                                        CQT_tS_TC_NEAT_phXs[st][pt] = phXs
                                        CQT_tS_TC_NEAT_npms[st][pt] =  CQT_tS_TC_NEAT_npms[phase][pt]
                                        CQT_tS_TC_NEAT_phXs[phase][pt] = [0]*nelements 
                                        CQT_tS_TC_NEAT_npms[phase][pt] = 0
                                    else:
                                        CQT_tS_TC_NEAT_phXs[st][pt] = phXs
                                        CQT_tS_TC_NEAT_npms[st][pt] =  CQT_tS_TC_NEAT_npms[phase][pt]
                                        CQT_tS_TC_NEAT_phXs[phase][pt] = [0]*nelements 
                                        CQT_tS_TC_NEAT_npms[phase][pt] = 0
                        elif cutoff  ==  1:
                            if sorted_searchElidx == 0: #search element is tha largest constituent
                                if sorted_phXs[sorted_searchElidx] >0:
                                    st = phase_to_change+'-'
                                    for nel, el in enumerate(sorted_elnames[:1]):
                                        st +=  el
                                    if st not in CQT_tS_TC_NEAT_npms:
                                        CQT_tS_TC_NEAT_phXs[st] = np.zeros((n_pts, nelements))
                                        CQT_tS_TC_NEAT_npms[st] = np.zeros(n_pts)
                                        CQT_tS_TC_NEAT_phXs[st][pt, :] = phXs
                                        CQT_tS_TC_NEAT_npms[st][pt] =  CQT_tS_TC_NEAT_npms[phase][pt]
                                        CQT_tS_TC_NEAT_phXs[phase][pt] = [0]*nelements 
                                        CQT_tS_TC_NEAT_npms[phase][pt] = 0
    dict['CQT_tS_TC_NEAT_phXs'] = CQT_tS_TC_NEAT_phXs 
    dict['CQT_tS_TC_NEAT_npms'] = CQT_tS_TC_NEAT_npms
    klist=[]
    for k in  dict['CQT_tS_TC_NEAT_npms'].keys():
        if all(dict['CQT_tS_TC_NEAT_npms'][k]<1e-4):
            klist.append(k)
    for k in klist:
        dict['CQT_tS_TC_NEAT_npms'].pop(k)
    klist=[]
    for k in  dict['CQT_tS_TC_NEAT_phXs'].keys():
        if all(dict['CQT_tS_TC_NEAT_phXs'][k].ravel()==0):
            klist.append(k)
    for k in klist:
        dict['CQT_tS_TC_NEAT_phXs'].pop(k)        
    return dict
# #********************************************************************************************
def value_correction_rutines(dict_in):
    dict1 = correct_phase_indices(dict_in)
    dict2 = add_compSets(dict1)
    dict3 = phnameChange(dict2)
    dict_out = add_compSets_DICT(dict3)
    return(dict_out)
#********************************************************************************************
def add_compSets(dict_in):
    dict = copy.deepcopy(dict_in) 
    npms_dict = dict['CQT_tS_TC_NEAT_npms'] 
    keys = [key for key in npms_dict.keys()]
    phs_without_Csets  = []
    for key in keys:
        if '#1' in key:
            tmp = key.split('#')
            phs_without_Csets.append(tmp[0])
    for ph in phs_without_Csets:
        for i in np.arange(2, 10):
            for key in keys:
                 if key  ==  ph+'#{}'.format(i):
                    npms_dict[ph+'#1'] +=  npms_dict[ph+'#{}'.format(i)]
                    npms_dict.pop(ph+'#{}'.format(i))
    keys = [key for key in npms_dict.keys()]
    for i in np.arange(len(keys)):
        for j in np.arange(i, len(keys)):
             if sorted(keys[i])  ==  sorted(keys[j]):
                if keys[i] is not keys[j]:
                    npms_dict[keys[i]] +=  npms_dict[keys[j]]
                    npms_dict.pop(keys[j])
    dict['sum_CQT_tS_TC_NEAT_npms'] = npms_dict
    return dict
#********************************************************************************************
def phnameChange(dict_in):
    dict = copy.deepcopy(dict_in)
    name_pairs = dict['name_pairs']
    npms_dict = dict['CQT_tS_TC_NEAT_npms'] 
    for name in name_pairs:
        if name[0] in npms_dict.keys():
            if name[1] in npms_dict.keys(): 
                npms_dict[name[1]] += npms_dict[name[0]]
            else:
                npms_dict[name[1]] = npms_dict[name[0]]
            del npms_dict[name[0]]
    dict['nameChanged_CQT_tS_TC_NEAT_npms'] = npms_dict
    return dict
#********************************************************************************************
def add_compSets_DICT(dict_in):
    dict = copy.deepcopy(dict_in)
    npms = np.array(dict['tS_DICT_npms'])
    phnames = dict['tS_DICT_phnames'] 
    npms_dict = {}
    phnames_without_Csets  = []
    for ph in phnames:
        if '#' in ph:
            tmp = ph.split('#')
            if not(tmp[0] in phnames_without_Csets):
                phnames_without_Csets.append(tmp[0])
                npms_dict[tmp[0]] = np.zeros(npms.shape[0]) 
    for ph1 in phnames_without_Csets:
        for nph,ph2 in enumerate(phnames):
            if ph1 in ph2:
              npms_dict[ph1] += npms[:,nph]  
    dict['sum_tS_DICT_npms'] = npms_dict
    return dict  
