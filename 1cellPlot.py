import numpy as np
import matplotlib.pyplot as plt
import sys 
import os


#lim1=sys.argv[2]#float(input('lim1:\n'))
#lim2=sys.argv[3]#float(input('lim2:\n'))
os.chdir(sys.argv[1])

#BOUNDARIES            = np.loadtxt('BOUNDARIES.TXT')
CHEMICAL_POTENTIALS   = np.loadtxt('CHEMICAL_POTENTIALS.TXT')
EL_INDEX              = np.loadtxt('EL_INDEX.TXT')
EL_NAMES              = np.loadtxt('EL_NAMES.TXT', dtype = str)
FLUXES                = np.loadtxt('FLUXES.TXT')
GEOMETRY              = np.loadtxt('GEOMETRY.TXT')
INTERFACE_U_FRACTIONS = np.loadtxt('INTERFACE_U_FRACTIONS.TXT')
#MOLAR_VOLUME          = np.loadtxt('MOLAR_VOLUME.TXT')
MOLE_FRACTIONS        = np.loadtxt('MOLE_FRACTIONS.TXT')
NR_OF_CELLS           = np.loadtxt('NR_OF_CELLS.TXT')
NR_OF_EL              = np.loadtxt('NR_OF_EL.TXT', dtype = int)
NR_OF_PH              = np.loadtxt('NR_OF_PH.TXT', dtype = int)
PHASE_FRACTIONS       = np.loadtxt('PHASE_FRACTIONS.TXT')
PHASES_IN_REGION      = np.loadtxt('PHASES_IN_REGION.TXT')
PH_COMP_SET           = np.loadtxt('PH_COMP_SET.TXT')
PH_INDEX              = np.loadtxt('PH_INDEX.TXT')
with open('PH_NAMES.TXT','r') as f:
    PH_NAMES = [name.strip() for name in f]
#PH_NAMES              = np.loadtxt('PH_NAMES.TXT', dtype = str)
REGION_NAMES          = np.loadtxt('REGION_NAMES.TXT', dtype =str)
REGIONS_PER_CELL      = np.loadtxt('REGIONS_PER_CELL.TXT')
SUBSTITUTIONAL        = np.loadtxt('SUBSTITUTIONAL.TXT')
TIME                  = np.loadtxt('TIME.TXT')
VOLUME_MIDPOINTS      = np.loadtxt('VOLUME_MIDPOINTS.TXT')
VOLUMES_PER_REGION    = np.loadtxt('VOLUMES_PER_REGION.TXT', dtype =int)


'''last timestep'''
VOLUMES_PER_REGION_last = VOLUMES_PER_REGION[-1]
VOLUME_MIDPOINTS_last = VOLUME_MIDPOINTS[-1 * VOLUMES_PER_REGION_last : ]
VOLUMES_PER_REGION_0 = VOLUMES_PER_REGION[0]
VOLUME_MIDPOINTS_0 = VOLUME_MIDPOINTS[: VOLUMES_PER_REGION_0 ]

MOLE_FRACTIONS_last = MOLE_FRACTIONS[-1 * VOLUMES_PER_REGION_last * NR_OF_EL : ]
MOLE_FRACTIONS_last = MOLE_FRACTIONS_last.reshape([-1, NR_OF_EL])
MOLE_FRACTIONS_0 = MOLE_FRACTIONS[: VOLUMES_PER_REGION_last * NR_OF_EL ]
MOLE_FRACTIONS_0 = MOLE_FRACTIONS_0.reshape([-1, NR_OF_EL])

CHEMICAL_POTENTIALS_last = CHEMICAL_POTENTIALS[-1 * VOLUMES_PER_REGION_last * NR_OF_EL :]
CHEMICAL_POTENTIALS_last = CHEMICAL_POTENTIALS_last.reshape([-1, NR_OF_EL])

PHASE_FRACTIONS_last = PHASE_FRACTIONS[-1 * VOLUMES_PER_REGION_last * NR_OF_PH : ]
PHASE_FRACTIONS_last = PHASE_FRACTIONS_last.reshape([-1, NR_OF_PH])
PHASE_FRACTIONS_0 = PHASE_FRACTIONS[: VOLUMES_PER_REGION_last * NR_OF_PH ]
PHASE_FRACTIONS_0 = PHASE_FRACTIONS_0.reshape([-1, NR_OF_PH])


VOLUME_MIDPOINTS_last = -1*(VOLUME_MIDPOINTS_last-VOLUME_MIDPOINTS_last[-1])
VOLUME_MIDPOINTS_0 = -1*(VOLUME_MIDPOINTS_0-VOLUME_MIDPOINTS_0[-1])

print(TIME)

lim1=input('lim1 {}: \n'.format(int(VOLUME_MIDPOINTS_last[0]*1e6)))
if lim1=='':
    lim1 = int(VOLUME_MIDPOINTS_last[0]*1e6)
else:
    lim1=float(lim1 )

lim2=input('lim2 {}: \n'.format(int(VOLUME_MIDPOINTS_last[-1]*1e6)))
if lim2=='':
    lim2 = int(VOLUME_MIDPOINTS_last[-1]*1e6)
else:
    lim2 = float(lim2 )

#MF
plt.figure()
for el,elname in enumerate(EL_NAMES):
    if any(MOLE_FRACTIONS_last[:,el]>1e-4):
        plt.plot(VOLUME_MIDPOINTS_last*1e6,MOLE_FRACTIONS_last[:,el], label='X('+elname+')')
    #plt.plot(VOLUME_MIDPOINTS_first,MOLE_FRACTIONS_first[:,el], '--', label=elname+' first')
plt.title('t = '+str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])
#MU
plt.figure()
for el,elname in enumerate(EL_NAMES):
    plt.plot(VOLUME_MIDPOINTS_last*1e6,CHEMICAL_POTENTIALS_last[:,el], '.-', label='MU('+elname+')')
    #plt.plot(VOLUME_MIDPOINTS_first,CHEMICAL_POTENTIALS_first[:,el], '--', label=elname+' first')
plt.title(str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])

#PHF DICTRTA
print(PH_NAMES)
plt.figure()
for ph,phname in enumerate(PH_NAMES):
    if any(PHASE_FRACTIONS_last[:,ph]>1e-12):
        plt.plot(VOLUME_MIDPOINTS_last*1e6,PHASE_FRACTIONS_last[:,ph], label = 'NPM('+PH_NAMES[ph]+')'  )
        #plt.plot(VOLUME_MIDPOINTS_first,PHASE_FRACTIONS_first[:,ph], '--', label = phname+ ' first')
plt.title(str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])



for ph,phname in enumerate(PH_NAMES):
    if 'DIAMOND' in phname:
        plt.figure()
        plt.plot(VOLUME_MIDPOINTS_last*1e6,PHASE_FRACTIONS_last[:,ph], label = 'NPM('+PH_NAMES[ph]+')'  )
        plt.plot(VOLUME_MIDPOINTS_0*1e6,PHASE_FRACTIONS_0[:,ph],':', label = 'NPM('+PH_NAMES[ph]+')'  )
        #plt.plot(VOLUME_MIDPOINTS_first,PHASE_FRACTIONS_first[:,ph], '--', label = phname+ ' first')
        plt.title(str(TIME[-1]))
        plt.legend()
        plt.xlim([lim1,lim2])

plt.show()

##Semi-Corrected PHF
#plt.figure()
#BCC=np.zeros(PHASE_FRACTIONS_last.shape[0])
#FCC=np.zeros(PHASE_FRACTIONS_last.shape[0])
#HCP=np.zeros(PHASE_FRACTIONS_last.shape[0])
#M6C=np.zeros(PHASE_FRACTIONS_last.shape[0])
#for ph,phname in enumerate(PH_NAMES):
#    if 'BCC' in phname:
#        BCC += PHASE_FRACTIONS_last[:,ph]
#    if 'FCC' in phname:
#        FCC += PHASE_FRACTIONS_last[:,ph]
#    if 'HCP' in phname:
#        HCP += PHASE_FRACTIONS_last[:,ph]
#    if 'M6C' in phname:
#        M6C += PHASE_FRACTIONS_last[:,ph]
#if any(BCC>1e-12):
#    plt.plot(VOLUME_MIDPOINTS_last*1e6,BCC, label = 'BCC'  )
#if any(FCC>1e-12):
#    plt.plot(VOLUME_MIDPOINTS_last*1e6,FCC, label = 'FCC'  )
#if any(HCP>1e-12):
#    plt.plot(VOLUME_MIDPOINTS_last*1e6,HCP, label = 'HCP'  )
#if any(M6C>1e-12):
#    plt.plot(VOLUME_MIDPOINTS_last*1e6,M6C, label = 'M6C'  )
#for ph,phname in enumerate(PH_NAMES):
#    if any(PHASE_FRACTIONS_last[:,ph]>1e-12) and  ('BCC' not in phname)   and  ('FCC' not in phname)   and  ('HCP' not in phname) and ('M6C' not in phname) :
#        plt.plot(VOLUME_MIDPOINTS_last*1e6,PHASE_FRACTIONS_last[:,ph], label = PH_NAMES[ph])
#    #plt.plot(VOLUME_MIDPOINTS_first,PHASE_FRACTIONS_first[:,ph], '--', label = phname+ ' first')
#plt.title(str(TIME[-1]))
#plt.legend()
#plt.xlim([lim1,lim2])




#'''first timestep'''
#tstp=2
#VOLUMES_PER_REGION_before = np.sum(VOLUMES_PER_REGION[:tstp])
#VOLUMES_PER_REGION_first = VOLUMES_PER_REGION[tstp]+VOLUMES_PER_REGION_before
#
#VOLUME_MIDPOINTS_first = VOLUME_MIDPOINTS[VOLUMES_PER_REGION_before: VOLUMES_PER_REGION_first]
#print(VOLUMES_PER_REGION_first)
#
#MOLE_FRACTIONS_first = MOLE_FRACTIONS[VOLUMES_PER_REGION_before * NR_OF_EL: VOLUMES_PER_REGION_first * NR_OF_EL ]
#MOLE_FRACTIONS_first = MOLE_FRACTIONS_first.reshape([-1, NR_OF_EL ])
#
#CHEMICAL_POTENTIALS_first = CHEMICAL_POTENTIALS[VOLUMES_PER_REGION_before * NR_OF_EL: VOLUMES_PER_REGION_first * NR_OF_EL ]
#CHEMICAL_POTENTIALS_first = CHEMICAL_POTENTIALS_first.reshape([-1, NR_OF_EL ])
#
#PHASE_FRACTIONS_first = PHASE_FRACTIONS[VOLUMES_PER_REGION_before * NR_OF_PH : VOLUMES_PER_REGION_first * NR_OF_PH ]
#PHASE_FRACTIONS_first = PHASE_FRACTIONS_first.reshape([-1, NR_OF_PH])
