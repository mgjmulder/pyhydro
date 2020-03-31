

#%% Import packages
import datetime as dt
import numpy as np
import pandas as pd

#%%
def Import_KNMIstation_daily(path_file):
    '''
    
    
    '''
    
    ## Import file.
    file = open(path_file, 'r')
    line = file.readline()

    while 'YYYYMMDD' not in line:
        line = file.readline()
    
    metadata = {}
    while 'EV24' not in line:
        metadata[line.strip().split(' = ')[0].strip()] = line.strip().split(' = ')[1].strip().split(' / ')[1]
        line = file.readline()
    metadata[line.strip().split(' = ')[0].strip()] = line.strip().split(' = ')[1].strip().split(' / ')[1]
    
    ## Walk through file, line by line, until line with header.
    while '# STN,' not in line:
        line = file.readline()
    
    ## Split header in parameter names.
    header = line.strip('\n').split(',')
    header = [header_part.strip() for header_part in header]

    ## Start importing data series
    data_raw = []   
    line = file.readline()
    while line != '':
        line = file.readline()
        if line != '':
            line_data = line.strip('\n').split(',')
            line_data = [line_part.strip() for line_part in line_data]
            line_data = [np.nan if line_part == '' else np.float(line_part) for line_part in line_data]
            data_raw.append(line_data)
        else:
            ## Close file.
            file.close
    data_raw = pd.DataFrame(data_raw, columns=header)
    data_raw.loc[:, 'YYYYMMDD'] = pd.to_datetime(data_raw.loc[:, 'YYYYMMDD'], format='%Y%m%d')
    data_raw = data_raw.set_index('YYYYMMDD')
    
    return metadata, data_raw

def conv_KNMIdata_daily(data_raw):
    data_conv = data_raw.copy()
    data_conv.loc[:, 'DDVEC'] = data_conv.loc[:, 'DDVEC']
    data_conv.loc[:, 'FHVEC'] = data_conv.loc[:, 'FHVEC'] * 0.1
    data_conv.loc[:, 'FG'] = data_conv.loc[:, 'FG'] * 0.1
    data_conv.loc[:, 'FHX'] = data_conv.loc[:, 'FHX'] * 0.1
    data_conv.loc[:, 'FHXH'] = data_conv.loc[:, 'FHXH']
    data_conv.loc[:, 'FHN'] = data_conv.loc[:, 'FHN'] * 0.1
    data_conv.loc[:, 'FHNH'] = data_conv.loc[:, 'FHNH']
    data_conv.loc[:, 'FXX'] = data_conv.loc[:, 'FXX'] * 0.1
    data_conv.loc[:, 'FXXH'] = data_conv.loc[:, 'FXXH']
    data_conv.loc[:, 'TG'] = data_conv.loc[:, 'TG'] * 0.1
    data_conv.loc[:, 'TN'] = data_conv.loc[:, 'TN'] * 0.1
    data_conv.loc[:, 'TNH'] = data_conv.loc[:, 'TNH']
    data_conv.loc[:, 'TX'] = data_conv.loc[:, 'TX'] * 0.1
    data_conv.loc[:, 'TXH'] = data_conv.loc[:, 'TXH']
    data_conv.loc[:, 'T10N'] = data_conv.loc[:, 'T10N']
    data_conv.loc[:, 'T10NH'] = data_conv.loc[:, 'T10NH'].replace(6, '0-6 UT')
    data_conv.loc[:, 'T10NH'] = data_conv.loc[:, 'T10NH'].replace(12, '6-12 UT')
    data_conv.loc[:, 'T10NH'] = data_conv.loc[:, 'T10NH'].replace(18, '12-18 UT')
    data_conv.loc[:, 'T10NH'] = data_conv.loc[:, 'T10NH'].replace(24, '18-24 UT')
    data_conv.loc[data_conv.loc[:, 'SQ'] != -1, 'SQ'] = data_conv.loc[data_conv.loc[:, 'SQ'] != -1, 'SQ'] * 0.1
    data_conv.loc[data_conv.loc[:, 'SQ'] == -1, 'SQ'] = 0.025
    data_conv.loc[:, 'SP'] = data_conv.loc[:, 'SP']
    data_conv.loc[:, 'Q'] = data_conv.loc[:, 'Q']
    data_conv.loc[:, 'DR'] = data_conv.loc[:, 'DR'] * 0.1
    data_conv.loc[data_conv.loc[:, 'RH'] != -1, 'RH'] = data_conv.loc[data_conv.loc[:, 'RH'] != -1, 'RH'] * 0.1 / 1000
    data_conv.loc[data_conv.loc[:, 'RH'] == -1, 'RH'] = 0.025 * 0.1 / 1000
    data_conv.loc[data_conv.loc[:, 'RHX'] != -1, 'RHX'] = data_conv.loc[data_conv.loc[:, 'RHX'] != -1, 'RHX'] * 0.1 / 1000
    data_conv.loc[data_conv.loc[:, 'RHX'] == -1, 'RHX'] = 0.025 * 0.1 / 1000
    data_conv.loc[:, 'RHXH'] = data_conv.loc[:, 'RHXH']
    data_conv.loc[:, 'PG'] = data_conv.loc[:, 'PG'] * 0.1
    data_conv.loc[:, 'PX'] = data_conv.loc[:, 'PX'] * 0.1
    data_conv.loc[:, 'PXH'] = data_conv.loc[:, 'PXH']
    data_conv.loc[:, 'PN'] = data_conv.loc[:, 'PN'] * 0.1
    data_conv.loc[:, 'PNH'] = data_conv.loc[:, 'PNH']
    data_conv.loc[:, 'VVN'] = data_conv.loc[:, 'VVN']
    data_conv.loc[:, 'VVNH'] = data_conv.loc[:, 'VVNH']
    data_conv.loc[:, 'VVX'] = data_conv.loc[:, 'VVX']
    data_conv.loc[:, 'VVXH'] = data_conv.loc[:, 'VVXH']
    data_conv.loc[:, 'NG'] = data_conv.loc[:, 'NG']
    data_conv.loc[:, 'UG'] = data_conv.loc[:, 'UG']
    data_conv.loc[:, 'UX'] = data_conv.loc[:, 'UX']
    data_conv.loc[:, 'UXH'] = data_conv.loc[:, 'UXH']
    data_conv.loc[:, 'UN'] = data_conv.loc[:, 'UN']
    data_conv.loc[:, 'UNH'] = data_conv.loc[:, 'UNH']
    data_conv.loc[:, 'EV24'] = data_conv.loc[:, 'EV24'] * 0.1 / 1000
    return data_conv

