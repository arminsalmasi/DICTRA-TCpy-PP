import numpy as np
import matplotlib.pyplot as plt
import sys 
import os
import pdb

os.chdir(sys.argv[1])
#BOUNDARIES            = np.loadtxt('BOUNDARIES.TXT')
chpot   = np.loadtxt('CHEMICAL_POTENTIALS.TXT')
EL_INDEX              = np.loadtxt('EL_INDEX.TXT')
EL_NAMES              = np.loadtxt('EL_NAMES.TXT', dtype = str)
FLUXES                = np.loadtxt('FLUXES.TXT')
GEOMETRY              = np.loadtxt('GEOMETRY.TXT')
INTERFACE_U_frs = np.loadtxt('INTERFACE_U_FRACTIONS.TXT')
mfrs        = np.loadtxt('MOLE_FRACTIONS.TXT')
NR_OF_CELLS           = np.loadtxt('NR_OF_CELLS.TXT',dtype=int)
NR_OF_EL              = np.loadtxt('NR_OF_EL.TXT', dtype = int)
NR_OF_PH              = np.loadtxt('NR_OF_PH.TXT', dtype = int)
phfrs       = np.loadtxt('PHASE_FRACTIONS.TXT')
PHASES_INreg      = np.loadtxt('PHASES_IN_REGION.TXT')
PH_COMP_SET           = np.loadtxt('PH_COMP_SET.TXT')
PH_INDEX              = np.loadtxt('PH_INDEX.TXT')
with open('PH_NAMES.TXT','r') as f:
    PH_NAMES = [name.strip() for name in f]
REGION_NAMES          = np.loadtxt('REGION_NAMES.TXT', dtype =str)
REGIONSper_CELL      = np.loadtxt('REGIONS_PER_CELL.TXT')
SUBSTITUTIONAL        = np.loadtxt('SUBSTITUTIONAL.TXT')
TIME                  = np.loadtxt('TIME.TXT')
Vmdps      = np.loadtxt('VOLUME_MIDPOINTS.TXT')
VsPerReg    = np.loadtxt('VOLUMES_PER_REGION.TXT', dtype =int)

'''first timestep'''
VsPerReg_1 = VsPerReg[-NR_OF_CELLS:]
Vmdps_1 = Vmdps[: np.sum(VsPerReg_1) ]
mfrs_1 = mfrs[:  np.sum(VsPerReg_1) * NR_OF_EL]
mfrs_1 = mfrs_1.reshape([-1, NR_OF_EL])
chpot_1 = chpot[: np.sum(VsPerReg_1) * NR_OF_EL]
chpot_1 = chpot_1.reshape([-1, NR_OF_EL])
phfrs_1 = phfrs[: np.sum(VsPerReg_1) * NR_OF_PH]
phfrs_1 = phfrs_1.reshape([-1, NR_OF_PH])
'''last timestep'''
VsPerReg_2 = VsPerReg[-NR_OF_CELLS:]
Vmdps_2 = Vmdps[-1 * np.sum(VsPerReg_2) : ]
mfrs_2 = mfrs[-1 * np.sum(VsPerReg_2) * NR_OF_EL : ]
mfrs_2 = mfrs_2.reshape([-1, NR_OF_EL])
chpot_2 = chpot[-1 * np.sum(VsPerReg_2) * NR_OF_EL :]
chpot_2 = chpot_2.reshape([-1, NR_OF_EL])
phfrs_2 = phfrs[-1 * np.sum(VsPerReg_2) * NR_OF_PH : ]
phfrs_2 = phfrs_2.reshape([-1, NR_OF_PH])
''''''
print(TIME)
x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
x12 = Vmdps_1[VsPerReg_1[0]:]*1e6
x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
x22 = Vmdps_2[VsPerReg_2[0]:]*1e6
x1 = np.concatenate((x11, x11[-1]+max(x12)+min(x12)-np.flip(x12)), axis=0)
x2 = np.concatenate((x21, x21[-1]+max(x22)+min(x22)-np.flip(x22)), axis=0)
x1 = -1*(x1-x1[-1])
x2 = -1*(x2-x2[-1])
lim1=input('lim1 {}: \n'.format(int(x2[0])))
if lim1=='':
    lim1 = int(x2[0])
else:
    lim1=float(lim1 )
lim2=input('lim2 {}: \n'.format(int(x2[-1])))
if lim2=='':
    lim2 = int(x2[-1])
else:
    lim2 = float(lim2 )
## Merged cell1 + cell 2
#MF
plt.figure()
for el,elname in enumerate(EL_NAMES):
    #time1 cell1
    y11 = mfrs_1[:VsPerReg_2[0],el] 
    y12 = mfrs_1[VsPerReg_2[0]:,el]
    y21 = mfrs_2[:VsPerReg_2[0],el]
    y22 = mfrs_2[VsPerReg_2[0]:,el]
    y = np.concatenate((y11, np.flip(y12)),axis = 0 )
    plt.plot(x1,y,':',label='X('+elname+')-1')
    y = np.concatenate((y21, np.flip(y22)),axis=0)
    plt.plot(x2,y,'-',label='X('+elname+')-2')
plt.title('t = ' + str(TIME[-1]))
plt.xlim([lim1,lim2])
plt.legend()    
#MU
plt.figure()
for el,elname in enumerate(EL_NAMES):
    y11 = chpot_1[:VsPerReg_2[0],el] 
    y12 = chpot_1[VsPerReg_2[0]:,el]
    y21 = chpot_2[:VsPerReg_2[0],el]
    y22 = chpot_2[VsPerReg_2[0]:,el]
    y = np.concatenate((y11, np.flip(y12)),axis = 0 )
    plt.plot(x1,y,':',label='MU('+elname+')-1')
    y = np.concatenate((y21, np.flip(y22)),axis=0)
    plt.plot(x2,y,'-',label='MU('+elname+')-2')
plt.title('t = ' + str(TIME[-1]))
plt.xlim([lim1,lim2])
plt.legend()    
#PHF DICTRTA
print(PH_NAMES)
plt.figure()
leg = []
for ph,phname in enumerate(PH_NAMES):
    if any(phfrs_2[:,ph]>1e-6):
        #time1 cell2
        y11 = phfrs_1[:VsPerReg_2[0],ph] 
        y21 = phfrs_2[:VsPerReg_2[0],ph]
        y12 = phfrs_1[VsPerReg_2[0]:,ph]
        y22 = phfrs_2[VsPerReg_2[0]:,ph]
        y = np.concatenate((y11, np.flip(y12)),axis = 0 )
        #plt.plot(x1,y,':',label='NPM('+PH_NAMES[ph]+')-1')
        y = np.concatenate((y21, np.flip(y22)),axis=0)
        plt.plot(x2,y,'-',label='NPM('+PH_NAMES[ph]+')-2')
plt.title('t = ' + str(TIME[-1]))
plt.xlim([lim1,lim2])
plt.legend()
plt.show()
exit()




##cell 1
#MF
plt.figure()
for el,elname in enumerate(EL_NAMES):
    plt.plot(Vmdps_2[:VsPerReg_2[0]]*1e6,mfrs_2[:VsPerReg_2[0],el], label=elname)
plt.title(str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])
#MU
plt.figure()
for el,elname in enumerate(EL_NAMES):
    plt.plot(Vmdps_2[:VsPerReg_2[0]]*1e6,chpot_2[:VsPerReg_2[0],el], '.-', label=elname)
plt.title(str(TIME[-1]))
plt.legend()

#PHF DICTRTA
print(PH_NAMES)
plt.figure()
for ph,phname in enumerate(PH_NAMES):
    if any(phfrs_2[:,ph]>1e-6):
        plt.plot(Vmdps_2[:VsPerReg_2[0]]*1e6,phfrs_2[:VsPerReg_2[0],ph], label = PH_NAMES[ph]  )
plt.title(str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])

##cell 2
#MF
plt.figure()
for el,elname in enumerate(EL_NAMES):
    plt.plot(Vmdps_2[VsPerReg_2[0]:]*1e6,mfrs_2[VsPerReg_2[0]:,el], label=elname+'-2')
    plt.plot(Vmdps_1[VsPerReg_1[0]:]*1e6,mfrs_1[VsPerReg_2[0]:,el],':', label=elname+'-1')

plt.title(str(TIME[-1]))
plt.legend()
plt.xlim([lim1,lim2])

#MU
plt.figure()
for el,elname in enumerate(EL_NAMES):
    plt.plot(Vmdps_2[VsPerReg_2[0]:]*1e6,chpot_2[VsPerReg_2[0]:,el], '.-', label=elname+'-2')
    plt.plot(Vmdps_1[VsPerReg_1[0]:]*1e6,chpot_1[VsPerReg_1[0]:,el], ':', label=elname+'-1')
plt.title(str(TIME[-1]))
plt.legend()

#PHF DICTRTA
print(PH_NAMES)
plt.figure()
for ph,phname in enumerate(PH_NAMES):
    if any(phfrs_2[:,ph]>1e-6):
        plt.plot(Vmdps_2[VsPerReg_2[0]:]*1e6,phfrs_2[VsPerReg_2[0]:,ph], label = PH_NAMES[ph]+'-2'  )
        plt.plot(Vmdps_1[VsPerReg_1[0]:]*1e6,phfrs_1[VsPerReg_1[0]:,ph],':', label = PH_NAMES[ph]+'-1'  )
plt.title(str(TIME[-1]))
plt.legend()




