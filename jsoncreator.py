import json

setting = {}
setting['phase_changes'] = [('BCC_A2', 'W', 1), ('FCC_A1', 'C', 0.03)]
phase_change = [('BCC_A2', 'W', 1), ('FCC_A1', 'C', 0.03)]#, ('FCC_A1', 'Ti', 0.05), ('FCC_A1', 'Al', 0.05)]
tc_setting = {'database':'tcfe9', 'acRefs':[], 'phsToSus':[], 'p3flag':True} 
setting['tc_setting'] = {'database':'tcfe9', 'acRefs':[], 'phsToSus':[], 'p3flag':False} 
setting['name_pairs'] = [('BCC_A2#1', 'Ti64 BCC'), 
              ('MC_SHP#1', 'WC'), 
              ('M6C#1', 'Eta M6'), 
              ('BCC_A2-W', 'W BCC'), 
              ('FCC_A1-CTI', 'TiC FCC'), ('FCC_A1-TIC', 'TiC FCC'),
              ('FCC_A1-CAL', 'AlC FCC'), ('FCC_A1-ALC', 'AlC FCC'), 
              ('LIQUID#1', 'LIQUID'),
              ('DIAMOND_FCC_A4#1', 'GRAPHITE'),
              ('AL4C3#1', 'AL4C3'),
              ('FCC_A1#1', 'Co FCC'), ('FCC_A1_ALCO', 'Co FCC'), ('FCC_A1-COAL', 'Co FCC'), 
              ('FCC_A1-COC', 'Co FCC') ],
setting["plt_settings"]={"legend":"", "lineW":3, "legF":20, "xlims":[], "title":"",
                    "ylab":"", "xlab":"", "labF":20, "tickS":20, "bins":5, "figsize":[15,15]}
##('FCC_A1_ALCO', 'CoAl FCC '), ('FCC_A1-COAL', 'CoAl FCC'),  ('FCC_A1-COC', 'CoC FCC')


with open('setting.json', 'w') as f:
    json.dump(setting, f, indent=4)

plot_settings = {"xlims": [150,250],"ylims": [0,1],
"figsize": [15,15],
"lineW": 5,
"title": "",
"labF": 22,
"tickS": 22,
"bins": 5,
"boxLw": 5
}
#f = open('setting.json')
#setting = json.load(f)
#print(setting.keys())