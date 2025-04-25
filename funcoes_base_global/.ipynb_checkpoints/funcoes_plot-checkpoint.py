#!/usr/bin/env python
# coding: utf-8

# In[6]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os
import json
from random import *
import matplotlib.pyplot as plt
from matplotlib.dates import (DAILY,HOURLY,MINUTELY,DateFormatter,
                              rrulewrapper, RRuleLocator, drange)
import numpy as np
import datetime
import seaborn as sns


# In[1]:


def plot_variables(df, variables_array, start_date, end_date, ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', error=False, rolling_time=0, 
                   abs_error=False, reference_line=[], figure_heigh=10, figure_width=30, ticks=[], legend=[]):
    
    df_filtered = df[ (df.index > start_date) & (df.index < end_date) ];
    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)
#             df_filtered = df_filtered[ df_filtered[variable]==0]
            
    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    if(error):
            if(abs_error):
                error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
                if(rolling_time>0):
                    plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time).mean(), linestyle='-', marker='o'); 
                else:
                    plt.plot_date(df_filtered.index, error_abs, linestyle='-', marker='o');
            else:
                error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
                if(rolling_time>0):
                    plt.plot_date(df_filtered.index, error_.rolling(rolling_time).mean(), linestyle='-', marker='o');
                else:
                    plt.plot_date(df_filtered.index, error_, linestyle='-', marker='o');
                 
    else:
        for variable in variables_array:
            plt.plot_date(df_filtered.index, df_filtered[variable], linestyle='-', marker='o');
            plt.title(variables_array[0])
            
            if(rolling_time>0):
                plt.plot_date(df_filtered.index, df_filtered[variable].rolling(rolling_time).mean(), linestyle='-', marker='o');

    if(error):        
        plt.title('Error')
    else:
        plt.title(variables_array[0])        
    if(len(reference_line)>0):
        for value in reference_line:
            ax.axhline(value, color='black', lw=2)

    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
         
            
    if(days_interval<2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)


    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)
    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)
    plt.show()

    return df_filtered


# In[ ]:


def plot_variables_rolling_base(df, variables_array, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', save_figure_dir='', error=False,  
                   abs_error=False, reference_line=[], figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           fail_dates_type = [], trasholds=[], absolute=False):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];
    df_filtered = df_filtered[variables_array]

    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)
#             df_filtered = df_filtered[ df_filtered[variable]==0]
            
    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    if(len(trasholds)>0):
        if(absolute):
            attention_trashold = trasholds[0]
            prefail_trashold = trasholds[1]
        else:
            base_line = df_filtered[variable].rolling(rolling_time[0]).mean().dropna().iloc[0]   
            attention_trashold = base_line*(1+trasholds[0])
            prefail_trashold = base_line*(1+trasholds[1])

    if(error):
            if(abs_error):
                error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
                plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time[0]).mean(), linestyle='-', marker='o'); 

            else:
                error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
                plt.plot_date(df_filtered.index, error_.rolling(rolling_time[0]).mean(), linestyle='-', marker='o');

                 
    else:
        for variable in variables_array:
              if(len(trasholds)>0):
                  good_interval = df_filtered[variable].rolling(rolling_time[0]).mean() > 0 & (df_filtered[variable].rolling(rolling_time[0]).mean() <= attention_trashold)
                  attention_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= attention_trashold) & (df_filtered[variable].rolling(rolling_time[0]).mean() <= prefail_trashold)
                  prefail_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= prefail_trashold)
                  plt.plot_date(df_filtered.index[good_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[good_interval], marker='o',color='green');
                  plt.plot_date(df_filtered.index[attention_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[attention_interval], marker='o',color='orange');
                  plt.plot_date(df_filtered.index[prefail_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[prefail_interval], marker='o',color='red');
              else:
                for i in rolling_time:
                    plt.plot_date(df_filtered.index, df_filtered[variable].rolling(i).mean(), linestyle='-', marker='o');
#                   plt.plot_date(df_filtered.index, df_filtered[variable], linestyle='-', marker='o');


    if(error):        
        plt.title('Error')
    else:
        plt.title(variables_array[0])         
    if(len(reference_line)>0):
        for value in reference_line:
            ax.axhline(value, color='green', lw=2)

    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)

        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0,1)
            plt.text(d,ymin+position*(ymax-ymin)/2,fail_dates[date])
            
    for date in fail_dates_type:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('1 days'), color='yellow', alpha=0.5)
    
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

            
    if(len(trasholds)>0):
        if(absolute):
            ax.axhline(trasholds[0], color='orange', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[0]), color='orange', lw=2)
    if(len(trasholds)>1):
        if(absolute):
            ax.axhline(trasholds[1], color='red', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[1]), color='red', lw=2)

    if(len(save_figure_name)>0):
        if(len(save_figure_dir)>0):
            plt.savefig(save_figure_dir+save_figure_name, dpi=350)
        else:
            plt.savefig(save_figure_name, dpi=350)
        
    plt.show()

    return df_filtered


