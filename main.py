#!/usr/bin/env python
# coding: utf-8

import json

from calculator import *
from correcting import *
from plotter import *
from datareader import *
import os


def main(path):
    plt.close('all')
    
    os.chdir(path)
    print(os.getcwd())
    
    with open("settings.json", "r") as f:
        settings = json.load(f)
    
    if settings['actions']['read']:
        [data_reader(path+dir,settings) for dir in settings['dirList']]
            

    if settings['actions']['calc']:
        [calculator(path+dir+'/',settings) for dir in settings['dirList']]
            
    if settings['actions']['value_correction']:
        [value_correction(path+dir+'/', settings) for dir in settings['dirList']]
    
    if settings['actions']['plot']:
        [single_plotter(path+dir+'/', settings) for dir in settings['dirList']] 
    
    if settings['actions']['plotoverlaid']:
        [ol_plotter(path+dir+'/', settings) for dir in settings['dirList']]
    
    if settings['actions']['plotMG'] and settings['tc_setting']['mobFlag']:
        all_GMX_plotter(path, settings)

if __name__ == "__main__":
    main('/Volumes/exFAT/LUND/PCD/')