def get_relevantKNMIdata_daily(data_raw, conversion=True):
    '''
    Function to retrieve relevant data for Vitens monitoring wells from raw KNMI station data. 
        - Precipitation
        - Evaporation
        - Air pressure
    If conversion=True, data is automatically converted to right units.
    '''
    
    data_vitens = data_raw[['RH', 'EV24', 'PG']]
    data_vitens = data_vitens.rename(columns={'RH':'precipitation', 'EV24':'evaporation', 'PG':'pressure'})
    
    if conversion:
        ## raw precipitation data is in 0.1mm. with -1 for precipitation < 0.5mm. Replace -1 by 0.
        data_vitens.loc[data_vitens.loc[:, 'precipitation'] == -1, 'precipitation'] = 0
        data_vitens.loc[:, 'precipitation'] = data_vitens.loc[:, 'precipitation'] * 0.1 / 1000
        
        ## raw evaporation and pressure are in 0.1mm and 0.1hPa respectively. 
        data_vitens.loc[:, 'evaporation'] = data_vitens.loc[:, 'evaporation'] * 0.1 / 1000
        data_vitens.loc[:, 'pressure'] = data_vitens.loc[:, 'pressure'] * 0.1
    
    return data_vitens
        

def Import_KNMIstation_hourly(path_file):
    '''
    
    
    '''
    
    ## Import file.
    file = open(path_file, 'r')
    line = file.readline()
    
    ## Walk through file until station metadata. 
    while '# STN' not in line:
        line = file.readline()
    line = file.readline().split()
    metastation = {}
    metastation['Nummer'] = line[1].strip(':')
    metastation['X'] = line[2]
    metastation['Y'] = line[3]
    metastation['Z'] = line[4]
    metastation['Naam'] = line[5]
    
    ## Skip through file until measurement metadata
    line = file.readline()
    line = file.readline()
    metadata = {}
    while '# Y ' not in line:
        metadata[line.strip().split(' = ')[0].strip().strip('# ')] = line.strip().split(' = ')[1].split(';')[0].strip()
        line = file.readline()
    metadata[line.strip().split(' = ')[0].strip().strip('# ')] = line.strip().split(' = ')[1].split(';')[0].strip()
    
    ## Skip through file until data header. 
    while '# STN,' not in line:
         line = file.readline()
    
    ## Split header in parameter names.
    header = line.strip('\n').strip('# ').split(',')
    header = [header_part.strip() for header_part in header]
    line = file.readline()
    
    ## Skip through file until end of all data lines. 
    data_raw = []   
    while line != '':
        line = file.readline()
        if line != '':
            line_data = line.strip('\n').split(',')
            line_data = [line_part.strip() for line_part in line_data]
            line_data = [np.nan if line_part == '' else np.float(line_part) for line_part in line_data]
            data_raw.append(line_data)
        else:
            file.close
    
    ## Post-processing of output data. 
    data_raw = pd.DataFrame(data_raw, columns=header)
    data_raw.loc[:, 'YYYYMMDD'] = data_raw.loc[:, 'YYYYMMDD'].astype(int).astype(str)
    data_raw.loc[:, 'date'] = data_raw.loc[:, 'YYYYMMDD'] + np.char.zfill((data_raw.loc[:, 'HH'] - 1).astype(int).astype(str).values.astype(str), 2)
    data_raw.loc[:, 'HH'] = np.char.zfill((data_raw.loc[:, 'HH']).astype(int).astype(str).values.astype(str), 2)
    data_raw.loc[:, 'date'] = pd.to_datetime(data_raw.loc[:, 'date'].astype(str), format='%Y%m%d%H') + dt.timedelta(hours=1)
    data_raw = data_raw.set_index('date')
    
    return metastation, metadata, data_raw

