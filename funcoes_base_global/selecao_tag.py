import pandas as pd
import numpy  as np

def select_sensor(bd, tag_1, tag_2, cond, new_variable = None, period = 600):
    df = bd.copy()
    df[new_variable] = np.zeros(df.shape[0])
    df[new_variable] = np.nan
    tempo = period
    df['rule_tag1'] = df[tag_1].rolling(window = tempo, min_periods = 1).std()
    df['rule_tag2'] = df[tag_2].rolling(window = tempo, min_periods = 1).std()
    df.loc[(df['rule_tag1'] <= cond) & pd.isna(df[new_variable]), new_variable] = df.loc[(df['rule_tag1'] <= cond) & pd.isna(df[new_variable]), tag_1].values
    df.loc[(df['rule_tag2'] <= cond) & pd.isna(df[new_variable]), new_variable] = df.loc[(df['rule_tag2'] <= cond) & pd.isna(df[new_variable]), tag_2].values
    df.drop(columns = ['rule_tag1', 'rule_tag2'], inplace = True)
    return df