# In[1]:


def plot_variables_rolling_V2(df, variables_array, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', save_figure_dir='', error=False,  
                   abs_error=False, reference_line=[], figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           fail_dates_type = {}, trasholds=[], absolute=False):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];
    df_filtered = df_filtered[variables_array]

    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)
#             df_filtered = df_filtered[ df_filtered[variable]==0]
            
    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    if(len(trasholds)>0):
        base_line = df_filtered[variable].rolling(rolling_time[0]).mean().dropna().iloc[0]   
        if(absolute):
            attention_trashold = trasholds[0]
            prefail_trashold = trasholds[1]
        else:
            attention_trashold = base_line*(1+trasholds[0])
            prefail_trashold = base_line*(1+trasholds[1])

    if(error):
            if(abs_error):
                error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
                plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time[0]).mean(), linestyle='-', marker='o'); 

            else:
                error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
                plt.plot_date(df_filtered.index, error_.rolling(rolling_time[0]).mean(), linestyle='-', marker='o');

                 
    else:
        for variable in variables_array:
              if(len(trasholds)>0):
                  good_interval = df_filtered[variable].rolling(rolling_time[0]).mean() > 0 & (df_filtered[variable].rolling(rolling_time[0]).mean() <= attention_trashold)
                  attention_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= attention_trashold) & (df_filtered[variable].rolling(rolling_time[0]).mean() <= prefail_trashold)
                  prefail_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= prefail_trashold)
                  plt.plot_date(df_filtered.index[good_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[good_interval], marker='o',color='green');
                  plt.plot_date(df_filtered.index[attention_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[attention_interval], marker='o',color='orange');
                  plt.plot_date(df_filtered.index[prefail_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[prefail_interval], marker='o',color='red');
              else:
                for i in rolling_time:
                    plt.plot_date(df_filtered.index, df_filtered[variable].rolling(i).mean(), linestyle='-', marker='o');
#                   plt.plot_date(df_filtered.index, df_filtered[variable], linestyle='-', marker='o');


    if(error):        
        plt.title('Error')
    else:
        plt.title(variables_array[0])         
    if(len(reference_line)>0):
        for value in reference_line:
            ax.axhline(value, color='green', lw=2)

    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)

        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0.7,0.9)
            plt.text(d,ymin+position*(ymax-ymin),fail_dates[date],color='blue',fontsize=20)
            
            
    for date in fail_dates_type:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='black', alpha=0.5)
            position = uniform(0.7,0.9)
            plt.text(d,ymin+position*(ymax-ymin),fail_dates_type[date], color='blue',fontsize=20)
    
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

            
    if(len(trasholds)>0):
        if(absolute):
            ax.axhline(trasholds[0], color='orange', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[0]), color='orange', lw=2)
    if(len(trasholds)>1):
        if(absolute):
            ax.axhline(trasholds[1], color='red', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[1]), color='red', lw=2)

    if(len(save_figure_name)>0):
        if(len(save_figure_dir)>0):
            plt.savefig(save_figure_dir+save_figure_name, dpi=350)
        else:
            plt.savefig(save_figure_name, dpi=350)
        
    plt.show()

    return df_filtered