##cell1 + cell 2
#MF
plt.figure()
leg =[]
for el,elname in enumerate(EL_NAMES):
    #time1 cell1
    x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
    y11 = mfrs_1[:VsPerReg_2[0],el] 
    
    
    #time2 cell1
    x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
    y21 = mfrs_2[:VsPerReg_2[0],el]

    #time1 cell2
    x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
    y12 = mfrs_1[VsPerReg_2[0]:,el]

    #time2 cell2
    x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
    y22 = mfrs_2[VsPerReg_2[0]:,el]

    plt.plot(x11,y11,':',x21,y21,'-' )
    plt.plot(np.flip(x12),y12,':',np.flip(x22),y22,'-' )
    leg.append( elname+'-t1c1' ) 
    leg.append( elname+'-t2c1' )
    leg.append( elname+'-t1c2' )
    leg.append( elname+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)

plt.figure()
#MU
leg=[]
for el,elname in enumerate(EL_NAMES):
    #time1 cell1
    x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
    y11 = chpot_1[:VsPerReg_2[0],el] 
    
    
    #time2 cell1
    x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
    y21 = chpot_2[:VsPerReg_2[0],el]

    #time1 cell2
    x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
    y12 = chpot_1[VsPerReg_2[0]:,el]

    #time2 cell2
    x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
    y22 = chpot_2[VsPerReg_2[0]:,el]

    plt.plot(x21,y21,'-' )
    plt.plot(np.flip(x22),y22,'-' )
    leg.append( elname+'-t2c1' )
    leg.append( elname+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)

#PHF DICTRTA
print(PH_NAMES)
plt.figure()
leg = []
for ph,phname in enumerate(PH_NAMES):
    if any(phfrs_2[:,ph]>1e-6):
        #time1 cell1
        x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
        y11 = phfrs_1[:VsPerReg_2[0],ph] 
    
        #time2 cell1
        x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
        y21 = phfrs_2[:VsPerReg_2[0],ph]

        #time1 cell2
        x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
        y12 = phfrs_1[VsPerReg_2[0]:,ph]

        #time2 cell2
        x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
        y22 = phfrs_2[VsPerReg_2[0]:,]

        plt.plot(x21,y21,'-' )
        plt.plot(np.flip(x22),y22,'-' )
        leg.append( PH_NAMES[ph]+'-t2c1' )
        leg.append( PH_NAMES[ph]+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)

##cell1 + cell 2
#MF
plt.figure()
leg =[]
for el,elname in enumerate(EL_NAMES):
    #time1 cell1
    x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
    y11 = mfrs_1[:VsPerReg_2[0],el] 
    
    
    #time2 cell1
    x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
    y21 = mfrs_2[:VsPerReg_2[0],el]

    #time1 cell2
    x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
    y12 = mfrs_1[VsPerReg_2[0]:,el]

    #time2 cell2
    x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
    y22 = mfrs_2[VsPerReg_2[0]:,el]

    plt.plot(x11,y11,':',x21,y21,'-' )
    plt.plot(np.flip(x12),y12,':',np.flip(x22),y22,'-' )
    leg.append( elname+'-t1c1' ) 
    leg.append( elname+'-t2c1' )
    leg.append( elname+'-t1c2' )
    leg.append( elname+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)

plt.figure()
#MU
leg=[]
for el,elname in enumerate(EL_NAMES):
    #time1 cell1
    x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
    y11 = chpot_1[:VsPerReg_2[0],el] 
    
    
    #time2 cell1
    x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
    y21 = chpot_2[:VsPerReg_2[0],el]

    #time1 cell2
    x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
    y12 = chpot_1[VsPerReg_2[0]:,el]

    #time2 cell2
    x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
    y22 = chpot_2[VsPerReg_2[0]:,el]

    plt.plot(x21,y21,'-' )
    plt.plot(np.flip(x22),y22,'-' )
    leg.append( elname+'-t2c1' )
    leg.append( elname+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)

#PHF DICTRTA
print(PH_NAMES)
plt.figure()
leg = []
for ph,phname in enumerate(PH_NAMES):
    if any(phfrs_2[:,ph]>1e-6):
        #time1 cell1
        x11 = Vmdps_1[:VsPerReg_1[0]]*1e6
        y11 = phfrs_1[:VsPerReg_2[0],ph] 
    
        #time2 cell1
        x21 = Vmdps_2[:VsPerReg_2[0]]*1e6
        y21 = phfrs_2[:VsPerReg_2[0],ph]

        #time1 cell2
        x12 = Vmdps_1[VsPerReg_1[0]:]*1e6+x11[-1]
        y12 = phfrs_1[VsPerReg_2[0]:,ph]

        #time2 cell2
        x22 = Vmdps_2[VsPerReg_2[0]:]*1e6+x21[-1]
        y22 = phfrs_2[VsPerReg_2[0]:,]

        plt.plot(x21,y21,'-' )
        plt.plot(np.flip(x22),y22,'-' )
        leg.append( PH_NAMES[ph]+'-t2c1' )
        leg.append( PH_NAMES[ph]+'-t2c2' )
plt.title(str(TIME[-1]))
plt.legend(leg)
plt.show()
