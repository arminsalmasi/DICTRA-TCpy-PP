#!/usr/bin/env python
# coding: utf-8

# In[28]:


from CALCULATE_PLT_DLL import *
import matplotlib.pyplot as plt
#%matplotlib qt
#import pdb
###########################################################################3


pth, mfs, elnames, vmps, ts, vprs, npms, phnames, chem_pots, T,tidx1, tidx2, tidx3, mf1, mf2, mf3 , npm1, npm2, npm3, chem_pot1,chem_pot2, chem_pot3, vmp1, vmp2,vmp3, phnames21, phnames22,phnames23, t1, t2,t3, all_grid_values3, xph_pp, npm_pp, ph_names_pp,Lpp, npm_pp_corrected, xph_pp_corrected, accgraph, acs_SER = get_values()


# In[29]:


subs=[0,2,3,4,5]

'''Deleting png files'''
#plt.close('all')
del_pngs()
#'''Setting plot xlimits, lim1,lim2=-1 : domain xlimits lim1,lim2='' : automatic'''
# lim1,lim2 = get_lims_gui(vmp3)
# xlim1,xlim2 = set_xlim(vmp1,vmp3,lim1,lim2)


# In[37]:


domlim=(-1,-1)
zoomlim = (190,210)
zommlimstr='{}-{}'.format(zoomlim[0],zoomlim[1])
domainstr='0-400'

'''Plotting corrected NPMs npm, xph, t, TIM, L, lim1, lim2, fsize, lsize, tsize, bins, tksize, stsize, lgsiz'''
'''U fractions'''
plt.figure(figsize=[15,15])
color=['r','k','g','blue','m','c']
cnt=0
for i in [0,2,3,4,5]:
    #plt.plot(vmp1,  mf1[:,i]/ (mf1[:,0]+mf1[:,2]+mf1[:,3]+mf1[:,4]+mf1[:,5]),'--',color=color[cnt],linewidth=5)
    plt.plot(vmp1,  mf1[:,i]/ np.sum(mf1[:,subs]),'--',color=color[cnt],linewidth=5)
    #plt.plot(vmp3, mf3[:,i]/(mf3[:,0]+mf3[:,2]+mf3[:,3]+mf3[:,4]+mf3[:,5]),color=color[cnt],linewidth=5,label=elnames[i])      
    plt.plot(vmp3, mf3[:,i]/np.sum(mf1[:,subs]),color=color[cnt],linewidth=5,label=elnames[i])      
    cnt+=1
plt.legend(fontsize=26)
plt.xlabel(r'Distance $\mu$m', fontsize = 40)
plt.ylabel('u-fraction', fontsize = 40)
plt.xticks(fontsize = 40)
plt.yticks(fontsize = 40)
#plt.xlim([zoomlim[0], zoomlim[1]])
plt.savefig('u_fraction_sub.png')
plt.rcParams["axes.edgecolor"] = "black"
plt.rcParams["axes.linewidth"] = 5

'''U fraction C'''
plt.figure(figsize=[15,15])
color=['r','g','k','blue','c','m']
plt.plot(vmp1,  mf1[:,1]/(mf1[:,0]+mf1[:,2]+mf1[:,3]+mf1[:,4]+mf1[:,5]),'k--',linewidth=5)
plt.plot(vmp3, mf3[:,1]/(mf3[:,0]+mf3[:,2]+mf3[:,3]+mf3[:,4]+mf3[:,5]),'k',linewidth=5,label=elnames[1])      
plt.legend(fontsize = 40)
plt.xlabel(r'Distance $\mu$m', fontsize = 40)
plt.ylabel('u-fraction', fontsize = 40)
plt.xticks(fontsize = 40)
plt.yticks(fontsize = 40)
#plt.xlim([zoomlim[0], zoomlim[1]])
plt.savefig('u_fraction_C.png')
plt.rcParams["axes.edgecolor"] = "black"
plt.rcParams["axes.linewidth"] = 5


# In[40]:


zoomlim = (190,210)
plt.figure(figsize=[15,15])
plt.plot(vmp3,accgraph,'k',linewidth=4)
plt.xlabel(r'Distance $\mu$m', fontsize = 40)
plt.ylabel('Activity C (Graphite)', fontsize = 40)
plt.xticks(fontsize = 40)
plt.yticks(fontsize = 40)
#plt.xlim([zoomlim[0], zoomlim[1]])
plt.savefig('aC_Graph.png')
plt.rcParams["axes.edgecolor"] = "black"
plt.rcParams["axes.linewidth"] = 5