# In[ ]:


def plot_variables_rolling_V2(df, variables_array, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', error=False,  
                   abs_error=False, reference_line=[], figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           fail_dates_type = {}, trasholds=[], absolute=False):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];
    df_filtered = df_filtered[variables_array]

    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)
#             df_filtered = df_filtered[ df_filtered[variable]==0]
            
    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    if(len(trasholds)>0):
        base_line = df_filtered[variable].rolling(rolling_time[0]).mean().dropna().iloc[0]   
        if(absolute):
            attention_trashold = trasholds[0]
            prefail_trashold = trasholds[1]
        else:
            attention_trashold = base_line*(1+trasholds[0])
            prefail_trashold = base_line*(1+trasholds[1])

    if(error):
            if(abs_error):
                error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
                plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time[0]).mean(), linestyle='-', marker='o'); 

            else:
                error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
                plt.plot_date(df_filtered.index, error_.rolling(rolling_time[0]).mean(), linestyle='-', marker='o');

                 
    else:
        for variable in variables_array:
              if(len(trasholds)>0):
                  good_interval = df_filtered[variable].rolling(rolling_time[0]).mean() > 0 & (df_filtered[variable].rolling(rolling_time[0]).mean() <= attention_trashold)
                  attention_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= attention_trashold) & (df_filtered[variable].rolling(rolling_time[0]).mean() <= prefail_trashold)
                  prefail_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= prefail_trashold)
                  plt.plot_date(df_filtered.index[good_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[good_interval], marker='o',color='green');
                  plt.plot_date(df_filtered.index[attention_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[attention_interval], marker='o',color='orange');
                  plt.plot_date(df_filtered.index[prefail_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[prefail_interval], marker='o',color='red');
              else:
                for i in rolling_time:
                    plt.plot_date(df_filtered.index, df_filtered[variable].rolling(i).mean(), linestyle='-', marker='o');
#                   plt.plot_date(df_filtered.index, df_filtered[variable], linestyle='-', marker='o');


    if(error):        
        plt.title('Error')
    else:
        plt.title(variables_array[0])         
    if(len(reference_line)>0):
        for value in reference_line:
            ax.axhline(value, color='green', lw=2)

    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)

        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0.7,0.9)
            plt.text(d,ymin+position*(ymax-ymin),fail_dates[date],color='blue',fontsize=20)
            
            
    for date in fail_dates_type:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='black', alpha=0.5)
            position = uniform(0.7,0.9)
            plt.text(d,ymin+position*(ymax-ymin),fail_dates_type[date], color='blue',fontsize=20)
    
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

            
    if(len(trasholds)>0):
        if(absolute):
            ax.axhline(trasholds[0], color='orange', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[0]), color='orange', lw=2)
    if(len(trasholds)>1):
        if(absolute):
            ax.axhline(trasholds[1], color='red', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[1]), color='red', lw=2)

    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)
        
    plt.show()

    return df_filtered


# In[4]:


def plot_variables_rolling_gaussian_based(df, variables_array, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', error=False,  
                   abs_error=False, reference_line=[], figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           fail_dates_type = {}, trasholds=[], absolute=False):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];
    df_filtered = df_filtered[variables_array]

    
    print(df_filtered.shape)
    for variable in variables_array:
        if 'MODE' in variable:
            df_filtered[variable] = df_filtered[variable].apply(lambda d: 1 if d=="CAS" else 0)