def conv_KNMIdata_hourly(data_raw):
    data_conv = data_raw.copy()
    data_conv.loc[:, 'DD'] = data_conv.loc[:, 'DD']
    data_conv.loc[:, 'FH'] = data_conv.loc[:, 'FH'] * 0.1
    data_conv.loc[:, 'FF'] = data_conv.loc[:, 'FF'] * 0.1
    data_conv.loc[:, 'FX'] = data_conv.loc[:, 'FX'] * 0.1
    data_conv.loc[:, 'T'] = data_conv.loc[:, 'T'] * 0.1
    data_conv.loc[:, 'T10N'] = data_conv.loc[:, 'T10N'] * 0.1
    data_conv.loc[:, 'TD'] = data_conv.loc[:, 'TD'] * 0.1
    data_conv.loc[data_conv.loc[:, 'SQ'] != -1, 'SQ'] = data_conv.loc[data_conv.loc[:, 'SQ'] != -1, 'SQ'] * 0.1
    data_conv.loc[data_conv.loc[:, 'SQ'] == -1, 'SQ'] = 0.025
    data_conv.loc[:, 'Q'] = data_conv.loc[:, 'Q']
    data_conv.loc[:, 'DR'] = data_conv.loc[:, 'DR'] * 0.1
    data_conv.loc[data_conv.loc[:, 'RH'] != -1, 'RH'] = data_conv.loc[data_conv.loc[:, 'RH'] != -1, 'RH'] * 0.1 / 1000
    data_conv.loc[data_conv.loc[:, 'RH'] == -1, 'RH'] = 0.025 * 0.1 / 1000
    data_conv.loc[:, 'P'] = data_conv.loc[:, 'P'] * 0.1
    data_conv.loc[:, 'VV'] = data_conv.loc[:, 'VV']
    data_conv.loc[:, 'N'] = data_conv.loc[:, 'N']
    data_conv.loc[:, 'U'] = data_conv.loc[:, 'U']
    data_conv.loc[:, 'WW'] = data_conv.loc[:, 'WW']
    data_conv.loc[:, 'IX'] = data_conv.loc[:, 'IX']
    data_conv.loc[:, 'M'] = data_conv.loc[:, 'M']
    data_conv.loc[:, 'R'] = data_conv.loc[:, 'R']
    data_conv.loc[:, 'S'] = data_conv.loc[:, 'S']
    data_conv.loc[:, 'O'] = data_conv.loc[:, 'O']
    data_conv.loc[:, 'Y'] = data_conv.loc[:, 'Y']
    return data_conv

def get_relevantKNMIdata_hourly(data_raw, conversion=True):
    '''
    Function to retrieve relevant data for Vitens monitoring wells from raw KNMI station data. 
        - Precipitation
        - Air pressure
    If conversion=True, data is automatically converted to right units.
    '''
    
    data_vitens = data_raw[['RH', 'P']]
    data_vitens = data_vitens.rename(columns={'RH':'precipitation', 'P':'pressure'})
    
    if conversion:
        ## raw precipitation data is in 0.1mm. with -1 for precipitation < 0.5mm. Replace -1 by 0.
        data_vitens.loc[data_vitens.loc[:, 'precipitation'] == -1, 'precipitation'] = 0
        data_vitens.loc[:, 'precipitation'] = data_vitens.loc[:, 'precipitation'] * 0.1 / 1000
        
        ## raw pressure is in 0.1hPa. 
        data_vitens.loc[:, 'pressure'] = data_vitens.loc[:, 'pressure'] * 0.1
    
    return data_vitens
