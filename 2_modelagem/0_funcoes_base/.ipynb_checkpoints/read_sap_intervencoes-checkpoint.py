import pandas as pd
import os
import json

def path_out(name):
    path = os.path.join('..','..','1_preprocessamento','out',name)
    return(path)


def read(name):
    if name.split('.')[1] == 'xlsx':
        df = pd.read_excel(path_out(name))
    else:
        df = pd.read_csv(path_out(name))
    df['Data'] =pd.to_datetime(df['Data'])
    df.index = df['Data']
    df = df.drop('Data' , axis = 1)
    df = df.drop('Data.1' , axis = 1)
    return df


def dicionario():
    name = 'dados_sap_out.xlsx'
    df = read(name)
    
    name = 'tabela_de_intervencoes_out.csv'
    df_2 = read(name)
    
    
    df['Tp'].loc[df['Tp'].str.contains('Z8')] = 'Prev.'
    df['Tp'].loc[df['Tp'].str.contains('Z')] = 'Corr.'
    
    df_2['intervencoes'] = 'Inter.'
    
    dicionario_sap = df['Tp'].to_dict()
    dicionario_intervencoes = df_2['intervencoes'].to_dict()
    
    dicionario_important_dates = dicionario_intervencoes
    dicionario_important_dates.update(dicionario_sap)
    
    return (dicionario_sap, dicionario_intervencoes, dicionario_important_dates)
