import pandas as pd
import numpy as np

def mount_dataframe_from_files(files_dir,columns_to_retrieve):
    final_df = []
    for df_name in files_dir:
        for col in columns_to_retrieve:
            try:
                df = pd.read_csv(df_name, compression = 'gzip',usecols=[col,'Date'])
                df['Date'] = pd.to_datetime(df['Date'])
                df.set_index('Date', inplace = True)
                df.head()
                final_df.append(df)
                print(col+' found in '+df_name)
            except Exception as e: 
                print(e)
                print('skiping '+col+' for '+df_name)
    
    if(len(final_df)>0):
        print('Mounting final DF')
        return pd.concat(final_df,axis=1)
    else:
        print('No data retrieve... returning empty DF')
    return 
