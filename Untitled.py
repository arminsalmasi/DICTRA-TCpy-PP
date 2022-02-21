0#!/usr/bin/env python
# coding: utf-8

from calculator import *
from plotter import *
from correcting import *




def main(DIR1,DIRs,timeflags,actionflags):
    plt.close('all')
    if actionflags['calc']:
        for DIR in DIRs:
            calculator(DIR1, DIR, timeflags)
    if actionflags['value_correction']:
        [value_correction(DIR1, DIR, timeflags) for DIR in DIRs]
    if actionflags['plot']:
        for DIR in DIRs:
            for files in os.listdir(DIR):
                if files.endswith('.pickle') :
                    [single_plotter(DIR1, DIR, filename) for filename in files.split("\n") if "uncorrected" not in filename]
                else:
                    continue
    if actionflags['plotoverlaid'][0]:
        [ol_plotter(DIR1, DIR, actionflags['plotoverlaid'][1]) for DIR in DIRs]
        
if __name__ == "__main__":
    #DIR1 = '/Volumes/exFAT/LUND/WC15Co-Ti64-200um200um/'
    #DIR2 =["DONE-1300C", "1300C-2ndrun", "DONE-1000C", "DONE-1000C-2ndrun", "DONE-1200C", "DONE-1200C-2ndrun", "DONE-1200C-570sec"]
    DIR1 = '/Volumes/exFAT/LUND/PCD/'
    DIR2 = ["1000C-2ndrun", "1000C", "1200C", 
            "1300C-2ndrun", "DONE-1300C","1200C-2ndrun"]
    DIRs = [DIR1+d+'/' for d in DIR2]
    actionflags = {'calc':False, 
                    'value_correction':True, 
                    'plot':True, 
                    'plotoverlaid':[True,['first', 'last']]}
    timeflags = ['first', 'last'] 
    
    main(DIR1, DIRs, timeflags, actionflags)

#bashCommand = "open "+'nameChanged_CQT_tS_TC_NEAT_npms_{}.png'.format(int(tS_tc_VLUs['nearestTime']))
#process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
## %matplotlib qt#user_path = !eval echo ~$USERoutput, error = process.communicate()