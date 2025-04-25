import pandas as pd
import os
import numpy as np
def load_dataframe(name,cols = [], ref_dir = ''):
    path_Input = ref_dir

    if(len(cols)>0):
        df = pd.read_csv(os.path.join(path_Input,name), sep=',', usecols = cols+['Instant']) 
    else:
        df = pd.read_csv(os.path.join(path_Input,name), sep=',') 
    df['Instant'] = pd.to_datetime(df['Instant'],errors='coerce');
    df = df.set_index('Instant')
    
    
    
    #df = df.resample('60s').mean()
    
    feature = df.columns[0]
    
        
    return df



def create_df_freq(df,start_date,end_date,window):
    
    start_day =pd.Timestamp(start_date)
    end_day = pd.Timestamp(end_date)
    df_freq = []

    while start_day<=end_day:
    
    
        n = df[(df.index>=start_day)&(df.index<=start_day+pd.Timedelta(str(window)+'minutes'))].shape[0]
        
        if (df[(df.index>=start_day)&(df.index<=start_day+pd.Timedelta(str(window)+'minutes'))].isna().sum()>0).sum()>0:
            start_day = start_day+pd.Timedelta(str(window))
            continue
        
        
        df_freqn = pd.DataFrame(np.abs(np.fft.fft(df[(df.index>=start_day)&(df.index<=start_day+pd.Timedelta(str(window)+'minutes'))],axis = 1)[:n//2]),columns = df[(df.index>=start_day)&(df.index<=start_day+pd.Timedelta(str(window)+'minutes'))].columns)
       
        
        df_freqn['Date'] = pd.to_datetime(np.array([str(start_day)]*(int(n/2))))
        df_freqn['highest'] = np.arange(1,int(n/2)+1)
        
        for column in df_freqn.columns:
            df_freqn['freq'] = np.fft.fftfreq(int(n/2))
            if '_freq' or 'Date' not in column:
                df_freqn[str(column)+'_freq'] = df_freqn[[column,'freq']].sort_values(by=column, ascending = False)['freq'].values  
        
        
        df_freq += [df_freqn]
        del df_freqn
    
        start_day = start_day+pd.Timedelta(str(window)+'minutes')
    

    df_freq = pd.concat(df_freq)
    df_freq.set_index('Date', inplace = True)
    return df_freq
