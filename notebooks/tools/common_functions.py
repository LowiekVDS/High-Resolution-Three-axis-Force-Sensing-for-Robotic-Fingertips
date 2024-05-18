import pandas as pd
import os
import numpy as np

def validate_data(data, model, ARRAY_SIZE=4):
    # Validate against the subsampled version
    # Load in data file and prepare for val
    
    # Predict F_z{i} based on measurements
    X = data[[f'Z{i}' for i in range(ARRAY_SIZE)]].to_numpy()
    F_zi = model.predict(X)
    
    return F_zi

def correct_data_for_faulty_conversion(faulty_data, array_size, old_factors, new_factors):
    
    # Correction of data
    for i in range(array_size):
        for j, letter in enumerate(["X", "Y", "Z"]):
            
            # Correction (from what I did in the sensor measurement .py file)
            faulty_data.loc[:, f'{letter}{i}'] /= old_factors[j]
            faulty_data.loc[:, f'{letter}{i}'] += 32768
            
            # Now in the sensor readout code I also set a constant offset. So a measurement of 32768 was reported as 0
            # faulty_data.loc[:, f'{letter}{i}'] -= 32768
            
            # 2's complement
            faulty_data[f'{letter}{i}'][faulty_data[f'{letter}{i}'] > 2**16] -= 2**16
            
            # Correct factor (to uT)
            faulty_data[f'{letter}{i}'] *= new_factors[j]

    return faulty_data

def split_data_into_regions(data, center_points, min_distance=99999999):
    
    ARRAY_SIZE_SUB = len(center_points)

    # Fetch distances from the samples in data to each and every data_point
    distances = np.zeros((len(data), ARRAY_SIZE_SUB))
    for i, point in enumerate(center_points):
        distances[:,i] = np.sqrt((data['X'] - point[0])**2 + (data['Y'] - point[1])**2)
    
    # Find the closest data_point for each sample
    closest = np.argmin(distances, axis=1)
    
    # Separate based on min distance
    # Note: keeps the time order intact
    models = [data[closest == i][distances[closest == i] < min_distance] for i in range(ARRAY_SIZE_SUB)]
    for model in models:
        model.reset_index(inplace=True)
        model.dropna(inplace=True)
        
    return models

def split_data_into_regions_full(data, center_points, columns, min_distance=99999999):
    
    ARRAY_SIZE_SUB = len(center_points)

    # Fetch distances from the samples in data to each and every data_point
    distances = np.zeros((len(data), ARRAY_SIZE_SUB))
    for i, point in enumerate(center_points):
        distances[:,i] = np.sqrt((data['X'] - point[0])**2 + (data['Y'] - point[1])**2)
    
    # Find the closest data_point for each sample
    closest = np.argmin(distances, axis=1)
    
    # Separate based on min distance
    # Note: keeps the time order intact
    models = [data.copy() for i in range(ARRAY_SIZE_SUB)]
    
    for i in range(ARRAY_SIZE_SUB):
        
        for col in columns:
            models[i].loc[closest != i, col] = 0
            models[i].loc[distances[:, i] > min_distance, col] = 0
        
    return models

def extract_features(data):
    # Calculate magnitude and angle

    data['F_m'] = np.sqrt(data['F_x']**2 + data['F_y']**2 + data['F_z']**2)
    data['F_xy'] = np.sqrt(data['F_x']**2 + data['F_y']**2)
    data['F_t'] = np.arctan2(data['F_y'], data['F_x']) 
    for i in range(4):
        data[f'M{i}'] = np.sqrt(data['X0']**2 + data['Y0']**2 + data['Z0']**2)
        data[f'XY{i}'] = np.sqrt(data['X0']**2 + data['Y0']**2)
        data[f'T{i}'] = np.arctan2(data['Y0'], data['X0'])
        
    return data
    

def extract_center_points_from_data(old_data, ARRAY_SIZE_SUB, normalize=False):
    
    # Boundary search of where the x,y is valid
    z_filter = old_data['Z'].copy().to_numpy()
    z_filter[old_data['Z'] - np.min(z_filter) > 0.005] = 0
    z_filter[z_filter.nonzero()] = 1
    boundaries = np.diff(z_filter).nonzero()[0].reshape(-1, 2)
    
    data = old_data.copy()
    
    data_points = np.zeros((ARRAY_SIZE_SUB, 2))
    assert boundaries.shape[0] == ARRAY_SIZE_SUB, f"Expected {ARRAY_SIZE_SUB} boundaries, got {boundaries.shape[0]}"
    
    for i in range(ARRAY_SIZE_SUB):
        data_points[i][0] = data['X'].to_numpy()[boundaries[i][0]:boundaries[i][1]].mean()
        data_points[i][1] = data['Y'].to_numpy()[boundaries[i][0]:boundaries[i][1]].mean()
    
    # When needed, normalize the data (incl. X and Y)
    if normalize:
        # Normalize data points between 0 and 1
        shift = np.min(data_points, axis=0)
        scale = np.max(data_points, axis=0) - np.min(data_points, axis=0)
        data_points = (data_points - shift) / scale

        # Apply the filter to the XY data
        data['X'] = (data['X'] - shift[0]) / scale[0]
        data['Y'] = (data['Y'] - shift[1]) / scale[1]
    
    return data_points, data