# In[41]:


domlim=(-1,-1)
zoomlim = (0,1600)
zommlimstr='{}-{}'.format(zoomlim[0],zoomlim[1])
domainstr='0-400'
strr=zommlimstr

xlim1,xlim2=zoomlim
'''Plotting corrected NPMs npm, xph, t, TIM, L, lim1, lim2, fsize, lsize, tsize, bins, tksize, stsize, lgsiz'''
plot_tc_corrected_results_phf_all_phases(npm_pp_corrected, xph_pp_corrected, tidx3, ts, vmp3, xlim1, xlim2, 40, 40, 40, 10, 40, 40, 40, 4, 'corrected-npm-{}'.format(zommlimstr)  )
plt.show()
# In[33]:


# '''Setting plot xlimits, lim1,lim2=-1 : domain xlimits lim1,lim2='' : automatic'''
# xlim1,xlim2=-1,-1
# '''Plotting post processed phase compositions '''
# fsize, lsize, tsize, bins, tksize, stsize, lgsize = 15, 15, 15, 15, 15, 20, 15
# plot_tc_results_xphf_phases(xph_pp,npm_pp,t3,elnames,ph_names_pp,vmp3,xlim1,xlim2, fsize, lsize, tsize, bins, tksize, stsize, lgsize )


# In[34]:


# '''Plotting zeropadded corrected averages of NPMs Lx2, npm_pp_corrected, ttx2, lim1, lim2, L, fsize, lsize, tsize, bins, tksize, stsize, lgsize'''
# plot_zero_padded_npm_corrected(vmp3, npm_pp_corrected, t3, xlim1, xlim2, vmp3, 20, 20, 30, 10, 20, 30, 20, 3 ,'zeropadded-npm-190-200')
# '''Plotting chemical potential DICTRA output at 3 timesteps x1, x2, x3, L1, L2, L3, tt1, tt2, tt3, names, lim1, lim2, title, file_name', ylab, fsize, lsize, tsize, bins, tksize, stsize, lgsize'''
# xlim1,xlim2=-1,-1
# plot_x_3ts_log10(chem_pot1, chem_pot2, chem_pot3, vmp1, vmp2, vmp3 , t1, t2, t3, elnames, xlim1, xlim2, '', 'log10-Mus_DICTRA-0-200',r'-log10($\mu$)', 20, 20, 20, 8, 15, 30, 20, 3 ) #r'-log10($\mu$)'
# plot_x_3ts_log10(chem_pot1, chem_pot2, chem_pot3, vmp1, vmp2, vmp3 , t1, t2, t3, elnames, xlim1, xlim2, '', 'log10-Mus_DICTRA-0-200',r'-log10($\mu$)', 20, 20, 20, 8, 15, 30, 20, 3 ) #r'-log10($\mu$)'
# xlim1,xlim2=zoomlim
# plot_x_3ts_log10(chem_pot1, chem_pot2, chem_pot3, vmp1, vmp2, vmp3 , t1, t2, t3, elnames, xlim1, xlim2, '', 'log10-Mus-DICTRA-{}'.format(zommlimstr),r'-log10($\mu$)', 20, 20, 20, 8, 15, 30, 20, 3 ) #r'-log10($\mu$)'


# In[35]:




# plt.figure(figsize=[15,10])
# #plt.plot(vmp1,np.log10(mf1[:,2]),'-.',vmp2, np.log10(mf2[:,2]),'--',vmp3, np.log10(mf3[:,2]),linewidth=3)
# plt.plot(vmp1,mf1[:,1],'-.',vmp2, mf2[:,2],'--',vmp3, mf3[:,2],linewidth=3)
# plt.legend(['t={:0.0f} sec'.format(t1),'t={:0.0f} sec'.format(t2),'t={:0.0f} sec'.format(t3)],fontsize=20)
# plt.xlabel(r'Dist $\mu$m', fontsize = 20)
# plt.ylabel('Mole fraction of C', fontsize = 20)
# #plt.ylabel('log10(X(Co))', fontsize = 20)
# plt.xticks(fontsize = 20)
# plt.yticks(fontsize = 20)
# plt.xlim([zoomlim[0], zoomlim[1]])
# plt.savefig('mf-C.png')
# #plot_tc_corrected_result_phf_all_phases(npm_pp_corrected, xph_pp_corrected, tidx3, ts, vmp3, xlim1, xlim2, 20, 20, 30, 10, 20, 30, 20, 3, 'corrected-npm-{}'.format(zommlimstr)  )

# plt.figure(figsize=[15,10])
# #plt.plot(vmp1,np.log10(mf1[:,2]),'-.',vmp2, np.log10(mf2[:,2]),'--',vmp3, np.log10(mf3[:,2]),linewidth=3)
# plt.plot(vmp1,mf1[:,2],'-.',vmp2, mf2[:,2],'--',vmp3, mf3[:,2],linewidth=3)
# plt.legend(['t={:0.0f} sec'.format(t1),'t={:0.0f} sec'.format(t2),'t={:0.0f} sec'.format(t3)],fontsize=20)
# plt.xlabel(r'Dist $\mu$m', fontsize = 20)
# plt.ylabel('Mole fraction of Co', fontsize = 20)
# #plt.ylabel('log10(X(Co))', fontsize = 20)
# plt.xticks(fontsize = 20)
# plt.yticks(fontsize = 20)
# plt.xlim([zoomlim[0], zoomlim[1]])
# plt.savefig('mf-Co.png')
# #plot_tc_corrected_result_phf_all_phases(npm_pp_corrected, xph_pp_corrected, tidx3, ts, vmp3, xlim1, xlim2, 20, 20, 30, 10, 20, 30, 20, 3, 'corrected-npm-{}'.format(zommlimstr)  )



# In[36]:



# '''Plotting Mu '''
# all_x_plotter(elnames, vmp3, t3, chem_pot3, xlim1, xlim2, '','allMus-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), 'Chemical Potential', 20, 20, 30, 8, 20, 30, 15,4 )

# xlim1,xlim2 =zoomlim
# strr=zommlimstr
# '''Plotting mfs from DICTRA output names, L, tt, xs, lim1 = -10, lim2 = -10, title = '', file_name = 'all_values', ylab = "fractions", fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, wlsize=3'''
# all_x_plotter(elnames, vmp3, t3, mf3, xlim1, xlim2 ,'', 'mfs-{}-{:3.0f}-sec'.format(strr,t3), 'Mole Fraction', 20, 20, 30, 8, 20, 30, 20,3 )

# '''Plotting mfs 0-last from DICTRA output x1, x2, L1, L2, tt1, tt2, names, lim1 = -10, lim2 = -10, title ='', file_name='', fsize = 20, lsize = 20, tsize = 20, bins = 6, tksize = 20, stsize=20, lgsize=20, lwsize=20):'''
# plot_allx_2ts(mf3, mf1, vmp3, vmp1, t1, t3, elnames, xlim1, xlim2, '', 'mfs-{}-{:3.0f}-{:.0f}-sec'.format(strr,t3,t1),20, 20, 30, 8, 20, 30, 15,4)


# '''Plotting log10 ac SER activities postprocessed'''
# xlim1,xlim2 =zoomlim
# strr=zommlimstr

# '''Plotting log10 ac SER activities postprocessed'''
# all_x_plotter_log10(elnames, vmp3, t3, acs_SER, xlim1, xlim2, '','log10-acs-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), 'log10(Activity) SER', 20, 20, 30, 8, 20, 30, 15,3 )

# '''Plotting log10 Mu activities postprocessed'''
# all_x_plotter_log10(elnames, vmp3, t3, -1*chem_pot3, xlim1, xlim2, '','log10-allMus-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), '-log10(Chemical Potential)', 20, 20, 30, 8, 20, 30, 15,3 )


# '''Plotting ac SER activities postprocessed'''
# all_x_plotter(elnames, vmp3, t3, acs_SER, xlim1, xlim2, '','acs-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), 'Activity SER', 20, 20, 30, 8, 20, 30, 15,3 )


#plot_tc_corrected_result_phf_all_phases(npm_pp_corrected, xph_pp_corrected, tidx3, ts, vmp3, xlim1, xlim2, 20, 20, 30, 10, 20, 30, 20, 3, 'corrected-npm-{}'.format(zommlimstr)  )

# xlim1,xlim2=zoomlim
# strr=zommlimstr

# '''Plotting ac SER activities postprocessed'''
# all_x_plotter(['C'], vmp3, t3, acs_SER, xlim1, xlim2, '','acC-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), 'Activity SER', 20, 20, 30, 8, 20, 30, 15,3 )

# '''Plotting Mu '''
# all_x_plotter(['C'], vmp3, t3, chem_pot3, xlim1, xlim2, '','allMus-C-SER-{}-{:3.0f}-sec-DICTRA'.format(strr,t3), 'Chemical Potential', 20, 20, 30, 8, 20, 30, 15,3 )


# In[ ]:




