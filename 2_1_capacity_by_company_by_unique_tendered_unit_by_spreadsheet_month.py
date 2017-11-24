#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 17:44:10 2017

@author: alexk
"""

import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import cm as cmp
import sys

#%%
base_dir = '/'.join(os.getcwd().split('/')[0:-1])
df = pd.read_csv(os.path.join(base_dir, 'combined csvs', 'processed_data.csv'))
#%%
df.sort_values(by=['Tender Application Date', 'Company Name', 'Tender Number'], \
               inplace=True, ascending=[False, False, False])

#%%
dups = []
for date in df['Tender Application Date'].unique():
    indx = np.where(df['Tender Application Date'] == date)[0]
    df_sub = df.iloc[indx, :]
    dups.append(df_sub.index[df_sub['Tendered Unit      (BMU/Unit ID)'].duplicated(keep='first')])
dups = np.hstack(dups)

df = df.drop(dups)

#%%
df.reset_index(drop=True, inplace=True)

indxs = np.where(pd.isnull(df['Company Name']))[0]
df.loc[indxs, 'Company Name'] = df['Tender unit abr'].iloc[indxs]

for i, cname in enumerate(df['Company Name']):
    name = cname.split(' (_inferred)')[0]
    df.loc[i, 'Company Name'] = name

df.to_csv('2_1_filter_result.csv')

#%%
d = {}
for sh_date in df['Tender Application Date'].unique():
    indx = np.where(df['Tender Application Date'] == sh_date)[0]
    df_l = df.iloc[indx, :]   #copy data of interest
    #getting unique tendered unit values
    
    for cname in df_l['Company Name'].unique():
        print(cname)
        indxs  =np.where(df_l['Company Name']==cname)[0]
        print(indxs)
        data = df_l.iloc[indxs, :]

        if cname not in d:  #initialise the dictionary
            d[cname] = {}

        d[cname]['-'.join(str(sh_date).split('-')[0:2]) + ' -p'] = \
            np.sum(data['Dynamic Providers Only: Primary Response (max.) @ 0.5Hz (MW)'].values.astype(float))
        d[cname]['-'.join(str(sh_date).split('-')[0:2]) + ' -s'] = np.sum(data\
            ['Dynamic Providers Only: Secondary Response (max.) @ 0.5/0.5Hz (MW)'].values.astype(float))
        d[cname]['-'.join(str(sh_date).split('-')[0:2]) + ' -h'] = np.sum(data\
            ['Dynamic Providers Only: High Frequency Response (max.) @ 0.5Hz (MW)'].values.astype(float))
#%%
d = pd.DataFrame(d)
sys.exit()
#%%

lis = np.arange(0, 90).reshape([9, 10])
all_del = []
for i in np.arange(0, 9):
    df_s = d.iloc[lis[i], :]
    df_s = df_s.dropna(axis=1, how='all')   #remove columns containing only nan

    dele = []   #REMOVE COLUMNS IF all zeros present
    for col in list(df_s):
        col_vals = df_s[col].iloc[:].values
        if np.nansum(col_vals) == 0:
            dele.append(col)
            all_del.append(dele)

    df_s.drop(labels=dele, axis=1, inplace=True)
    
    f = plt.figure(figsize=[20, 10])
    plt.title('Monthly Bid For Capacity by Company', color='black')
    df_s.plot(kind='bar', ax=f.gca(), stacked=True)
    plt.legend(loc='best', bbox_to_anchor=(1.0, 0.5))
    plt.show()
    plt.savefig('-'.join(df_s.index[0].split('-')[0:2]) + ' .png')
#%%

color_used = []
colors = np.array(dir(cmp))
for color in colors:
    if ('__' not in color) and ('LUTSIZE' not in color): 
        color_used.append(color)

#%%

for color in color_used[40:60]:
    try:
        df_s = d.iloc[:]
        df_s=df_s.dropna(axis=1,how='all')   #remove columns containing only nan
        
        colormap2 = cmp.get_cmap(color)
        df_s.to_csv('2_1 all plot data.csv')
        f = plt.figure(figsize=[20, 10])
        ax = f.gca()
        df_s.plot(kind='bar', ax=ax, stacked=True, cmap=colormap2)
        plt.title(color+ ' Monthly Bid For Capacity by Company', color='black')
        plt.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        plt.ylabel('Total Capacity MW')
        plt.show()
    except:
        pass
#%%
