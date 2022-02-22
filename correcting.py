import copy
import json
import pickle
import sys

import numpy as np
from tc_python import *

from clibv2 import *  # %matplotlib qt#user_path = !eval echo ~$USER

#********************************************************************************************
def value_correction(DIR1, DIR2, tflags):
    for tflag in tflags:
        with open(DIR2+'/uncorrected_results_{}.pickle'.format(tflag), 'rb') as f:
            dict_in = pickle.load(f)
    
        with open(DIR1+'/name_pairs.json', 'rb') as f:
            setting = json.load(f)
            dict_in['name_pairs'] = setting['name_pairs']
            dict_in['phase_changes'] = setting['phase_changes']
    
        dict1 = correct_phase_indices(dict_in)
        dict2 = add_compSets(dict1)
        dict3 = phnameChange(dict2)
        dict_out = add_compSets_DICT(dict3)
        
        with open(DIR2+'results_{}.pickle'.format(tflag), 'wb') as f:
            pickle.dump(dict_out, f)
#********************************************************************************************
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