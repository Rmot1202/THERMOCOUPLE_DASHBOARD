# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 11:04:27 2018

@author: andrea.marcon
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
plt.close('all')
#T_limit should be set 10 degrees below setpoint
Furnace = ('A')
T_limit = 200
folder = ('Downloads') #Downloaded or Recorded
file_name = ('TUS_FA_260608_134147')
plot_title = ("F"+str(Furnace)+" - Furnace Response Time - "+str(T_limit)+"°C - "+file_name[7:13])

#os.chdir(r"\\ccam-filer-07\Docs\CCAM\Research\Directed\D-320\Working-Local\TUS Heat up rates\F"+str(Furnace)+"\"+folder)

os.chdir("C:\\Users\\raven.mott\\Downloads")
df = pd.read_csv(file_name+'.txt',sep="\t", header=1)
print(df)
df.columns = ["hour", "minute", "second", "T_outlet", "T_center", "T_inlet", "T4"]
sampling_freq = 5

df.insert(3, "time", 0)
df.insert(7, "LL", T_limit)
df.insert(8, "UL", T_limit+20)

#%% Find response time
def R(x):
    i=x[x > 50].index[0]    
    f=x[x > T_limit].index[0]
    return (f-i)

for i in range(0,len(df)):
    df.loc[i,'time']  = 1/sampling_freq*i

time_out=round(R(df.T_outlet)/sampling_freq)
time_ctr=round(R(df.T_center)/sampling_freq)
time_in=round(R(df.T_inlet)/sampling_freq)



#%% Plot
ax1 = df.plot(x="time", y=["T_outlet", "T_center", "T_inlet","LL"], color=['b','r','m','silver'])
ax1.set_ylabel('Temperature (°C)')
ax1.set_xlabel('Time (s)')
plt.ylim(0,1000)
plt.xlim(0,time_out+150)
plt.xticks(np.arange(0, time_out+150, 60),rotation=45)
plt.yticks(np.arange(50, T_limit+100, 100))
plt.title(plot_title)
text_x = time_out-300#380
text_bottom = 350

ax1.text(text_x-70, text_bottom+460, 'Final temperature:').set_weight('bold')
ax1.text(text_x-60, text_bottom+400, 'Inlet=%i °C' %df['T_inlet'].iat[-1])
ax1.text(text_x-60, text_bottom+340, 'Center=%i °C' %df['T_center'].iat[-1])
ax1.text(text_x-60, text_bottom+280, 'Outlet=%i °C' %df['T_outlet'].iat[-1])

ax1.text(text_x-70, text_bottom+190, 'Response time:').set_weight('bold')
ax1.text(text_x-60, text_bottom+120, 'Inlet=%i s' %time_in)
ax1.text(text_x-60, text_bottom+60, 'Center=%i s' %time_ctr)
ax1.text(text_x-60, text_bottom, 'Outlet=%i s' %time_out)
labels = ["Outlet (17.0\")","Center (25.0\")","Inlet (30.0\")","Limit: %i°C" %T_limit]
legend = ax1.legend(labels=labels, loc='lower right', shadow=True, fontsize='medium')
plt.tight_layout()
plt.savefig(file_name+'_Response_Time.png',format='png', dpi=600)

#%%

del i, file_name, folder, labels, plot_title, text_x, text_bottom, sampling_freq