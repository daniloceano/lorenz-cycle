#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 16:32:27 2022

@author: daniloceano
"""

import pandas as pd
import argparse
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits import mplot3d
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import cmocean
import glob


def MarkerSizeKe(df,flag):
    
    msizes = [200,400,600,800,1000]
    
    if flag == 1 or flag ==3:
        intervals = [3e5,4e5,5e5,6e5]
        data = df['Ke']
        title = 'Eddy Kinect\n    Energy\n(Ke - '+r' $J\,m^{-2})$'
    elif flag == 2:
        intervals = [1e5,1.75e5,2.25e5,3e5]
        data = df['Ae']
        title = 'Eddy Potential\n      Energy\n(Ae - '+r' $J\,m^{-2})$'

    sizes = []
    for val in data:
        if val <= intervals[0]:
            sizes.append(msizes[0])
        elif val > intervals[0] and val <= intervals[1]:
            sizes.append(msizes[1])
        elif val > intervals[1] and val <= intervals[2]:
            sizes.append(msizes[2])
        elif val > intervals[2] and val <= intervals[3]:
            sizes.append(msizes[3])
        else:
            sizes.append(msizes[4])
    df['sizes'] = sizes
    
    # Plot legend
    labels = ['< '+str(intervals[0]),
              '< '+str(intervals[1]),
              '< '+str(intervals[2]),
              '< '+str(intervals[3]),
              '> '+str(intervals[3])]
    l1 = plt.scatter([],[],c='k', s=msizes[0],label=labels[0])
    l2 = plt.scatter([],[], c='k', s=msizes[1],label=labels[1])
    l3 = plt.scatter([],[],c='k', s=msizes[2],label=labels[2])
    l4 = plt.scatter([],[],c='k', s=msizes[3],label=labels[3])
    l5 = plt.scatter([],[],c='k', s=msizes[4],label=labels[4])
    leg = plt.legend([l1, l2, l3, l4, l5], labels, ncol=1, frameon=False,
                     fontsize=10, handlelength = 0.3, handleheight = 4,
                     borderpad = 1.5, scatteryoffsets = [0.1], framealpha = 1,
                handletextpad=1.5, title=title,
                scatterpoints = 1, loc = 1,
                bbox_to_anchor=(0.73, -0.57, 0.5, 1),labelcolor = '#383838')
    leg._legend_box.align = "center"
    plt.setp(leg.get_title(), color='#383838')
    plt.setp(leg.get_title(),fontsize=12)
    for i in range(len(leg.legendHandles)):
        leg.legendHandles[i].set_color('#383838')
        leg.legendHandles[i].set_edgecolor('gray')
    
    return df

def LorenzPhaseSpace(flag):
    
    '''
    flag == 1:
        Will produce Ck x Ca x Ge plots
    flag == 2:
        Will produce Ce x Ca x Ge+BAe plots
    flasg == 3:
        Will produce Ck x Ce x BKe+RKe plots
    '''
    
    Ca = smoothed['Ca']
    Ce = smoothed['Ce']
    Ck = smoothed['Ck']
    Ge = smoothed['Ge']
    RAe = smoothed['Ge']+smoothed['BAe']
    Re = smoothed['RKe']+smoothed['BKe']
    smoothed['Rae'], smoothed['Re'] = RAe, Re
    
    plt.close('all')
    fig = plt.figure(figsize=(10,10))
    # plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(right=0.85)
    # plt.gcf().subplots_adjust(left=0.135)
    ax = plt.gca()
    
    # Line plot
    if flag == 1:
        ax.plot(Ck,Ca,'-',c='gray',zorder=2,linewidth=3)
    elif flag == 2:
        ax.plot(Ce,Ca,'-',c='gray',zorder=2,linewidth=3)
    elif flag == 3:
        ax.plot(Ck,Ce,'-',c='gray',zorder=2,linewidth=3)
    
    # Scatter plot
    s = MarkerSizeKe(smoothed,flag)['sizes']

    # Plot limits
    if flag == 1:
        ax.set_xlim(-24,24)
        ax.set_ylim(-7,7)
        norm = colors.TwoSlopeNorm(vmin=-7, vcenter=0, vmax=15)
        dots = ax.scatter(Ck,Ca,c=Ge,cmap=cmocean.cm.curl,s=s,zorder=100,
                        edgecolors='grey', norm=norm)
        # Labels
        ax.set_xlabel('Conversion from zonal to eddy Kinetic Energy (Ck - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        ax.set_ylabel('Conversion from zonal to eddy Potential Energy (Ca - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        
    elif flag == 2:
        ax.set_xlim(-18,18)
        ax.set_ylim(-7,7)
        norm = colors.TwoSlopeNorm(vmin=-7, vcenter=0, vmax=15)
        dots = ax.scatter(Ce,Ca,c=RAe,cmap=cmocean.cm.curl,s=s,zorder=100,
                        edgecolors='grey', norm=norm)
        # Labels
        ax.set_xlabel('Conversion from eddy Potential to Kinectic Energy (Ce - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        ax.set_ylabel('Conversion from zonal to eddy Potential Energy (Ca - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        
    elif flag == 3:
        ax.set_xlim(-24,24)
        ax.set_ylim(-18,18)
        norm = colors.TwoSlopeNorm(vmin=-40, vcenter=0, vmax=5)
        dots = ax.scatter(Ck,Ce,c=Re,cmap=cmocean.cm.curl,s=s,zorder=100,
                        edgecolors='grey', norm=norm)
        # Labels
        ax.set_xlabel('Conversion from zonal to eddy Kinetic Energy (Ck - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        ax.set_ylabel('Conversion from eddy Potential to Kinectic Energy (Ce - '+r' $W\,m^{-2})$',
                      fontsize=12,labelpad=40,c='#383838')
        
    # Gradient lines in the center of the plot
    alpha, offsetalpha = 0.3, 20
    lw, c = 2.5, '#383838'
    if flag == 1:
        offsetx, offsety = 16, 4.3
    elif flag == 2:
        offsetx, offsety = 16, 5.7
    elif flag == 3:
        offsetx, offsety = 7, 4.3
    for i in range(7):
        ax.axhline(y=0+(i/offsetx),zorder=0+(i/5),linewidth=lw,
                   alpha=alpha-(i/offsetalpha),c=c)
        ax.axhline(y=0-(i/offsetx),zorder=0+(i/5),linewidth=lw,
                   alpha=alpha-(i/offsetalpha),c=c)
        ax.axvline(x=0+(i/offsety),zorder=0+(i/5),linewidth=lw,
               alpha=alpha-(i/offsetalpha),c=c)
        ax.axvline(x=0-(i/offsety),zorder=0+(i/5),linewidth=lw,
               alpha=alpha-(i/offsetalpha),c=c)
        
   
    # Colorbar
    if flag == 1:
        cax = fig.add_axes([ax.get_position().x1+0.01,
                        ax.get_position().y0+0.32,0.02,ax.get_position().height/1.74])
        cbar = plt.colorbar(dots, extend='both',cax=cax)
        cbar.ax.set_ylabel('Generation of eddy Potential Energy (Ge - '+r' $W\,m^{-2})$',
                       rotation=270,fontsize=12,verticalalignment='bottom',
                       c='#383838',labelpad=40)
    elif flag == 2:
        cax = fig.add_axes([ax.get_position().x1+0.01,
                        ax.get_position().y0+0.32,0.02,ax.get_position().height/1.74])
        cbar = plt.colorbar(dots, extend='both',cax=cax)
        cbar.ax.set_ylabel('Sources of eddy Potential Energy (Ge + BAe - '+r' $W\,m^{-2})$',
                       rotation=270,fontsize=12,verticalalignment='bottom',
                       c='#383838',labelpad=40)
    elif flag == 3:
        cax = fig.add_axes([ax.get_position().x1+0.01,
                        ax.get_position().y0+0.32,0.02,ax.get_position().height/1.74])
        cbar = plt.colorbar(dots, extend='both',cax=cax)
        cbar.ax.set_ylabel('Sinks of eddy Kinectic Energy (RKe + BKe - '+r' $W\,m^{-2})$',
                       rotation=270,fontsize=12,verticalalignment='bottom',
                       c='#383838',labelpad=40)
    for t in cbar.ax.get_yticklabels():
         t.set_fontsize(10)
        

    # Annotate plot
    plt.tick_params(labelsize=10)
    system = outfile.split('/')[-1].split('_')[0]
    datasource = outfile.split('/')[-1].split('_')[1]
    start, end = str(df['Datetime'][0]),str(df['Datetime'].iloc[-1]) 
    ax.text(0,1.1,'System: '+system+' - Data from: '+datasource,
            fontsize=16,c='#242424',horizontalalignment='left',
            transform=ax.transAxes)
    ax.text(0,1.06,'Start (A):',fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0,1.025,'End (Z):',fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0.14,1.06,start,fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0.14,1.025,end,fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    annotate_fs = 10
    if flag == 1:
        y_upper = 'Eddy is gaining potential energy \n from the mean flow'
        y_lower = 'Eddy is providing potential energy \n to the mean flow'
        x_left = 'Eddy is gaining kinetic energy \n from the mean flow'
        x_right = 'Eddy is providing kinetic energy \n to the mean flow'
        col_lower = 'Subisidence decreases \n eddy potential energy'
        col_upper = 'Latent heat release feeds \n eddy potential energy'
        lower_left = 'Barotropic instability'
        upper_left = 'Eddy growth by barotropic and\n baroclinic processes'
        lower_right = 'Eddy is feeding the local atmospheric circulation'
        upper_right = 'Gain of eddy potential energy\n via baroclinic processes'
    elif flag == 2:
        y_upper = 'Eddy is gaining potential energy \n from the mean flow'
        y_lower = 'Eddy is providing potential energy \n to the mean flow'
        x_left = 'Eddy is converting kinetic energy \n into potential energy'
        x_right = 'Eddy is converting potential energy \n into kinetic energy'
        col_lower = 'Destruction of eddy\n potential energy'
        col_upper = 'Creation of eddy\n potential energy'
        lower_left = 'Eddy lifting the local center of mass up'
        upper_left = 'Net gain of eddy potential energy'
        lower_right = 'Eddy center of mass being lowered'
        upper_right = 'Gain of eddy potential energy\n via baroclinic processes'
    elif flag == 3:
        y_upper =  'Eddy is converting potential energy \n into kinetic energy'
        y_lower = 'Eddy is converting kinetic energy \n into potential energy'
        x_left = 'Eddy is gaining kinetic energy \n from the mean flow'
        x_right = 'Eddy is providing kinetic energy \n to the mean flow'
        col_lower = 'Destruction of eddy\n kinetic energy'
        col_upper = 'Creation of eddy\n kinetic energy'
        lower_left = 'Pure barotropic instability'
        upper_left = 'Barotropic and baroclinic \n instabilities'
        lower_right = 'Eddy dissipation'
        upper_right = 'Pure baroclinic instability'
        
    ax.text(-0.08,0.12,y_lower,
            rotation=90,fontsize=annotate_fs,horizontalalignment='center',c='#19616C',
            transform=ax.transAxes)
    ax.text(-0.08,0.65,y_upper,
            rotation=90,fontsize=annotate_fs,horizontalalignment='center',c='#CF6D66',
            transform=ax.transAxes)
    ax.text(0.22,-0.08,x_left,
            fontsize=annotate_fs,horizontalalignment='center',c='#CF6D66',
            transform=ax.transAxes)
    ax.text(0.75,-0.08,x_right,
            fontsize=annotate_fs,horizontalalignment='center',c='#19616C',
            transform=ax.transAxes)
    ax.text(1.13,0.51,col_lower,
            rotation=270,fontsize=annotate_fs,horizontalalignment='center',c='#19616C'
            ,transform=ax.transAxes)
    ax.text(1.13,0.75,col_upper,
            rotation=270,fontsize=annotate_fs,horizontalalignment='center',c='#CF6D66',
            transform=ax.transAxes)
    ax.text(0.22,0.03,lower_left,
            fontsize=annotate_fs,horizontalalignment='center',c='#660066',
            verticalalignment='center', transform=ax.transAxes)
    ax.text(0.22,0.97,upper_left,
            fontsize=annotate_fs,horizontalalignment='center',c='#800000',
            verticalalignment='center', transform=ax.transAxes)
    ax.text(0.75,0.03,lower_right,
            fontsize=annotate_fs,horizontalalignment='center',c='#000066',
            verticalalignment='center', transform=ax.transAxes)
    ax.text(0.75,0.97,upper_right,
            fontsize=annotate_fs,horizontalalignment='center',c='#660066',
            verticalalignment='center', transform=ax.transAxes)
    
    # Marking start and end of the system
    if flag == 1:
        ax.text(Ck[0], Ca[0],'A',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
        ax.text(Ck.iloc[-1], Ca.iloc[-1], 'Z',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
    elif flag == 2:
        ax.text(Ce[0], Ca[0],'A',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
        ax.text(Ce.iloc[-1], Ca.iloc[-1], 'Z',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
    elif flag == 3:
        ax.text(Ck[0], Ce[0],'A',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
        ax.text(Ck.iloc[-1], Ce.iloc[-1], 'Z',
                zorder=101,fontsize=22,horizontalalignment='center',
                verticalalignment='center')
        
    fname = FigsDir+'LPS'+str(flag)+'.png'
    plt.savefig(fname,dpi=500)
    print(fname+' created!')
    
def LorenzPhaseSpace_zoomed():
    
    Ca = smoothed['Ca']
    Ck = smoothed['Ck']
    Ge = smoothed['Ge']
    
    plt.close('all')
    fig = plt.figure(figsize=(10,10))
    # plt.gcf().subplots_adjust(bottom=0.15)
    plt.gcf().subplots_adjust(right=0.85)
    # plt.gcf().subplots_adjust(left=0.135)
    ax = plt.gca()
    
    # Line plot
    ax.plot(Ck,Ca,'-',c='gray',zorder=2,linewidth=3)
    
    # Scatter plot
    s = MarkerSizeKe(smoothed)['sizes']

    # Plot limits
    ax.set_xlim(min(Ck)-1,max(Ck)+1)
    ax.set_ylim(min(Ca)-1,max(Ca)+1)
    norm = colors.TwoSlopeNorm(vmin=min(Ge), vcenter=0, vmax=max(Ge))
        
    dots = ax.scatter(Ck,Ca,c=Ge,cmap=cmocean.cm.curl,s=s,zorder=100,
                        edgecolors='grey', norm=norm)
    
    # Gradient lines in the center of the plot
    c,lw,alpha = '#383838',20,0.2
    ax.axhline(y=0,linewidth=lw,c=c,alpha=alpha,zorder=1)
    ax.axvline(x=0,linewidth=lw,c=c,alpha=alpha,zorder=1)
        
    # Labels
    ax.set_xlabel('Conversion from zonal to eddy Kinetic Energy (Ck - '+r' $W\,m^{-2})$',
                  fontsize=12,labelpad=10,c='#383838')
    ax.set_ylabel('Conversion from zonal to eddy Potential Energy (Ca - '+r' $W\,m^{-2})$',
                  fontsize=12,labelpad=10,c='#383838')
    plt.tick_params(labelsize=10)
    
    # Colorbar
    cax = fig.add_axes([ax.get_position().x1+0.01,
                        ax.get_position().y0+0.32,0.02,ax.get_position().height/1.74])
    cbar = plt.colorbar(dots, extend='both',cax=cax)
    cbar.ax.set_ylabel('Generation of eddy Potential Energy (Ge - '+r' $W\,m^{-2})$',
                       rotation=270,fontsize=12,verticalalignment='bottom',
                       c='#383838',labelpad=10)
    for t in cbar.ax.get_yticklabels():
         t.set_fontsize(10)

    # Annotate plot
    system = outfile.split('/')[-1].split('_')[0]
    datasource = outfile.split('/')[-1].split('_')[1]
    start, end = str(df['Datetime'][0]),str(df['Datetime'].iloc[-1]) 
    ax.text(0,1.1,'System: '+system+' - Data from: '+datasource,
            fontsize=16,c='#242424',horizontalalignment='left',
            transform=ax.transAxes)
    ax.text(0,1.06,'Start (A):',fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0,1.025,'End (Z):',fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0.14,1.06,start,fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    ax.text(0.14,1.025,end,fontsize=14,c='#242424',
            horizontalalignment='left',transform=ax.transAxes)
    
    # Marking start and end of the system
    ax.text(Ck[0], Ca[0],'A',
            zorder=101,fontsize=22,horizontalalignment='center',
            verticalalignment='center')
    ax.text(Ck.iloc[-1], Ca.iloc[-1], 'Z',
            zorder=101,fontsize=22,horizontalalignment='center',
            verticalalignment='center')
    
    fname = FigsDir+"LPS_zoom.png"
    plt.savefig(fname,dpi=500)
    print(fname+' created!')
    
    
    
if __name__ == "__main__":
 
    parser = argparse.ArgumentParser(description = "\
reads an CSV file with all terms from the Lorenz Energy Cycle \
  (as input from user) and make the deafult figures for the Lorenz energy cycle\
The transparecy in each box is set to be proportional to the energy tendency,\
  as well as the arrows are set to be proportional to the conversion rates.")
    parser.add_argument("outfile", help = "The .csv file containing the \
results from the main.py program.")

    args = parser.parse_args()
    outfile = args.outfile
    # outfile = '../LEC_Results/Reg1_NCEP-R2_60W30W42S17S/Reg1_NCEP-R2_60W30W42S17S.csv'
    # outfile = '../LEC_Results/Catarina_NCEP-R2_55W36W35S20S/Catarina_NCEP-R2_55W36W35S20S.csv' 
    ResultsSubDirectory = '/'.join(outfile.split('/')[:-1])
    FigsDir = ResultsSubDirectory+'/Figures/'
    
    df = pd.read_csv(outfile)
    df['Datetime'] = pd.to_datetime(df.Date) + pd.to_timedelta(df.Hour, unit='h')
    smoothed = df.groupby(pd.Grouper(key="Datetime", freq="12H")).mean()

    for i in range(3):
        LorenzPhaseSpace(i+1)
    # LorenzPhaseSpace_zoomed()