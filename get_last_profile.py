from snapshot_Mon31Jun22_clibv2 import * #%matplotlib qt#user_path = !eval echo ~$USER
import matplotlib.pyplot as plt
import numpy as np


VLUs = get_values_from_textfiles('./')
#['path', 'all_mfs', 'elnames', 'all_pts', 'times', 'n_pts', 'DICT_all_npms', 'DICT_phnames', 'DICT_all_mus', 'T', 'interstitials', 'substitutionals'])


points =[]
holder = 0
for n,npt in enumerate(VLUs['n_pts'][1:]):
    npt = int(npt)
    points.append(VLUs['all_pts'][holder:holder+npt])
    holder = holder+npt
grid = np.array(points[-1])

mf =[]
holder = 0
for n,npt in enumerate(VLUs['n_pts'][1:]):
    npt = int(npt)
    mf.append(VLUs['all_mfs'][holder: holder+(npt*len(VLUs['elnames']))])
    holder = holder+(npt*len(VLUs['elnames']))
mf = np.array(mf[-1]).reshape((-1,len(VLUs['elnames'])))


np.savetxt('grid.TXT', grid, fmt='%.18e', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)
for nel,el in enumerate(VLUs['elnames']):
    np.savetxt(el+'.TXT', mf[:,nel], fmt='%.18e', delimiter=' ', newline='\n', header='', footer='', comments='# ', encoding=None)

plt.plot(grid,mf)
plt.show()