#             df_filtered = df_filtered[ df_filtered[variable]==0]
            
    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    if(len(trasholds)>0):
        base_line = df_filtered[variable].rolling(rolling_time[0]).mean().dropna().iloc[0]   
        if(absolute):
            attention_trashold = trasholds[0]
            prefail_trashold = trasholds[1]
        else:
            attention_trashold = base_line*(1+trasholds[0])
            prefail_trashold = base_line*(1+trasholds[1])

    if(error):
            if(abs_error):
                error_abs = abs(df_filtered[variables_array[0]]-df_filtered[variables_array[1]])
                plt.plot_date(df_filtered.index, error_abs.rolling(rolling_time[0]).mean(), linestyle='-', marker='o'); 

            else:
                error_ = df_filtered[variables_array[0]]-df_filtered[variables_array[1]]
                plt.plot_date(df_filtered.index, error_.rolling(rolling_time[0]).mean(), linestyle='-', marker='o');

                 
    else:
        for variable in variables_array:
              if(len(trasholds)>0):
                  good_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() <= attention_trashold)
                  attention_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= attention_trashold) & (df_filtered[variable].rolling(rolling_time[0]).mean() <= prefail_trashold)
                  prefail_interval = (df_filtered[variable].rolling(rolling_time[0]).mean() >= prefail_trashold)
                  plt.plot_date(df_filtered.index[good_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[good_interval], marker='o',color='green');
                  plt.plot_date(df_filtered.index[attention_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[attention_interval], marker='o',color='orange');
                  plt.plot_date(df_filtered.index[prefail_interval], df_filtered[variable].rolling(rolling_time[0]).mean()[prefail_interval], marker='o',color='red');
              else:
                for i in rolling_time:
                    plt.plot_date(df_filtered.index, df_filtered[variable].rolling(i).mean(), linestyle='-', marker='o');
#                   plt.plot_date(df_filtered.index, df_filtered[variable], linestyle='-', marker='o');


    if(error):        
        plt.title('Error')
    else:
        plt.title(variables_array[0])         
    if(len(reference_line)>0):
        for value in reference_line:
            ax.axhline(value, color='green', lw=2)

    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)

        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0,1)
            plt.text(d,ymin+position*(ymax-ymin)/2,fail_dates[date])
            
    for date in fail_dates_type:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('1 days'), color='yellow', alpha=0.5)
            
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

            
    if(len(trasholds)>0):
        if(absolute):
            ax.axhline(trasholds[0], color='orange', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[0]), color='orange', lw=2)
    if(len(trasholds)>1):
        if(absolute):
            ax.axhline(trasholds[1], color='red', lw=2)
        else:
            ax.axhline(base_line*(1+trasholds[1]), color='red', lw=2)

    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)
        
    plt.show()

    return df_filtered


# In[3]:


def correlacao_var(df,size,title, save_figure_name = ''):
    corr = df.corr()
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True
 
    # Set up the matplotlib figure
    
    f, ax = plt.subplots(figsize=size)
    #f.title(title)
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)
 
    # Draw the heatmap with the mask and correct aspect ratio
    sns_plot = sns.heatmap(corr, mask=mask, cmap=cmap, vmax=1, center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": .5},annot = True)
    
    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)


# In[1]:


def plot_twin_result_gaussian_based(df, variable, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           trasholds=[]):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];

    print(df_filtered.shape)

    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    
    attention_trashold = trasholds[0]
    prefail_trashold = trasholds[1]


        
    df_filtered_rolling = df_filtered[[variable]].rolling(rolling_time).mean().dropna()  
    
   

    df_filtered_rolling['Result'] = np.where( df_filtered_rolling[[variable]]>=prefail_trashold, 2, np.where( (df_filtered_rolling[[variable]]>=attention_trashold), 1, 0) )

    good_interval = df_filtered_rolling['Result'] == 0
    attention_interval = df_filtered_rolling['Result'] == 1         
    prefail_interval = df_filtered_rolling['Result'] == 2       

    
    plt.plot_date(df_filtered_rolling['Result'].index[good_interval], df_filtered_rolling['Result'][good_interval], marker='o',color='green');
    plt.plot_date(df_filtered_rolling['Result'].index[attention_interval], df_filtered_rolling['Result'][attention_interval], marker='o',color='orange');
    plt.plot_date(df_filtered_rolling['Result'].index[prefail_interval], df_filtered_rolling['Result'][prefail_interval], marker='o',color='red');
            
    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)
    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)
        
        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            min_date_fail = d-pd.Timedelta('45 days')
            max_date_fail = d
#             if( np.any(df_filtered_rolling[ (df_filtered_rolling.index>= min_date_fail) & (df_filtered_rolling.index<= max_date_fail)].Result>0)):                
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0,1)
            plt.text(d,ymin+position*(ymax-ymin)/2,fail_dates[date])

    
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

    plt.show()

    return df_filtered


# In[ ]:


def plot_twin_result(df, variable, start_date, end_date, rolling_time, train_start_date='', train_end_date='', ylabel='', days_interval=2,
                   minutes_interval=180, save_figure_name = '', figure_heigh=10, figure_width=30, ticks=[], legend=[], fail_dates={},
                           fail_dates_type = [], trasholds=[]):
            
    df_filtered = df[ (df.index >= start_date) & (df.index <= end_date) ];

    print(df_filtered.shape)

    rule = rrulewrapper(DAILY, interval=days_interval)
    minor_rule = rrulewrapper(MINUTELY, interval=minutes_interval)

    loc = RRuleLocator(rule)
    formatter = DateFormatter('%d-%m-%Y')
    minor_loc = RRuleLocator(minor_rule)
    minor_formatter = DateFormatter('%H:%M')

    fig, ax = plt.subplots();
    xs = {}
    series = {}
    smask = {}
    df_return = pd.DataFrame()
    
    
    attention_trashold = trasholds[0]
    prefail_trashold = trasholds[1]

        
    df_filtered_rolling = df_filtered[[variable]].rolling(rolling_time).mean().dropna()  
    
   

    df_filtered_rolling['Result'] = np.where( df_filtered_rolling[[variable]]>=prefail_trashold, 2, np.where( (df_filtered_rolling[[variable]]>=attention_trashold), 1, 0) )
  
    good_interval = df_filtered_rolling['Result'] == 0
    attention_interval = df_filtered_rolling['Result'] == 1         
    prefail_interval = df_filtered_rolling['Result'] == 2       

    
    plt.plot_date(df_filtered_rolling['Result'].index[good_interval], df_filtered_rolling['Result'][good_interval], marker='o',color='green');
    plt.plot_date(df_filtered_rolling['Result'].index[attention_interval], df_filtered_rolling['Result'][attention_interval], marker='o',color='orange');
    plt.plot_date(df_filtered_rolling['Result'].index[prefail_interval], df_filtered_rolling['Result'][prefail_interval], marker='o',color='red');
            
    if(len(ticks)>2):
        ax.set_yticks(np.arange(ticks[0], ticks[1], ticks[2]))
        
    if(len(legend)>0):
        ax.legend(legend)
            
    if(days_interval<=2):
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=60)
        
        ax.xaxis.set_minor_locator(minor_loc);
        ax.xaxis.set_minor_formatter(minor_formatter);
        ax.xaxis.set_tick_params(which='minor', labelsize=10, rotation=90)
    else:
        ax.xaxis.set_major_locator(loc);
        ax.xaxis.set_major_formatter(formatter); 
        ax.xaxis.set_tick_params(which='major', rotation=90, labelsize=10, pad=0)

    fig.set_figheight(figure_heigh)
    fig.set_figwidth(figure_width)
    plt.grid(True)
    
    if(len(ylabel)>0):
        plt.ylabel(ylabel)
    if(len(save_figure_name)>0):
        plt.savefig(save_figure_name, dpi=500)
        
        
    ymin, ymax = ax.get_ylim()
    for date in fail_dates:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='grey', alpha=0.5)
            position = uniform(0,1)
            plt.text(d,ymin+position*(ymax-ymin)/2,fail_dates[date])
            
    for date in fail_dates_type:
        d = pd.to_datetime(date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(start_date)) and (d <= pd.to_datetime(end_date) )):
            plt.axvspan(d, d+pd.Timedelta('5 days'), color='yellow', alpha=0.5)
    
    if( len(train_start_date) >0 and len(train_end_date) > 0):
         if( (pd.to_datetime(train_start_date)>=pd.to_datetime(start_date)) and (pd.to_datetime(train_end_date) <= pd.to_datetime(end_date) )):
             plt.axvspan(train_start_date, train_end_date, color='green', alpha=0.1)

    plt.show()

    return df_filtered


# In[1]:


def describe_twin_result(dftrain,dftest,trasholds, test_start, test_end, rolling_time, variable, fail_dates,dias_falsos_positivos=45):
    
    attention_trashold = trasholds[0]
    prefail_trashold = trasholds[1]
   
    df_filtered = dftest[ (dftest.index >= test_start) & (dftest.index <= test_end) ];
    df_filtered_rolling = df_filtered[[variable]].rolling(rolling_time).mean().dropna()  
    df_filtered_rolling['Result'] = np.where( df_filtered_rolling[[variable]]>=prefail_trashold, 2, np.where( (df_filtered_rolling[[variable]]>=attention_trashold), 1, 0) )
  
    good_interval = df_filtered_rolling['Result'] == 0
    attention_interval = df_filtered_rolling['Result'] == 1         
    prefail_interval = df_filtered_rolling['Result'] == 2       

    prediction_result = {}
    
    print('Tamanho do dataset de treino: {0}'.format(dftrain.shape[0]))
    print('Tamanho do dataset de teste: {0}'.format(dftest.shape[0]))
    print('Data de inicio de teste: {0}'.format(pd.to_datetime(test_start).strftime('%d/%m/%Y')))
    print('Data de fim de teste: {0}'.format(pd.to_datetime(test_end).strftime('%d/%m/%Y')))

    print('_____________________________________________________')
    fails_dataframe = []
    
    for fail_date in fail_dates:
        d = pd.to_datetime(fail_date , format="%d/%m/%Y")
        if( (d>=pd.to_datetime(test_start)) and (d <= pd.to_datetime(test_end) )):
            
            fail_start_region, fail_end_region = d-pd.to_timedelta(dias_falsos_positivos,unit='d'), d+pd.to_timedelta(15,unit='d')
            df_filtered = df_filtered_rolling[(df_filtered_rolling.index>fail_start_region) & (df_filtered_rolling.index<fail_end_region)]
            fails_dataframe.append(df_filtered)
            results = []
            if(df_filtered[df_filtered['Result']==1].shape[0]>0):              
                result_info = {}               
                result_info['severity'] = 'Warning'
                first_alarm_date = (df_filtered[df_filtered['Result']==1].head(1).index).strftime('%d/%m/%Y')[0]
                antecedence = ((d-df_filtered[df_filtered['Result']==1].head(1).index).days[0])  
                if(antecedence>0):
                    if(antecedence<1):
                        antecedence = ((d-df_filtered[df_filtered['Result']==1].head(1).index).astype('timedelta64[h]')[0])
                        antecedence = str(antecedence)+' h'
                    result_info['first_alarm_date'] = first_alarm_date
                    result_info['antecedence'] = antecedence                
                    results.append(result_info)

                
            if(df_filtered[df_filtered['Result']==2].shape[0]>0):              
                result_info = {}               
                result_info['severity'] = 'Pre Fail'
                first_alarm_date = (df_filtered[df_filtered['Result']==2].head(1).index).strftime('%d/%m/%Y')[0]
                antecedence = ((d-df_filtered[df_filtered['Result']==2].head(1).index).days[0]) 
                
                if(antecedence>0):
                    if(antecedence<1):
                        antecedence = ((d-df_filtered[df_filtered['Result']==2].head(1).index).astype('timedelta64[h]')[0])
                        antecedence = str(antecedence)+' h'
                    result_info['first_alarm_date'] = first_alarm_date
                    result_info['antecedence'] = antecedence                
                    results.append(result_info)
                                
            if(len(results)>0):
                prediction_result[fail_date] = results
                
                

    for prediction in prediction_result:
        print('-------------------------------------------')
        print('Data da falha: {0}'.format(prediction))
        for result in prediction_result[prediction]:
            print('----<>---') if len(prediction_result[prediction])>1 else 0
            print('Severidade do sinal: {0}'.format(result['severity']))
            print('Data do primeiro sinal: {0}'.format(result['first_alarm_date']))
            print('Número de dias anteriores a falha: {0}'.format(result['antecedence']))
    print('_____________________________________________________')  
    print('Numero de falhas pegas: {0}'.format(len(prediction_result)))
    print('_____________________________________________________')  
    fails_dataframe = pd.concat(fails_dataframe)
    false_positive_dataframe = df_filtered_rolling[~df_filtered_rolling.index.isin(fails_dataframe.index.tolist())]
    false_positive_dataframe = false_positive_dataframe[false_positive_dataframe['Result'].isin([1.0,2.0])]
    false_positive_warning = false_positive_dataframe[false_positive_dataframe['Result']==1].shape[0]
    false_positive_prefail = false_positive_dataframe[false_positive_dataframe['Result']==2].shape[0]
    
    
    print('Falsos positivos de degradacao: {0}'.format(false_positive_warning))
    print('Falsos positivos de pré-falha: {0}'.format(false_positive_prefail))
    
    print('Falsos positivos de degradacao:')
    print(false_positive_dataframe[false_positive_dataframe['Result']==1].index.strftime('%d/%m/%Y'))


    return false_positive_dataframe
    

    
                         


# In[6]:


def plot_distribution(data, start_date, end_date)  :  
    plt.suptitle('Variables Distributions')
    
    plt.figure(figsize=(19,4))
    plt.subplot(1,1,1)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['PressDescEst1'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.figure(figsize=(19,4))
    plt.subplot(1,1,1)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['PressDescEst2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.figure(figsize=(19,4))
    plt.subplot(1,2,1)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['LinEquImp'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.subplot(1,2,2)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['LinEquPar'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)

    
    plt.figure(figsize=(19,12))
    plt.subplot(3,2,1)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['TempSucCilB1B2_1'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,4000000,500000))
    plt.subplot(3,2,2)
    sns.distplot(data[(data.index>=start_date)&(data.index<=end_date)]['TempSucCilB1B2_2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,4000000,500000))
    
    plt.subplot(3,2,3)
    sns.distplot(data['TempDescCilB1'][(data.index>=start_date)&(data.index<=end_date)].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    plt.subplot(3,2,4)
    sns.distplot(data['TempDescCilB2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    plt.subplot(3,2,5)
    sns.distplot(data['TempGuiaHasteCilB1'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,4000000,500000))
    plt.subplot(3,2,6)
    sns.distplot(data['TempGuiaHasteCilB2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,4000000,500000))
    
    plt.figure(figsize=(20,12))
    plt.subplot(3,4,1)
    sns.distplot(data['TempSucCilA1A3'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3000000,250000))
    plt.subplot(3,4,2)
    sns.distplot(data['TempSucCilA2A4'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    
    
    plt.subplot(3,4,5)
    sns.distplot(data['TempDescCilA1'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    plt.subplot(3,4,6)
    sns.distplot(data['TempDescCilA2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    plt.subplot(3,4,7)
    sns.distplot(data['TempDescCilA3'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    plt.subplot(3,4,8)
    sns.distplot(data['TempDescarga Cil, A4'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    
    plt.subplot(3,4,9)
    sns.distplot(data['TempGuiaHasteCilA1'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    plt.subplot(3,4,10)
    sns.distplot(data['TempGuiaHasteCilA2'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    plt.subplot(3,4,11)
    sns.distplot(data['TempGuiaHasteCilA3'].dropna(axis = 0),kde=False,bins=25)
    plt.grid(True)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    plt.subplot(3,4,12)
    sns.distplot(data['TempGuiaHasteCilA4'].dropna(axis = 0),kde=False,bins=25)
    plt.xlim((0,100))
    #plt.yticks(np.arange(0,3500000,500000))
    plt.grid(True)


# In[4]:


def plot_dist(df,list_tags, suptitle):
    
    
    plt.figure(figsize = (19,len(list_tags)*4))
    plt.suptitle(suptitle)
    i = 1
    for tag in list_tags:
        
        plt.subplot(len(list_tags),2,i)
        df[[tag]].boxplot()
        plt.title('Boxplot:'+str(tag))
        i+=1
        plt.subplot(len(list_tags),2,i)
        sns.distplot(df[[tag]].dropna())
        plt.title('Distribution:'+str(tag))
        i+=1
    plt.show()
    
        


# In[ ]:




