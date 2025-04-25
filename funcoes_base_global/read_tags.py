import re
import numpy as np
import pandas as pd
from os.path import join
from functools import partial


def read_tags(tags, tag_path, compressed = True, coerce_tag_to_number = True, sort_index = False, drop_na = False, converters = None):
    dataframes = []
    for tag in tags:
        df = read_tag(tag = tag, tag_path = tag_path, compressed = compressed, 
                      coerce_tag_to_number = coerce_tag_to_number, sort_index = False, 
                      drop_na = False, converters = converters)
        dataframes.append(df)
        
    print('Concatenando...')    
    df = pd.concat(dataframes, axis = 1)
    del dataframes

    if drop_na:
        df.dropna(inplace = True)

    if sort_index:
       df.sort_index(inplace = True)
    print('Feito!')
    return df



def read_tag(tag, tag_path, compressed = True, coerce_tag_to_number = True, sort_index = False, drop_na = False, converters = None):
    tag_path = join(tag_path, tag + '_steped') + ('.csv.gz' if compressed else '.csv')
    compression = 'gzip' if compressed else None
    converters = converters if converters else get_tag_converters(tag, coerce_tag_to_number)
    
    print ('Processando TAG:',tag)
    df = pd.read_csv(tag_path, compression = compression, parse_dates = ['Date'], index_col = 'Date',
                     converters = converters)
    
    df[tag] = pd.to_numeric(df[tag], errors = 'coerce')

    if drop_na:
        df.dropna(inplace = True)

    # replaces duplicate values with the first ocourrence
    df = df.groupby(df.index).first()

    if sort_index:
       df.sort_index(inplace = True)

    return df


def get_tag_converters(tag, coerce_tag_to_number):
    if is_raw_tag(tag) and coerce_tag_to_number:
        tag_type = tag.split('.')[1]
        tag_converter = partial(tag_value_converter, tag_type = tag_type)
        converters = converters = {f'{tag}': tag_converter, f'{tag}_quality': tag_quality_converter}
    else: 
        converters = None
    
    return converters

def is_raw_tag(tag_name):
    return re.match(r'^\d{3}[a-zA-Z]{2}\d{4}[a-zA-z]?\.(PV|SP|OP|MODE|IQ|RATIO|OUT)', tag_name)


def tag_value_converter(raw_value, tag_type):
    if tag_type == 'MODE':
        return 1 if raw_value == 'AUTO' else 0
    else:
        try:
            return float(raw_value)
        except:
            return np.nan


def tag_quality_converter(raw_value):
    return raw_value