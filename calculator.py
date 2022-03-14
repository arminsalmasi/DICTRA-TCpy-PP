import copy
import os
import pickle
import sys
from collections import defaultdict
from copy import deepcopy
from tkinter import Tk, filedialog
import numpy as np
from tc_python import *

def calculator(dir, settings):
    for timeflag in settings['timeflags']:
        print(">>>>>>>>> TCpy calculator in {} for {} tstp".format(dir,timeflag)) 
        with open(dir+'rawdata_{}.pickle'.format(timeflag), 'rb') as f:
            tS_VLUs = pickle.load(f)
        tS_VLUs['tc_setting'] = settings['tc_setting']
        tS_tc_VLUs = tccalc(tS_VLUs)  # todo : automatic alternating
        with open(dir+'uncorrected_results_{}.pickle'.format(timeflag), 'wb') as f:
            pickle.dump(tS_tc_VLUs, f)
##********************************************************************************************
def tccalc(dict_input):
    ''' Calculate single equilibrium pt by pt with input condition'''
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
        poly3Flag = dict['tc_setting']['p3flag']
        McalcFlag = dict['tc_setting']['mobFlag'] #temp flag for calcualtion of mobilities
    except:
        print('error in TC input data')
        sys.exit()
    else:
        print('calculating thermodynaics')
    with TCPython() as start:
        if poly3Flag and os.path.isfile('{}/p.POLY3'.format(pth)):
            poly = start.select_database_and_elements(database[0], elnames).get_system().with_single_equilibrium_calculation()
            poly.run_poly_command('read {}/p.POLY3'.format(pth))
            #poly.run_poly_command('list-status , cps, ')
            poly.remove_all_conditions()
            poly.set_condition('N', 1)
            poly.set_condition('P', 1e5)
            print('************read poly3 file, calculating')
        else:
            if McalcFlag: 
                if ("Fe" not in elnames ) and ("MOBFE" in database[1]):# ''' necessary to get mobilities from mobfe5
                    poly = start.set_cache_folder( "./_cache2").select_thermodynamic_and_kinetic_databases_with_elements(database[0],database[1], elnames).deselect_phase("CEMENTITE").get_system().with_single_equilibrium_calculation()
                else:
                    poly = start.set_cache_folder( "./_cache2").select_thermodynamic_and_kinetic_databases_with_elements(database[0],database[1], elnames).get_system().with_single_equilibrium_calculation()
                tc_M, tc_G = {},{}
            elif not McalcFlag:
                poly = start.set_cache_folder( "./_cache2").select_database_and_elements(database[0], elnames).get_system().with_single_equilibrium_calculation()
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
            for nel, el in enumerate(elnames):
                tc_acSER[el].append(pntEq.get_value_of('ac({})'.format(el)))
                tc_mus[el].append(pntEq.get_value_of('mu({})'.format(el)))
                tc_ws[el].append(pntEq.get_value_of('w({})'.format(el)))

            for ph in stablePhs:      
                tc_npms['{}, {}'.format(pt, ph)] = pntEq.get_value_of('npm({})'.format(ph))
                tc_vpvs['{}, {}'.format(pt, ph)] = pntEq.get_value_of('vpv({})'.format(ph))
                temp1 = []
                if McalcFlag: 
                    temp2, temp3 = [],[]
                    for el2 in elnames[:]:
                        temp2.append(pntEq.get_value_of('M({}, {})'.format(ph, el2))) 
                        temp3.append(pntEq.get_value_of('M({}, {})'.format(ph, el2))*pntEq.get_value_of('X({}, {})'.format(ph, el2)))
                    tc_M['{}, {}'.format(pt, ph)] = np.array(temp2) 
                    tc_G['{}, {}'.format(pt, ph)] = np.array(temp3) 
                for el2 in elnames[:]:
                    temp1.append(pntEq.get_value_of('X({}, {})'.format(ph, el2)))    
                tc_phXs['{}, {}'.format(pt, ph)] = np.array(temp1)
    #clear_output(wait = False)
    if McalcFlag: #temp
        dict['tS_TC_M'] = tc_M 
        dict['tS_TC_G'] = tc_G 
        tc_NEAT_G, tc_NEAT_M = {}, {}
    
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
        if McalcFlag: 
            tc_NEAT_G[ph] = np.zeros([n_pts, len(elnames)]) 
            tc_NEAT_M[ph] = np.zeros([n_pts, len(elnames)]) 
    
    for nph, ph in enumerate(tc_NEAT_phnames):
        for pt in range(n_pts):
            if '{}, {}'.format(str(pt), ph) in tc_npms:
                tc_NEAT_npms[ph][pt] = tc_npms['{}, {}'.format(str(pt), ph)]
                tc_NEAT_vpvs[ph][pt] = tc_vpvs['{}, {}'.format(str(pt), ph)]    
                for nel, el in enumerate(elnames):
                    tc_NEAT_phXs[ph][pt, nel] = tc_phXs['{}, {}'.format(str(pt), ph)][nel]
                    if McalcFlag: #temp
                        tc_NEAT_G[ph][pt, nel] = tc_G['{}, {}'.format(str(pt), ph)][nel] #temp
                        tc_NEAT_M[ph][pt, nel] = tc_M['{}, {}'.format(str(pt), ph)][nel] #temp

    dict['tS_TC_NEAT_phnames'] = tc_NEAT_phnames
    dict['tS_TC_NEAT_npms'] = tc_NEAT_npms
    dict['tS_TC_NEAT_vpvs'] = tc_NEAT_vpvs
    dict['tS_TC_NEAT_phXs'] = tc_NEAT_phXs
    dict['tS_TC_NEAT_mfs'] = tc_NEAT_mfs
    if McalcFlag:
        dict['tS_TC_NEAT_G'] = tc_NEAT_G  
        dict['tS_TC_NEAT_M'] = tc_NEAT_M  
    return dict