def extract_center_points_from_data_alt(old_data, ARRAY_SIZE_SUB, normalize=False):
    
    # Find 
    
    # Boundary search of where the x,y is valid
    z_filter = old_data['Z'].copy().to_numpy()
    z_filter[old_data['Z'] - np.min(z_filter) > 0.005] = 0
    z_filter[z_filter.nonzero()] = 1
    boundaries = np.diff(z_filter).nonzero()[0].reshape(-1, 2)
    
    data = old_data.copy()
    
    data_points = np.zeros((ARRAY_SIZE_SUB, 2))
    assert boundaries.shape[0] == ARRAY_SIZE_SUB, f"Expected {ARRAY_SIZE_SUB} boundaries, got {boundaries.shape[0]}"
    
    for i in range(ARRAY_SIZE_SUB):
        data_points[i][0] = data['X'].to_numpy()[boundaries[i][0]:boundaries[i][1]].mean()
        data_points[i][1] = data['Y'].to_numpy()[boundaries[i][0]:boundaries[i][1]].mean()
    
    # When needed, normalize the data (incl. X and Y)
    if normalize:
        # Normalize data points between 0 and 1
        shift = np.min(data_points, axis=0)
        scale = np.max(data_points, axis=0) - np.min(data_points, axis=0)
        data_points = (data_points - shift) / scale

        # Apply the filter to the XY data
        data['X'] = (data['X'] - shift[0]) / scale[0]
        data['Y'] = (data['Y'] - shift[1]) / scale[1]
    
    return data_points, data

def prepare_data_for_fitting(name, ARRAY_SIZE=4, SENSOR_LAG = 25, faulty=True):
    
    print(f"Preparing data for fitting: {name}")
    columns = [f'X{i}' for i in range(ARRAY_SIZE)] + [f'Y{i}' for i in range(ARRAY_SIZE)] + [f'Z{i}' for i in range(ARRAY_SIZE)]
    
    TFdata = read_csv_file(f"../data/raw/TF/{name}.csv") 
    sensordata = read_csv_file(f'../data/raw/sensor/{name}.csv')

    # First corrcet faulty data
    if faulty:
        sensordata = correct_data_for_faulty_conversion(sensordata, ARRAY_SIZE, [0.300, 0.300, 0.484], [0.150, 0.150, 0.242])
    
    # First unwrap the sensordata
    # sensordata = unwrap_data(sensordata, columns)

    dt = TFdata.iloc[-1]['t_wall'] - TFdata.iloc[0]['t_wall']

    # TFdata['F_x'] = TFdata['F_x'].rolling(window=10).mean()
    # TFdata['F_y'] = TFdata['F_y'].rolling(window=10).mean()
    # TFdata['F_z'] = TFdata['F_z'].rolling(window=10).mean()

    # Time sync
    data = time_sync_data(sensordata, TFdata, SENSOR_LAG / 1000)
    
    # Remove rows containing NaN values
    data = data.dropna()
    
    # Offset and scale
    data = offset_data(data, columns, 100)
    
    # Remove other columns
    data = data.drop(columns=['t_robot', 'R_x', 'R_y', 'R_z'])

    return data

def unwrap_data(data, columns, threshold=1000):
    
    for col in columns:
        
        np_data = data[col].to_numpy()

        diff = np.diff(np_data)
                
        wrap_points = np.where(np.abs(diff) > threshold)[0]
                
        for point in wrap_points:
            np_data[point+1:] -= diff[point]

        data[col] = np_data

    return data

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

def offset_data(data, columns, window=100, startup=100):

    for col in columns:
        data[col] -= np.mean(data[col][startup:startup+window])
        data[col] /= 1000
        
    return data

def normalize_center_data(data, columns):
    """
    Normalizes the data in the specified columns.
    
    Parameters:
        data (pandas.DataFrame): The data to be normalized.
        columns (list): The columns to be normalized.
        
    Returns:
        pandas.DataFrame: The normalized data.
    """
    
    for col in columns:
        data[col] = data[col] / (data[col].max() - data[col].min())
        data[col] = (data[col] - data[col].mean())
        
    return data