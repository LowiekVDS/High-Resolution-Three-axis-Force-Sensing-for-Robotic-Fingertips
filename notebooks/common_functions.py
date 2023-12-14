import pandas as pd
import os
import numpy as np

def read_csv_file(path):
    """
    Reads a CSV file from the specified path and returns the data as a pandas DataFrame.
    
    Parameters:
        path (str): The path to the CSV file.
        
    Returns:
        pandas.DataFrame: The data read from the CSV file.
    """
    
    data = pd.read_csv(os.path.join(os.getcwd(), path))
    
    nr_of_columns = len(data.columns)
    
    # Remove units
    for col in data.columns:
        data[col .split(' ')[0]] = data[col]
    
    # Remove old columns
    data = data.iloc[:, nr_of_columns:]    
    
    return data
    
def read_csv_files(paths):
    """
    Reads all CSV files from the specified path and returns the data as a pandas DataFrame.
    
    Parameters:
        paths (list): list of paths
        
    Returns:
        pandas.DataFrame: The data read from the CSV files.
    """
    
    data = pd.DataFrame()
    
    for p in paths:
        data = pd.concat([data, read_csv_file(p)], ignore_index=True)
    
    return data    

def flatten_extend(matrix):
    flat_list = []
    for row in matrix:
        flat_list.extend(row)
    return flat_list

def time_sync_data(df1, df2, df1_lag):

    df1['t_wall'] -= df1_lag
    
    df1_is_first = df1['t_wall'][0] < df2['t_wall'][0]
    sensor_is_last = df1['t_wall'][len(df1)-1] > df2['t_wall'][len(df2)-1]

    if df1_is_first:
        start = df2['t_wall'][0]
    else:
        start = df1['t_wall'][0]
    
    if sensor_is_last:
        end = df1['t_wall'][len(df1)-1]
    else:
        end = df2['t_wall'][len(df2)-1]
    
    # Clip data to start at the same time and also to end at the same time
    df2 = df2[df2['t_wall'] >= start]
    df1 = df1[df1['t_wall'] >= start]
    df2 = df2[df2['t_wall'] <= end]
    df1 = df1[df1['t_wall'] <= end]

    combined = pd.concat([df1, df2], ignore_index=True, sort=False).sort_values(by=['t_wall'])

    combined.set_index('t_wall')
    combined = combined.apply(lambda x: x.interpolate(method='linear')).reset_index()
    
    return combined

def offset_data(data, columns, window=100):
    
    for col in columns:
        data[col] -= np.mean(data[col][:window])
        data[col] /= 1000
        
    return data

def normalize_data(data, columns, scale=True):
    """
    Normalizes the data in the specified columns.
    
    Parameters:
        data (pandas.DataFrame): The data to be normalized.
        columns (list): The columns to be normalized.
        
    Returns:
        pandas.DataFrame: The normalized data.
    """
    
    for col in columns:
        data[col] = (data[col] - data[col].mean())
        
        if scale:
            data[col] = data[col] / data[col].std()
        
    return data