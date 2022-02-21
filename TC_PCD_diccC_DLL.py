import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq as find_root
from tc_python import *
import pandas as pd
from tkinter import Tk, filedialog, font
import tkinter as ttk
import os
from IPython.display import clear_output
from copy import deepcopy
import copy
from scipy.ndimage.filters import gaussian_filter1d
import glob
#from tkinter import simpledialog
#import pdb
import random
#********************************************************************************************
def tccalc_AllPHS(T, L, elnames, xplot):    
    with TCPython() as start:
        system = start.set_cache_folder( "./_cache2").select_database_and_elements("TCFE9", elnames).deselect_phase('graphite').get_system().with_single_equilibrium_calculation()
        system.set_condition("T", T)
        phase_lists_per_grid = {}
        phase_fraction_per_grid = {}
        x_phase_per_grid = {}
        output_1 = []
        acgraph=[]
        ac=[]
        for grid in range(len(L)):
            grid_values = {}
            for ie, el in enumerate(elnames[:-1]):
                system.set_condition("X({})".format(el), xplot[grid, ie])
            results = system.calculate()
            phases = results.get_stable_phases()
            print(phases)
            phase_lists_per_grid[str(int(grid))] = phases        
            #acgraph.append(results.get_value_of('ac(c,graph)'))
            acgraph.append(results.get_value_of('ac(c)'))
            actemp=np.zeros(len(elnames))
            for ie, el in enumerate(elnames[:]):
                   actemp[ie]=results.get_value_of('ac({})'.format(el))
            ac.append(actemp)
            for ph in phases:      
                phase_fraction_per_grid['{}, {}'.format(grid, ph)] = results.get_value_of('npm({})'.format(ph))
                allXel_ph_ingrid = []
                for iee, ell in enumerate(elnames[:]):
                    allXel_ph_ingrid.append(results.get_value_of('X({}, {})'.format(ph, ell)))
                x_phase_per_grid['{}, {}'.format(grid, ph)] = np.array(allXel_ph_ingrid)
                ordered_el_names = []
                ordered_el_comp = []
                maxindx = np.flip(np.argsort(np.array(allXel_ph_ingrid), axis = 0))
                for i in maxindx:
                    ordered_el_names.append(elnames[i])
                    ordered_el_comp.append(allXel_ph_ingrid[i])
                grid_values[ph] = [results.get_value_of('npm({})'.format(ph)), np.array(allXel_ph_ingrid), ordered_el_names, np.array(ordered_el_comp)]
            output_1.append(grid_values)
    clear_output(wait = False)
    return output_1, acgraph, np.array(ac)
#********************************************************************************************
def get_values(tmp1 = 1,temp2 = 2,temp3 = -1):
    '''Change to the desired path'''
    pth = change_path()
    '''Loading the data from txt files'''
    mfs, elnames, vmps, ts, vprs, npms, phnames, chem_pots = read_profiles()
    T = np.loadtxt('T.DAT', dtype = int)+273
    '''Selecting time steps'''
    tidx1 = tmp1
    tidx2 = len(ts)//temp2
    tidx3 = len(ts)+(temp3)
    '''geting values of selected time steps from Data'''
    mf1, npm1, chem_pot1, vmp1, phnames21, t1 = get_values_tindex(phnames, elnames, tidx1, npms, mfs, chem_pots, ts, vmps, vprs)
    mf2, npm2, chem_pot2, vmp2, phnames22, t2 = get_values_tindex(phnames, elnames, tidx2, npms, mfs, chem_pots, ts, vmps, vprs)
    mf3, npm3, chem_pot3, vmp3, phnames23, t3 = get_values_tindex(phnames, elnames, tidx3, npms, mfs, chem_pots, ts, vmps, vprs)
    '''Post processing with TC-python '''
    all_grid_values3,accgraph,acs_SER = tccalc_AllPHS(T, vmp3, elnames, mf3)
    '''Reading post processed data of a time index'''
    xph_pp, npm_pp, ph_names_pp, Lpp = get_tc_results_mf_npm_all_phases(all_grid_values3, tidx3, vmp3, elnames)
    print(ph_names_pp)
    clear_output(wait = False)
    '''Correcting phase indexes'''
    npm_pp_corrected, xph_pp_corrected = correct_phase_indexes(vmp3, xph_pp, npm_pp, elnames)
    '''summarize'''
    print(pth)
    print('{:1.2e}, {:1.2e}'.format(vmp1[0], vmp1[-1]))
    print('{:1.2e}, {:1.2e}'.format(vmp3[0], vmp3[-1]))
    print('Ldiff = {:1.2e}, {:1.2e}'.format(vmp3[0]-vmp1[0], vmp3[-1]-vmp1[-1] ))
    print('t1 = {:2.1e} sec,  t2 = {:2.1e} sec,  t3 = {:2.1e} sec'.format(t1, t2, t3))
    print('Temperature = {}C'.format(T-273))
    return pth, mfs, elnames, vmps, ts, vprs, npms, phnames, chem_pots, T, \
           tidx1, tidx2, tidx3, mf1, mf2, mf3 , npm1, npm2, npm3 , chem_pot1, chem_pot2, chem_pot3, \
           vmp1, vmp2, vmp3, phnames21, phnames22, phnames23, t1, t2, t3, \
           all_grid_values3, xph_pp, npm_pp, ph_names_pp, Lpp, npm_pp_corrected, xph_pp_corrected, accgraph, acs_SER
#********************************************************************************************
def get_lims_gui(vmp1,vmp2):
    master = ttk.Tk()
#     def get_entry_fields():
#         print("xlim1: %s\nxlim2: %s" % (e1.get(), e2.get()))    
    ttk.Label(master, text = "xlim1 min {:3.1f} or -1".format(min(vmp1[0],vmp2[0]))).grid(row = 0)
    ttk.Label(master, text = "xlim2 max {:3.1f} or -1".format(max(vmp1[-1],vmp2[-1]))).grid(row = 1)
    e1 = ttk.Entry(master)
    e2 = ttk.Entry(master)
    e1.grid(row = 0, column = 1)
    e2.grid(row = 1, column = 1)
    ttk.Button(master, text = 'OK', command = master.quit).grid(row = 3, column = 0, sticky = ttk.W, pady = 4)
    #tk.Button(master, text = 'Get', command = get_entry_fields).grid(row = 3, column = 1, sticky = tk.W, pady = 4)
    ttk.mainloop()
    master.withdraw()
    lim1 = int(e1.get())
    lim2 = int(e2.get())
    return lim1, lim2
#********************************************************************************************
def set_xlim(vmp1, vmp3, lim1 = -2, lim2 = -2):
    '''Setting plot xlimits, L < 0 : domain xlimits'''
    if lim1 != -2 and lim2 != -2:
        xlim1, xlim2 = lim1, lim2
    else:
        if   max(vmp1[-1], vmp3[-1]) > 700: xlim1, xlim2 = 350, 450
        elif max(vmp1[-1], vmp3[-1]) <= 400 and max(vmp1[-1], vmp3[-1]) >= 200 : xlim1, xlim2 = 150, 250
        elif max(vmp1[-1], vmp3[-1]) >= 250 and max(vmp1[-1], vmp3[-1]) <= 360 : xlim1, xlim2 = 280, max(vmp1[-1], vmp3[-1])
        elif max(vmp1[-1], vmp3[-1]) <= 150 and max(vmp1[-1], vmp3[-1]) >= 100 : xlim1, xlim2 = 80, max(vmp1[-1], vmp3[-1])
        elif max(vmp1[-1], vmp3[-1]) <= 100 : xlim1, xlim2 = 40, max(vmp1[-1], vmp3[-1])
        else : xlim1, xlim2 = -1, -1
    return xlim1, xlim2
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
def change_path():
    '''change path to the designated folder/ root is jupyters opening path'''
    flag = True
    while flag:
        root = Tk() # pointing root to Tk() to use it as Tk() in program.
        root.withdraw() # Hides small tkinter window.
        root.attributes('-topmost', True) # Opened windows will be active. above all windows despite of selection.
        #help(root)
        open_file = filedialog.askdirectory() # Returns opened path as str
        open_file
        if open_file:
            os.chdir(open_file)
            flag = False
    return os.getcwd()
#********************************************************************************************
def read_profiles():
    '''reads molefractions, volumemidpoints, timestamps, volumsperregion, 
    elementnames.phasenames, chemicalpotentials from path '''
    mfs = np.loadtxt('MOLE_FRACTIONS.TXT', dtype = float)
    elnames = np.loadtxt('EL_NAMES.TXT', dtype = str)
    vmps = np.loadtxt('VOLUME_MIDPOINTS.TXT', dtype = float)
    ts = np.loadtxt('TIME.TXT', dtype = float)
    vprs = np.loadtxt('VOLUMES_PER_REGION.TXT', dtype = float)
    npms = np.loadtxt('PHASE_FRACTIONS.TXT', dtype = float)
    phnames_DICTRA = []
    with open('PH_NAMES.TXT', 'r')as f:
        for line in f:
            phnames_DICTRA.append(line.strip())
    phnames_DICTRA = np.array(phnames_DICTRA)
    chem_pots = np.loadtxt('CHEMICAL_POTENTIALS.TXT', dtype = float)
    return mfs, elnames, vmps, ts, vprs, npms, phnames_DICTRA, chem_pots
#********************************************************************************************
def get_values_tindex(phnames, elnames, tindex, npms, mfs, chem_pots, ts, vmps, vprs):
    '''gets molefractions, chemicalpotentials, phasefractions, volumemidpoints and time of the timeindex
    removes ZZDICTRA from phasenames'''
    vmp = vmps[int(np.sum(vprs[:tindex])):int(np.sum(vprs[:tindex+1]))]*1e6    
    idx1 = int(np.sum(vprs[:tindex]))*int(len(phnames))
    idx2 = int(np.sum(vprs[:tindex+1]))*int(len(phnames))
    ph = npms[idx1:idx2].reshape((-1, int(len(phnames))))
    if 'ZZDICTRA_GHOST' in phnames[-1]:
        phnames2 = deepcopy(phnames[:-1])
    else:
        phnames2 = deepcopy(phnames)
    idx1 = int(np.sum(vprs[:tindex]))*len(elnames)
    idx2 = int(np.sum(vprs[:tindex+1]))*len(elnames)
    mf = mfs[idx1:idx2].reshape((-1, len(elnames)))
    chem_pots = chem_pots[idx1:idx2].reshape((-1, len(elnames)))
    return mf, ph[:, :len(phnames2)], chem_pots, vmp, phnames2, ts[tindex]
#********************************************************************************************
def get_tc_results_mf_npm_all_phases(data, t, L, elnames):
    '''grid point = data[n]
    phase names = data[n].keys() 
    phase fraction = data[n][keys][0]
    el fractions in phase = data[n][keys][1]
    ordered el names in phase = data[n][keys][2]
    ordered el fractions in phase = data[n][keys][3]'''
    ph_names = []
    for i in range(len(data)):
        keys = data[i].keys()
        for key in keys:
            if key not in ph_names:
                ph_names.append(key)
    npms = {}
    for ph in ph_names:
        npm = []
        grid_idx_holder = []
        for grid in range(len(data)):
            for phase in data[grid].keys():    
                if ph in phase:
                    grid_idx_holder.append(grid)
                    npm.append(data[grid][phase][0])
                    if ph in npms.keys():
                        npms[ph].append(data[grid][phase][0])
                    else:
                        npms.setdefault(ph, []).append(data[grid][phase][0])
    xph = {}
    for ph in ph_names:
        x = []
        grid_idx_holder = []
        for grid in range(len(data)):
            for phase in data[grid].keys():    
                if ph in phase:
                    grid_idx_holder.append(grid)
                    x.append(data[grid][phase][1])
        x = np.ravel(x).reshape((-1, len(elnames)))     
        xph[ph] = [L[grid_idx_holder], x]                       
    return xph, npms, ph_names, L[grid_idx_holder]
#********************************************************************************************
def all_x_plotter(names, L, tt, xs, lim1 = -10, lim2 = -10, title = '', file_name = 'all_values', ylab = "fractions"\
                  , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, wlsize=3):
    new_names=[]
    for name in names:
        if '_' in name:
            name = name.replace('_','\_')
        if '#' in name:
            name = name.replace('#','\#')
        name = '$'+name+'$'
        new_names.append(name)
    if lim1 < 0: lim1 = L[0]
    if lim2 < 0: lim2 = L[-1]
    plt.figure(figsize = [15, 10])
    for i, x in enumerate(names):
        #ysmoothed = gaussian_filter1d(xs[:, i], sigma = 0.1)
        plt.plot(L, xs[:, i], linewidth=wlsize)
        plt.legend(new_names, fontsize = lgsize)
    plt.title(title, fontsize = tsize)
    plt.xlabel('Distance [um]', fontsize = lsize)
    plt.ylabel(ylab, fontsize = lsize)
    plt.xticks(fontsize = tksize)
    plt.yticks(fontsize = tksize)
    plt.xlim([lim1, lim2])
    plt.savefig(file_name+'.png')
#********************************************************************************************
def plot_x_3ts(x1, x2, x3, L1, L2, L3, tt1, tt2, tt3, names, lim1 = -10, lim2 = -10, title = '', 
               file_name = '3ts', ylab = "fractions",  
               fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20):  
    if lim1 < 0: lim1 = min(L1[0], L2[0])
    if lim2 < 0: lim2 = max(L1[-1], L2[-1])
    if len(names)//2 > 1:
        if len(names)%2 == 1:
            fig1, ax1 = plt.subplots(len(names)//2+1, 2, figsize = [15, (len(names)//2+1)*25/5])
        else:
            fig1, ax1 = plt.subplots(len(names)//2, 2, figsize = [15, len(names)//2*25/5])
        ie = 0
        for el in names:
            ysmoothed = gaussian_filter1d(x1[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L1, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt1) )
            ysmoothed = gaussian_filter1d(x2[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L2, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt2) )
            ysmoothed = gaussian_filter1d(x3[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L3, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt3) )
            ax1[ie//2, ie%2].legend(fontsize = lgsize)
            ax1[ie//2, ie%2].set_title(el, fontsize = tsize)
            ax1[ie//2, ie%2].set_xlabel('Distance [um]', fontsize = lsize)
            ax1[ie//2, ie%2].set_ylabel(ylab, fontsize = lsize)
            ax1[ie//2, ie%2].tick_params(axis = "x", labelsize = tksize)
            ax1[ie//2, ie%2].tick_params(axis = "y", labelsize = tksize)
            ax1[ie//2, ie%2].set_xlim([lim1, lim2])
            ax1[ie//2, ie%2].locator_params(axis = 'y', nbins = bins)
            ax1[ie//2, ie%2].locator_params(axis = 'x', nbins = bins)
            ie += 1
        fig1.suptitle(title, fontsize = stsize)
        fig1.tight_layout()
        plt.savefig(file_name+'.png')
    else:
        fig1, ax1 = plt.subplots(len(names), 1, figsize = [15, len(names)*25/5])
        ie = 0
        for el in names:
            ysmoothed = gaussian_filter1d(x1[:, ie], sigma = 0.1)
            ax1[ie].plot(L1, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt1))
            ysmoothed = gaussian_filter1d(x2[:, ie], sigma = 0.1)
            ax1[ie].plot(L2, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt2))
            ysmoothed = gaussian_filter1d(x3[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L3, ysmoothed, '.-', label = 't = {:2.1e} sec'.format(tt3))
            ax1[ie].legend(fontsize = lgsize)
            ax1[ie].set_title(el, fontsize = tsize)
            ax1[ie].set_xlabel('Distance [um]', fontsize = lsize)
            ax1[ie].set_ylabel(' ', fontsize = lsize)
            ax1[ie].tick_params(axis = "x", labelsize = tksize) 
            ax1[ie].tick_params(axis = "y", labelsize = tksize)
            ax1[ie].locator_params(axis = 'y', nbins = bins)
            ax1[ie].locator_params(axis = 'x', nbins = bins)       
            ax1[ie].set_xlim([lim1, lim2])
            ie += 1   
        fig1.suptitle(title, fontsize = stsize)
        fig1.tight_layout()
        plt.savefig(title+'.png')
#********************************************************************************************
def plot_tc_corrected_results_phf_all_phases(npm, xph, t, TIM, L, lim1 = -10, lim2 = -10
                                             , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, lwsize=3, filename='NPM-corrected-postprocessed_'):
    if lim1 <= 0: lim1 = L[0]
    if lim2 <= 0: lim2 = L[-1]
    plt.figure(figsize = [15, 15])
    for ph in npm.keys():
        if len(npm[ph]) != 0:
            #ysmoothed = gaussian_filter1d(npm[ph], sigma = 0.1)
            plt.plot(xph[ph][0], npm[ph], linewidth=lwsize)
    plt.legend(npm.keys(), fontsize = lgsize)
    #plt.title(' Corrected NPM t = {:4.0f}sec, Post processed with all phases in the database'.format(TIM[t]), fontsize = 20)
    plt.xlabel(r'Distance ($\mu m$)', fontsize = lsize)
    plt.ylabel('Phase fraction', fontsize = lsize)
    plt.xticks(fontsize = tksize)
    plt.yticks(fontsize = tksize)
    plt.xlim([lim1, lim2])
    plt.savefig(filename+'-{:4.0f}-sec.png'.format(TIM[t]))
#********************************************************************************************
def plot_zero_padded_npm_corrected(Lx2, npm_pp_corrected, ttx2, lim1, lim2, L
                                   , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, lwsize=3, filename='NPM-zeroPadded-Corrected'):
    if lim1 <= 0: lim1 = L[0]
    if lim2 <= 0: lim2 = L[-1]
    r = np.zeros(len(Lx2)+1)
    for i in range(1, len(Lx2)+1):
        r[i] = (Lx2[i-1]-r[i-1])+Lx2[i-1]
    A = []
    for ph in npm_pp_corrected.keys():
        A.append(ph)
    plt.figure(figsize = [15, 10])
    for ph in A:
        vertices_npm = np.zeros(len(r))
        vertices_npm[0] = npm_pp_corrected[ph][0]
        for i in range(1, len(vertices_npm)-1):
                vertices_npm[i] = (npm_pp_corrected[ph][i]+npm_pp_corrected[ph][i-1])/2
        vertices_npm[-1] = npm_pp_corrected[ph][-1]
        ysmoothed = vertices_npm#gaussian_filter1d(vertices_npm, sigma = 0.1)
        plt.plot(r, ysmoothed, linewidth=lwsize)
    plt.legend(A, fontsize = lgsize)
    plt.xlabel(r'Distance ($\mu m$)', fontsize = lsize)
    plt.ylabel('Phase fraction', fontsize = lsize)
    plt.xticks(fontsize = tksize)
    plt.yticks(fontsize = tksize)
    plt.xlim([lim1, lim2])
    #plt.title('zero padded corrected Phase fraction t = {:2.1e} sec'.format(ttx2), fontsize = 20)
    plt.savefig(filename+'-{:4.0f}-sec.png'.format(ttx2))
#********************************************************************************************
def plot_x_3ts_log10(x1, x2, x3, L1, L2, L3, tt1, tt2, tt3, names, lim1 = -10, lim2 = -10, title = '', 
               file_name = '3ts', ylab = "fractions",  fsize = 20, lsize = 20, tsize = 20, bins = 6, 
               tksize = 20, stsize=20, lgsize=20, lwsize=3):
    params = {'text.usetex': True}
    plt.rcParams.update(params)
    
    if lim1 < 0: lim1 = min(L1[0], L2[0])
    if lim2 < 0: lim2 = max(L1[-1], L2[-1])
    if len(names)//2 > 1:
        if len(names)%2 == 1:
            fig1, ax1 = plt.subplots(len(names)//2+1, 2, figsize = [15, (len(names)//2+1)*25/5])
        else:
            fig1, ax1 = plt.subplots(len(names)//2, 2, figsize = [15, len(names)//2*25/5])
        ie = 0
        for el in names:
            ax1[ie//2, ie%2].plot(L1, -1*np.log10(np.abs(x1[:, ie])), label = 't = {:4.0f} sec'.format(tt1) , linewidth=lwsize)
            ax1[ie//2, ie%2].plot(L2, -1*np.log10(np.abs(x2[:, ie])), label = 't = {:4.0f} sec'.format(tt2) , linewidth=lwsize)
            ax1[ie//2, ie%2].plot(L3, -1*np.log10(np.abs(x3[:, ie])), label = 't = {:4.0f} sec'.format(tt3) , linewidth=lwsize)
            ax1[ie//2, ie%2].legend(fontsize = lgsize)
            ax1[ie//2, ie%2].set_title(el, fontsize = tsize)
            ax1[ie//2, ie%2].set_xlabel(r'Distance ($\mu m$)', fontsize = lsize)
            ax1[ie//2, ie%2].set_ylabel(ylab, fontsize = lsize)
            ax1[ie//2, ie%2].tick_params(axis = "x", labelsize = tksize)
            ax1[ie//2, ie%2].tick_params(axis = "y", labelsize = tksize)
            ax1[ie//2, ie%2].set_xlim([lim1, lim2])
            ax1[ie//2, ie%2].locator_params(axis = 'y', nbins = bins)
            ax1[ie//2, ie%2].locator_params(axis = 'x', nbins = bins)
            ie += 1
        fig1.suptitle(title, fontsize = stsize)
        fig1.tight_layout()
        plt.savefig(file_name+'.png')
    else:
        fig1, ax1 = plt.subplots(len(names), 1, figsize = [15, len(names)*25/5])
        ie = 0
        for el in names:
            ax1[ie].plot(L1, -1*np.log10(np.abs(x1[:, ie])), label = 't = {:4.0f} sec'.format(tt1), linewidth=lwsize)
            ax1[ie].plot(L2, -1*np.log10(np.abs(x2[:, ie])), label = 't = {:4.0f} sec'.format(tt2), linewidth=lwsize)
            ax1[ie].plot(L3, -1*np.log10(np.abs(x3[:, ie])), label = 't = {:4.0f} sec'.format(tt3), linewidth=lwsize)
            ax1[ie].legend(fontsize = lgsize)
            ax1[ie].set_title(el, fontsize = tsize)
            ax1[ie].set_xlabel(r'Distance ($\mu m$) ', fontsize = lsize)
            ax1[ie].set_ylabel(' ', fontsize = lsize)
            ax1[ie].tick_params(axis = "x", labelsize = tksize) 
            ax1[ie].tick_params(axis = "y", labelsize = tksize)
            ax1[ie].locator_params(axis = 'y', nbins = bins)
            ax1[ie].locator_params(axis = 'x', nbins = bins)       
            ax1[ie].set_xlim([lim1, lim2])
            ie += 1   
        fig1.suptitle(title, fontsize = stsize)
        fig1.tight_layout()
        plt.savefig(file_name+'.png')       
#********************************************************************************************      
def all_x_plotter_log10(names, L, tt, xs, lim1 = -10, lim2 = -10, title = '', file_name = 'all_values', ylab = "fractions"\
                  , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, wlsize=3):
    
    if lim1 < 0: lim1 = L[0]
    if lim2 < 0: lim2 = L[-1]
    plt.figure(figsize = [15, 10])
    for i, x in enumerate(names):
        #ysmoothed = gaussian_filter1d(xs[:, i], sigma = 0.1)
        plt.plot(L, np.log10(xs[:, i]), linewidth=wlsize)
        plt.legend(names, fontsize = lgsize)
    plt.title(title, fontsize = tsize)
    plt.xlabel('Distance [um]', fontsize = lsize)
    plt.ylabel(ylab, fontsize = lsize)
    plt.xticks(fontsize = tksize)
    plt.yticks(fontsize = tksize)
    plt.xlim([lim1, lim2])
    plt.savefig(file_name+'.png')   
#********************************************************************************************
def plot_tc_results_xphf_phases(xph, allnpm, t, elnames, ph_names, L, lim1 = -10, lim2 = -10
                                , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20):
    '''grid point = data[n]
    phase names = data[n].keys() 
    phase fraction = data[n][keys][0]
    el fractions in phase = data[n][keys][1]
    ordered el names in phase = data[n][keys][2]
    ordered el fractions in phase = data[n][keys][3]'''
    params = {'text.usetex': False}
    plt.rcParams.update(params)
    if lim1 <= 0: lim1 = L[0]
    if lim2 <= 0: lim2 = L[-1]
    if len(ph_names)//2 > 1:
        if len(ph_names)%2 == 1:
            fig1, ax1 = plt.subplots(len(ph_names)//2+1, 2, figsize = [15, (len(ph_names)//2+1)*25/5])
        else:
            fig1, ax1 = plt.subplots(len(ph_names)//2, 2, figsize = [15, len(ph_names)//2*25/5])
        iph = 0
        for iph,ph in enumerate(ph_names):  
            for ie, el in enumerate(elnames):  
                ax1[iph//2, iph%2].plot(xph[ph][0], xph[ph][1][:, ie]*np.array(allnpm[ph]), 'o-', label = el)
            ax1[iph//2, iph%2].plot(xph[ph][0], allnpm[ph], 'silver', marker = 'd', label = 'npm {}'.format(ph))
            ax1[iph//2, iph%2].legend(fontsize = lgsize)
            ax1[iph//2, iph%2].set_title('X in {} t = {:2.1e}sec'.format(ph, t), fontsize = tsize)
            ax1[iph//2, iph%2].set_xlabel('Distance [um]', fontsize = lsize)
            ax1[iph//2, iph%2].set_ylabel('Fraction', fontsize = lsize)
            ax1[iph//2, iph%2].tick_params(axis = "x", labelsize = tksize) 
            ax1[iph//2, iph%2].tick_params(axis = "y", labelsize = tksize)
            ax1[iph//2, iph%2].locator_params(axis = 'y', nbins = bins)
            ax1[iph//2, iph%2].locator_params(axis = 'x', nbins = bins)
            ax1[iph//2, iph%2].set_xlim([lim1, lim2])
            iph += 1
        fig1.tight_layout()
        plt.savefig('XinPh-postprocessed-{:.0f}-sec.png'.format(t))  
    elif len(new_ph_names) == 1:
        ph = ph_names[0]
        plt.figure(figsize = [15, len(ph_names)*25/5])
        for ie, el in enumerate(elnames):
            plt.plot(xph[ph][0], xph[ph][1][:, ie]*np.array(allnpm[ph]), 'o-', label = el)
        plt.plot(xph[ph][0], allnpm[ph], 'silver', marker = 'd', label = 'npm {}'.format(ph))
        plt.legend(fontsize = lgsize)        
        plt.title('xs in {} t = {:2.1e}sec'.format(ph, TIM[t]), fontsize = tsize)
        plt.xlabel('Distance [um]', fontsize = lsize)
        plt.ylabel('Fractions', fontsize = lsize)
        plt.tick_params(axis = "x", labelsize = tksize) 
        plt.tick_params(axis = "y", labelsize = tksize)
        plt.locator_params(axis = 'y', nbins = bins)
        plt.locator_params(axis = 'x', nbins = bins)
        plt.xlim([lim1, lim2])
    else:
        iph = 0
        fig1, ax1 = plt.subplots(len(ph_names), 1, figsize = [15, len(ph_names)*25/5])
        for iph,ph in enumerate(ph_names):
            for ie, el in enumerate(elnames):
                ax1[iph].plot(xph[ph][0], xph[ph][1][:, ie]*np.array(allnpm[ph]), 'o-', label = el)
            ax1[iph].plot(xph[ph][0], allnpm[ph][1], 'silver', marker = 'd', label = 'npm {}'.format(ph))
            ax1[iph].legend(fontsize = lgsize)            
            ax1[iph].set_title('xs in {} t = {:2.1e}sec'.format(ph, t), fontsize = tsize)
            ax1[iph].set_xlabel('Distance [um]', fontsize = lsize)
            ax1[iph].set_ylabel('Fractions', fontsize = lsize)
            ax1[iph].tick_params(axis = "x", labelsize = tksize) 
            ax1[iph].tick_params(axis = "y", labelsize = tksize)
            ax1[iph].locator_params(axis = 'y', nbins = bins)
            ax1[iph].locator_params(axis = 'x', nbins = bins)
            ax1[iph].set_xlim([lim1, lim2])
            iph += 1
        fig1.tight_layout()
        plt.savefig('XinPh-postprocessed-{:4.0f}-sec.png'.format(t))        
#********************************************************************************************        
def plot_allx_2ts(x1, x2, L1, L2, tt1, tt2, names, lim1 = -10, lim2 = -10, title = '', file_name = '', fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, lwsize=20):
    NUM_COLORS = len(names)*2
    r = list(range(NUM_COLORS))
    random.shuffle(r)
    cm = plt.get_cmap('gist_rainbow')
    fig = plt.figure(figsize = [15, 10])
    ax = fig.add_subplot(111)
    ax.set_prop_cycle('color', [cm(1.*i/NUM_COLORS) for i in r])

    if lim1 < 0: lim1 = min(L1[0], L2[0])
    if lim2 < 0: lim2 = max(L1[-1], L2[-1])
    ie = 0
    for el in names:
        ax.plot(L1, x1[:, ie], linewidth=lwsize, label = '{}, {:.0f} sec'.format(el,tt2) )
        ax.plot(L2, x2[:, ie],'--', linewidth=lwsize, label = '{}, {:.0f} sec'.format(el,tt1) )
        ax.set_xlabel('Distance [um]', fontsize = lsize)
        ax.set_ylabel('Mole Fractions', fontsize = lsize)
        ax.tick_params(axis = "x", labelsize = tksize)
        ax.tick_params(axis = "y", labelsize = tksize)
        ax.set_xlim([lim1, lim2])
        ax.locator_params(axis = 'y', nbins = bins)
        ax.locator_params(axis = 'x', nbins = bins)
        ie += 1
    ax.legend(fontsize = lgsize)
    plt.savefig(file_name+'.png')
#********************************************************************************************
def correct_phase_indexes(Lx2, xph_pp, npm_pp, el_names2):
    '''Correcting WBCC'''
    def change_phase_based_on_major_element(xph_pp_corrected, ph, el_index, name_string, flag):
        xW = xph_pp_corrected[ph][1][:, el_index]
        xMax = np.max(xph_pp_corrected[ph][1], axis = 1)
        if any(xW >= xMax):
            xph_pp_corrected[name_string] = [[], []]
            npm_pp_corrected[name_string] = [[], []]
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
        if name_string in xph_pp_corrected.keys():    
            for gr in range(len(npm_pp_corrected[ph])):
                if xph_pp_corrected[ph][1][gr, -1] >= max(xph_pp_corrected[ph][1][gr, :]):
                    grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                    gr_keeper.append(gr)
                    L_keeper.append(xph_pp_corrected[ph][0][gr])            
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]            
            xph_pp_corrected[name_string][0] = xph_pp_corrected[ph][0][gr_keeper]
            xph_pp_corrected[name_string][1] = xph_pp_corrected[ph][1][gr_keeper, :]
            npm_pp_corrected[name_string][:] = npm_pp_corrected[ph][gr_keeper]
            xph_pp_corrected[name_string][0] = tmp3
            xph_pp_corrected[name_string][1] = tmp2
            npm_pp_corrected[name_string][:] = tmp1
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)
            flag = False
        return flag, npm_pp_corrected, xph_pp_corrected
    xph_pp_corrected = copy.deepcopy(xph_pp)
    npm_pp_corrected = copy.deepcopy(npm_pp)    
    for ph in xph_pp_corrected.keys():
        A = npm_pp_corrected[ph]
        npm_pp_corrected[ph] = np.array(A)
    BCCs = []
    for ph in xph_pp_corrected.keys():
        if ('BCC' in ph) and not(ph in(BCCs)):
            BCCs.append(ph)
    FCCs = []
    for ph in xph_pp_corrected.keys():
        if ('FCC' in ph) and not(ph in(BCCs) and not('DIAMOND'in ph) ):
            FCCs.append(ph)
    if len(BCCs) > 0:
        flag = True
        for ph in BCCs:
            xW = xph_pp_corrected[ph][1][:, -1]
            xMax = np.max(xph_pp_corrected[ph][1], axis = 1)
            if any(xW >= xMax):
                xph_pp_corrected[r'W(BCC)'] = [[], []]
                npm_pp_corrected[r'W(BCC)'] = [[], []]
                npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            if 'W(BCC)' in xph_pp_corrected.keys():    
                for gr in range(len(npm_pp_corrected[ph])):
                    if xph_pp_corrected[ph][1][gr, -1] >= max(xph_pp_corrected[ph][1][gr, :]):
                        grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                        gr_keeper.append(gr)
                        L_keeper.append(xph_pp_corrected[ph][0][gr])            
                tmp1 = np.zeros(len(Lx2))
                tmp3 = Lx2
                tmp2 = np.zeros((len(Lx2), len(el_names2)))
                tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
                tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
                tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]            
                xph_pp_corrected[r'W(BCC)'][0] = xph_pp_corrected[ph][0][gr_keeper]
                xph_pp_corrected[r'W(BCC)'][1] = xph_pp_corrected[ph][1][gr_keeper, :]
                npm_pp_corrected[r'W(BCC)'][:] = npm_pp_corrected[ph][gr_keeper]
                xph_pp_corrected[r'W(BCC)'][0] = tmp3
                xph_pp_corrected[r'W(BCC)'][1] = tmp2
                npm_pp_corrected[r'W(BCC)'][:] = tmp1
                np.delete(npm_pp_corrected[ph], gr_keeper)
                np.delete(xph_pp_corrected[ph][0], gr_keeper)
                np.delete(xph_pp_corrected[ph][1], gr_keeper)
                flag = False
            if not(flag): break
    if len(BCCs) > 0:
        flag = True
        for ph in BCCs:
            xTi = xph_pp_corrected[ph][1][:, 3]
            xMax = np.max(xph_pp_corrected[ph][1], axis = 1)
            if any(xTi >= xMax):
                xph_pp_corrected[r'Ti55'] = [[], []]
                npm_pp_corrected[r'Ti55'] = []
                npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            if 'Ti55' in xph_pp_corrected.keys():
                for gr in range(len(npm_pp_corrected[ph])):
                    if xph_pp_corrected[ph][1][gr, 3] >= max(xph_pp_corrected[ph][1][gr, :]):
                        grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                        gr_keeper.append(gr)
                        L_keeper.append(xph_pp_corrected[ph][0][gr])                    
                tmp1 = np.zeros(len(Lx2))
                tmp3 = Lx2
                tmp2 = np.zeros((len(Lx2), len(el_names2)))
                tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
                tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
                tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                                  
                xph_pp_corrected[r'Ti55'][0] = tmp3
                xph_pp_corrected[r'Ti55'][1] = tmp2
                npm_pp_corrected[r'Ti55'][:] = tmp1            
                np.delete(npm_pp_corrected[ph], gr_keeper)
                np.delete(xph_pp_corrected[ph][0], gr_keeper)
                np.delete(xph_pp_corrected[ph][1], gr_keeper)
                flag = False
            if not(flag): break
    if len(FCCs) > 0:
        flag = True
        for ph in FCCs:
            xCo = xph_pp_corrected[ph][1][:, 2]
            xMax = np.max(xph_pp_corrected[ph][1], axis = 1)
            if any(xCo >= xMax):
                xph_pp_corrected[r'Binder'] = [[], []]
                npm_pp_corrected[r'Binder'] = []
                npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            if 'Binder' in xph_pp_corrected.keys():
                for gr in range(len(npm_pp_corrected[ph])):
                    if xph_pp_corrected[ph][1][gr, 2] >= max(xph_pp_corrected[ph][1][gr, :]):
                        grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                        gr_keeper.append(gr)
                        L_keeper.append(xph_pp_corrected[ph][0][gr])            
                tmp1 = np.zeros(len(Lx2))
                tmp3 = Lx2
                tmp2 = np.zeros((len(Lx2), len(el_names2)))
                tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
                tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
                tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                        
                xph_pp_corrected[r'Binder'][0] = tmp3
                xph_pp_corrected[r'Binder'][1] = tmp2
                npm_pp_corrected[r'Binder'][:] = tmp1            
                np.delete(npm_pp_corrected[ph], gr_keeper)
                np.delete(xph_pp_corrected[ph][0], gr_keeper)
                np.delete(xph_pp_corrected[ph][1], gr_keeper)
                flag = False
            if not(flag): break
    if len(FCCs) > 0:        
        flag = True
        for ph in FCCs:
            xCo = xph_pp_corrected[ph][1][:, 3]
            xMax = np.max(xph_pp_corrected[ph][1], axis = 1)
            if any(xCo >= xMax):
                xph_pp_corrected[r'TiC'] = [[], []]
                npm_pp_corrected[r'TiC'] = []
                npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            if 'TiC' in xph_pp_corrected.keys():
                for gr in range(len(npm_pp_corrected[ph])):
                    if xph_pp_corrected[ph][1][gr, 3] >= max(xph_pp_corrected[ph][1][gr, :]):
                        grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                        gr_keeper.append(gr)
                        L_keeper.append(xph_pp_corrected[ph][0][gr])                        
                tmp1 = np.zeros(len(Lx2))
                tmp3 = Lx2
                tmp2 = np.zeros((len(Lx2), len(el_names2)))
                tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
                tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
                tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
                xph_pp_corrected[r'TiC'][0] = tmp3
                xph_pp_corrected[r'TiC'][1] = tmp2
                npm_pp_corrected[r'TiC'][:] = tmp1            
                np.delete(npm_pp_corrected[ph], gr_keeper)
                np.delete(xph_pp_corrected[ph][0], gr_keeper)
                np.delete(xph_pp_corrected[ph][1], gr_keeper)                    
                flag = False
            if not(flag): break
    '''Key change'''
    A = []
    for ph in xph_pp_corrected.keys():
        A.append(ph)
    for ph in A:
        if len(npm_pp_corrected[ph]) == 0:
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]      
        if 'FCC_A' in ph or 'BCC_A' in ph:
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]         
    for ph in A:
        if 'MC_SHP' in ph:
            xph_pp_corrected['WC'] = [[], []]
            npm_pp_corrected['WC'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected['WC'][0] = tmp3
            xph_pp_corrected['WC'][1] = tmp2
            npm_pp_corrected['WC'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]
        if 'LIQ' in ph:
            xph_pp_corrected[r'Liquid binder'] = [[], []]
            npm_pp_corrected[r'Liquid binder'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'Liquid binder'][0] = tmp3
            xph_pp_corrected[r'Liquid binder'][1] = tmp2
            npm_pp_corrected[r'Liquid binder'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]      
        if 'M12C' in ph:
            xph_pp_corrected[r'M12C $\eta$'] = [[], []]
            npm_pp_corrected[r'M12C $\eta$'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'M12C $\eta$'][0] = tmp3
            xph_pp_corrected[r'M12C $\eta$'][1] = tmp2
            npm_pp_corrected[r'M12C $\eta$'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]
        if 'M6C' in ph:
            xph_pp_corrected[r'M6C $\eta$'] = [[], []]
            npm_pp_corrected[r'M6C $\eta$'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'M6C $\eta$'][0] = tmp3
            xph_pp_corrected[r'M6C $\eta$'][1] = tmp2
            npm_pp_corrected[r'M6C $\eta$'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]
        if 'HCP' in ph:
            xph_pp_corrected[r'Ti $\beta$ HCP'] = [[], []]
            npm_pp_corrected[r'Ti $\beta$ HCP'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'Ti $\beta$ HCP'][0] = tmp3
            xph_pp_corrected[r'Ti $\beta$ HCP'][1] = tmp2
            npm_pp_corrected[r'Ti $\beta$ HCP'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]    
        if 'MU_PHASE' in ph:
            xph_pp_corrected[r'CoW $\mu$'] = [[], []]
            npm_pp_corrected[r'CoW $\mu$'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'CoW $\mu$'][0] = tmp3
            xph_pp_corrected[r'CoW $\mu$'][1] = tmp2
            npm_pp_corrected[r'CoW $\mu$'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph]    
        if 'G_PHASE' in ph:
            xph_pp_corrected[r'AlTi $G$'] = [[], []]
            npm_pp_corrected[r'AlTi $G$'] = []
            npm_tmp, xph_0_tmp, xph_1_tmp, grIndex_keeper, gr_keeper, L_keeper = [], [], [], [], [], []
            for gr in range(len(npm_pp_corrected[ph])):
                grIndex_keeper.append(np.where(Lx2 == xph_pp_corrected[ph][0][gr])[0][0])
                gr_keeper.append(gr)
                L_keeper.append(xph_pp_corrected[ph][0][gr])                        
            tmp1 = np.zeros(len(Lx2))
            tmp3 = Lx2
            tmp2 = np.zeros((len(Lx2), len(el_names2)))
            tmp1[grIndex_keeper] = npm_pp_corrected[ph][gr_keeper]
            tmp2[grIndex_keeper, :] = xph_pp_corrected[ph][1][gr_keeper, :]
            tmp3[grIndex_keeper] = xph_pp_corrected[ph][0][gr_keeper]                                       
            xph_pp_corrected[r'AlTi $G$'][0] = tmp3
            xph_pp_corrected[r'AlTi $G$'][1] = tmp2
            npm_pp_corrected[r'AlTi $G$'][:] = tmp1            
            np.delete(npm_pp_corrected[ph], gr_keeper)
            np.delete(xph_pp_corrected[ph][0], gr_keeper)
            np.delete(xph_pp_corrected[ph][1], gr_keeper)            
            del npm_pp_corrected[ph]
            del xph_pp_corrected[ph] 
    return npm_pp_corrected, xph_pp_corrected

#********************************************************************************************
#********************************************************************************************    
### UNUSED    
#********************************************************************************************
#********************************************************************************************
def plot_x_2ts(x1, x2, L1, L2, tt1, tt2, names, lim1 = -10, lim2 = -10, title = ''
               , file_name='', fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, lwsize=20):
    if lim1 < 0: lim1 = min(L1[0], L2[0])
    if lim2 < 0: lim2 = max(L1[-1], L2[-1])
    if len(names)//2 > 1:
        if len(names)%2 == 1:
            fig1, ax1 = plt.subplots(len(names)//2+1, 2, figsize = [15, (len(names)//2+1)*25/5])
        else:
            fig1, ax1 = plt.subplots(len(names)//2, 2, figsize = [15, len(names)//2*25/5])
        ie = 0
        for el in names:
            ysmoothed = gaussian_filter1d(x1[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L1, ysmoothed, '.-', label = 't = {:.0f} sec'.format(tt1) )
            ysmoothed = gaussian_filter1d(x2[:, ie], sigma = 0.1)
            ax1[ie//2, ie%2].plot(L2, ysmoothed, '.-', label = 't = {:.0f} sec'.format(tt2) )
            ax1[ie//2, ie%2].legend(fontsize = lgsize)
            ax1[ie//2, ie%2].set_title(el, fontsize = 20)
            ax1[ie//2, ie%2].set_xlabel('Distance [um]', fontsize = lsize)
            ax1[ie//2, ie%2].set_ylabel('Fractions', fontsize = lsize)
            ax1[ie//2, ie%2].tick_params(axis = "x", labelsize = tksize)
            ax1[ie//2, ie%2].tick_params(axis = "y", labelsize = tksize)
            ax1[ie//2, ie%2].set_xlim([lim1, lim2])
            ax1[ie//2, ie%2].locator_params(axis = 'y', nbins = bins)
            ax1[ie//2, ie%2].locator_params(axis = 'x', nbins = bins)
            ie += 1
        fig1.suptitle(title, fontsize = 20)
        plt.savefig(file_name+'.png')
    else:
        fig1, ax1 = plt.subplots(len(names), 1, figsize = [15, len(names)*25/5])
        ie = 0
        for el in names:
            ysmoothed = gaussian_filter1d(x1[:, ie], sigma = 0.1)
            ax1[ie].plot(L1, ysmoothed, '.-', label = 't = {:.0f} sec'.format(tt1) )
            ysmoothed = gaussian_filter1d(x2[:, ie], sigma = 0.1)
            ax1[ie].plot(L2, ysmoothed, '.-', label = 't = {:.0f} sec'.format(tt2) )
            ax1[ie].legend(fontsize = lgsize)
            ax1[ie].set_title(el, fontsize = 20)
            ax1[ie].set_xlabel('Distance [um]', fontsize = 20)
            ax1[ie].set_ylabel('Fraction', fontsize = 20)
            ax1[ie].tick_params(axis = "x", labelsize = tksize) 
            ax1[ie].tick_params(axis = "y", labelsize = tksize)
            ax1[ie].locator_params(axis = 'y', nbins = bins)
            ax1[ie].locator_params(axis = 'x', nbins = bins)       
            ax1[ie].set_xlim([lim1, lim2])
            ie += 1  
        fig1.suptitle(title, fontsize = 20)
        plt.savefig(file_name +'.png')
#********************************************************************************************
def plot_tc_results_phf_all_phases(data, t, L, TIM, elnames, lim1 = -10, lim2 = -10
                                   , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, filename=''):
    '''grid point = data[n]
    phase names = data[n].keys() 
    phase fraction = data[n][keys][0]
    el fractions in phase = data[n][keys][1]
    ordered el names in phase = data[n][keys][2]
    ordered el fractions in phase = data[n][keys][3]'''
    if lim1 <= 0: lim1 = L[0]
    if lim2 <= 0: lim2 = L[-1]
    ph_names = []
    for i in range(len(data)):
        keys = data[i].keys()
        for key in keys:
            if key not in ph_names:
                ph_names.append(key)
    plt.figure(figsize = [15, 10])
    npms = {}
    for ph in ph_names:
        npm = []
        grid_idx_holder = []
        for grid in range(len(data)):
            for phase in data[grid].keys():    
                if ph in phase:
                    grid_idx_holder.append(grid)
                    npm.append(data[grid][phase][0])
                    if ph in npms.keys():
                        npms[ph].append(data[grid][phase][0])
                    else:
                        npms.setdefault(ph, []).append(data[grid][phase][0])
        ysmoothed = gaussian_filter1d(npm, sigma = 0.1)
        plt.plot(L[grid_idx_holder], ysmoothed, '.-')
        plt.legend(ph_names, fontsize = lgsize)
        plt.title(' NPM t = {:2.1e} sec, Post processed, all phases'.format(TIM[t]), fontsize = 20)
        plt.xlabel('Distance [um]', fontsize = 20)
        plt.ylabel('Fractions', fontsize = 20)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        plt.xlim([lim1, lim2])
        plt.savefig('NPM_postprocessed-{:.0f}-sec.png'.format(TIM[t]))
    return npms, ph_names, L[grid_idx_holder]
#********************************************************************************************
def plot_tc_results_xphf_phases_scaled(data, t, L, TIM, elnames, lim1 = -10, lim2 = -10
                                       , fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20):                        
    '''grid point = data[n]
    phase names = data[n].keys() 
    phase fraction = data[n][keys][0]
    el fractions in phase = data[n][keys][1]
    ordered el names in phase = data[n][keys][2]
    ordered el fractions in phase = data[n][keys][3]'''

    if lim1 <= 0: lim1 = L[0]
    if lim2 <= 0: lim2 = L[-1]
    ph_names = []
    for i in range(len(data)):
        keys = data[i].keys()
        for key in keys:
            if key not in ph_names:
                ph_names.append(key)
    if len(ph_names)//2 > 1:
        if len(ph_names)%2 == 1:
            fig1, ax1 = plt.subplots(len(ph_names)//2+1, 2, figsize = [15, (len(ph_names)//2+1)*25/5])
        else:
            fig1, ax1 = plt.subplots(len(ph_names)//2, 2, figsize = [15, len(ph_names)//2*25/5])
        iph = 0
        xph = {}
        for ph in ph_names:
            x = []
            npm = []
            grid_idx_holder = []
            for grid in range(len(data)):
                for phase in data[grid].keys():    
                    if ph in phase:
                        grid_idx_holder.append(grid)
                        x.append(data[grid][phase][1])
                        npm.append(data[grid][phase][0])            
            x = np.ravel(x).reshape((-1, len(elnames)))
            xph[ph] = [L[grid_idx_holder], x]
            for ie, el in enumerate(elnames):
                ysmoothed = gaussian_filter1d(x[:, ie],  sigma = 0.1)
                ax1[iph//2, iph%2].plot(L[grid_idx_holder], ysmoothed, '.-')
            ax1[iph//2, iph%2].legend(elnames, fontsize = lgsize)
            ax1[iph//2, iph%2].set_title('X in {} t = {:2.1e}sec'.format(ph,  TIM[t]), fontsize = 20)
            ax1[iph//2, iph%2].set_xlabel('Distance [um]', fontsize = 20)
            ax1[iph//2, iph%2].set_ylabel('Fraction', fontsize = 20)
            ax1[iph//2, iph%2].tick_params(axis = "x", labelsize = tksize) 
            ax1[iph//2, iph%2].tick_params(axis = "y", labelsize = tksize)
            ax1[iph//2, iph%2].locator_params(axis = 'y', nbins = bins)
            ax1[iph//2, iph%2].locator_params(axis = 'x', nbins = bins)
            ax1[iph//2, iph%2].set_xlim([lim1, lim2])
            iph += 1
        fig1.tight_layout()
        plt.savefig('XinPh_postprocessed-{:.0f}-sec.png'.format(TIM[t]))  
    elif len(ph_names) == 1:
        ph = ph_names[0]
        plt.figure(figsize = [15, len(ph_names)*25/5])
        xph = {}
        x = []
        grid_idx_holder = []
        for grid in range(len(data)):
            for phase in data[grid].keys():    
                if ph in phase:
                    grid_idx_holder.append(grid)
                    x.append(data[grid][phase][1])
        x = np.ravel(x).reshape((-1, len(elnames)))
        xph[ph] = [L[grid_idx_holder], x]
        for ie, el in enumerate(elnames):
            ysmoothed = gaussian_filter1d(x[:, ie], sigma = 0.1)
            plt.plot(L[grid_idx_holder], ysmoothed , '.-')
        plt.legend(elnames, fontsize = lgsize)
        plt.title('xs in {} t = {:2.1e}sec'.format(ph, TIM[t]), fontsize = 20)
        plt.xlabel('Distance [um]', fontsize = 20)
        plt.ylabel('Fractions', fontsize = 20)
        plt.tick_params(axis = "x", labelsize = tksize) 
        plt.tick_params(axis = "y", labelsize = tksize)
        plt.locator_params(axis = 'y', nbins = bins)
        plt.locator_params(axis = 'x', nbins = bins)
        plt.xlim([lim1, lim2])
    else:
        fig1, ax1 = plt.subplots(len(ph_names), 1, figsize = [15, len(ph_names)*25/5])
        iph = 0
        xph = {}
        for ph in ph_names:
            x = []
            grid_idx_holder = []
            for grid in range(len(data)):
                for phase in data[grid].keys():    
                    if ph in phase:
                        grid_idx_holder.append(grid)
                        x.append(data[grid][phase][1])
            x = np.ravel(x).reshape((-1, len(elnames)))
            xph[ph] = [L[grid_idx_holder], x]
            for ie, el in enumerate(elnames):
                ysmoothed = gaussian_filter1d(x[:, ie], sigma = 0.1)
                ax1[iph].plot(L[grid_idx_holder], ysmoothed , '.-')
            ax1[iph].legend(elnames, fontsize = lgsize)
            ax1[iph].set_title('xs in {} t = {:2.1e}sec'.format(ph, TIM[t]), fontsize = 20)
            ax1[iph].set_xlabel('Distance [um]', fontsize = 20)
            ax1[iph].set_ylabel('Fractions', fontsize = 20)
            ax1[iph].tick_params(axis = "x", labelsize = tksize) 
            ax1[iph].tick_params(axis = "y", labelsize = tksize)
            ax1[iph].locator_params(axis = 'y', nbins = bins)
            ax1[iph].locator_params(axis = 'x', nbins = bins)
            ax1[iph].set_xlim([lim1, lim2])
            iph += 1
        fig1.tight_layout()
        plt.savefig('XinPh_postprocessed-{:.0f}-sec.png'.format(TIM[t]))
