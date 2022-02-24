#!/usr/bin/env python
# coding: utf-8

import json

from calculator import *
from correcting import *
from plotter import *


def main(path):
    with open(path+"actions.json", "r") as f:
        actions = json.load(f)
    actionFlags = actions['actionflags']
    timeFlags = actions['timeflags'] 
    dirList = [path+d+'/' for d in actions['dirList']]
    plt.close('all')
    if actionFlags['calc']:
        for dir in dirList:
            calculator(path, dir, timeFlags)
    if actionFlags['value_correction']:
        [value_correction(path, dir, timeFlags) for dir in dirList]
    if actionFlags['plot']:
        for dir in dirList:
            for files in os.listdir(dir):
                if files.endswith('.pickle') :
                    [single_plotter(path, dir, filename) for filename in files.split("\n") if "uncorrected" not in filename]
                else:
                    continue
    if actionFlags['plotoverlaid'][0]:
        [ol_plotter(path, dir, actionFlags['plotoverlaid'][1]) for dir in dirList]
        
if __name__ == "__main__":
    path = "/Volumes/exFAT/LUND/REALPCBN/"
    main(path)

    #DIR1 = '/Volumes/exFAT/LUND/WC15Co-Ti64-200um200um/'
    #dirList =["DONE-1300C", "1300C-2ndrun", "DONE-1000C", "DONE-1000C-2ndrun", "DONE-1200C", "DONE-1200C-2ndrun", "DONE-1200C-570sec"]
    #DIR1 = '/Volumes/exFAT/LUND/PCD/'
    #dirList = ["1000C-2ndrun", "1000C", "1200C", "1300C-2ndrun", "DONE-1300C","1200C-2ndrun"]
    #DIR1 = '/Volumes/exFAT/LUND/PcBN-diffC-erf/'
    #dirList = ["1000C", "1200C", "1300C"]
    #DIR1 = "/Volumes/exFAT/SheffieldTiAl/"
    #dirList = ["01-77-WC6CO-BC-closeW"]
    #DIR1 = '/Volumes/exFAT/SheffieldTiAl/finished-sims/'
    #dirList = ["01-22-WC6CO-BCC-200um-200um-FCC1234-BCC12345-DICTRAFCC-M6-M12-MCSHP-LiQ12-2openBC-3600sec"]
    #DIR1 = '/Volumes/exFAT/LUND/WC15Co-Ti64-200um200um/'
    #dirList =["DONE-1300C", "1300C-2ndrun", "DONE-1000C", "DONE-1000C-2ndrun", "DONE-1200C", "DONE-1200C-2ndrun", "DONE-1200C-570sec"]


    #bashCommand = "open "+'nameChanged_CQT_tS_TC_NEAT_npms_{}.png'.format(int(tS_tc_VLUs['nearestTime']))
    #process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    ## %matplotlib qt#user_path = !eval echo ~$USERoutput, error = process.communicate()
