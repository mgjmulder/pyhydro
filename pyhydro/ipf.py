import numpy as np
import pandas as pd


#%% 
def import_ipf(path_ipf, report=False):
    '''
    imports .ipf iMOD flowpath data and returns dataframe
    
    
    Parameters
    ----------
    path_ipf : str
        Path to .ipf file
    report : bool
        boolean to print progress report. Either True or False. The default is False
        
    Returns
    -------
    ipf_data : pd.DataFrame
        Dataframe containing the imported .ipf data
    ipf_xs : array
        array containing all x-coordinates of .ipf data
    ipf_ys : array
        array containing all y-coordinates of .ipf data
    '''
    
    
    ## Open file
    if report:
        print('Import .ipf-data of file', path_ipf)
    file = open(path_ipf, 'r')
    
    ## Read number of data lines and header lines.
    Ndata = int(file.readline().strip())
    Nheader = int(file.readline().strip())
    if report:
        print(str(Ndata), 'lines of flowpath data found')
        
    ## Import header lines.
    ipf_header = []
    for i in range(Nheader):
        ipf_header.append(file.readline().strip())
    file.readline().strip()
    
    ## Import data lines. 
    ipf_data = []
    for i in range(Ndata):
        ipf_data.append(file.readline().strip().split())
    file.close()
    
    ## Convert imported data to dataframe.
    if report:
        print('Converting .ipf-data to DataFrame')
    ipf_data = pd.DataFrame(data=ipf_data, columns=ipf_header, dtype=np.float)    
    
    ## Extracting x- and y-coordinates of imodpath data.
    ipf_xs = ipf_data.loc[:, 'SP_XCRD.'].drop_duplicates().values
    ipf_ys = ipf_data.loc[:, 'SP_YCRD.'].drop_duplicates().values
    
    ## Translating x- and y-coordinates to cols and row values of imodpath data.
    for i, index in enumerate(ipf_data.index):
        i_col = np.argmin(abs(ipf_xs - ipf_data.loc[index, 'SP_XCRD.']))
        i_row = np.argmin(abs(ipf_ys - ipf_data.loc[index, 'SP_YCRD.']))
    
        ipf_data.loc[index, 'imodpath_col'] = i_col
        ipf_data.loc[index, 'imodpath_row'] = i_row
    
    return ipf_data, ipf_xs, ipf_ys


def get_well_cells(wells, model_xs, model_ys, model_dx=25, report=False):
    '''
    takes a dataframe with wells and converts coordinates to cell-numbers of model. 
    so, basically converts x- and y- coordinates to column and row numbers.
    
    
    Parameters
    ----------
    wells : pd.DataFrame
        Dataframe containing the wells to extract flowpath data from.
        Dataframe contains at least a column "X" with x-coordinates and a column "Y" with y-coordinates.
    model_xs : array
        array containing all x-coordinates of iMOD model
    model_ys : array
        array containing all y-coordinates of iMOD model
    model_dx : float
        distance between x- and y- coordinates of iMOD model
    report : bool
        boolean to print progress report. Either True or False. The default is False
    
    Returns
    -------
    wells : pd.DataFrame
        Original dataframe with added columns "ICOL" and "IROW", containing the row and column numbers.
    well_bundle : raster
        raster with marked locations of the wells. 
    '''
    
    model_dy=-model_dx
    
    ## setting up output raster with well locations
    well_bundle = np.zeros((len(model_ys), len(model_xs)))
    well_bundle =  well_bundle * np.nan
    
    if report:
        print('convert coordinates for',str(len(wells)),'wells')
    
    for well_i, well_index in enumerate(wells.index):
        well_x = wells.loc[well_index, 'X']
        well_y = wells.loc[well_index, 'Y']
        ## get x-coordinate of wells
        for i, x in enumerate(model_xs):
            if (well_x > (x-model_dx/2)) & (well_x <= (x+model_dx/2)):
                well_ICOL = i
                wells.loc[well_index, 'ICOL'] = well_ICOL + 1
                break
            ## get y-coordinate of wells. Remember that dy=-dx
        for j, y in enumerate(model_ys):
            if (well_y >= (y+model_dy/2)) & (well_y < (y-model_dy/2)):
                well_IROW = j   
                wells.loc[well_index, 'IROW'] = well_IROW + 1
                break
        well_bundle[j,i] = 1
    if report:
        print('x- and y- coordinates of wells converted to row- and column-numbers of model')
    return wells, well_bundle


def flowpath_origin(wells, ipf_data, ipf_xs, ipf_ys, report=False):
    '''
    extracts all .ipf flowpaths that end up in wells. 
    requires a dataframe with wells containing row and column numbers. 
    returns a raster with origins of flowpaths from corresponding wells.
    returns a raster with traveltimes of flowpaths to all wells.
    returns data of all .ipf flowpaths that end up in wells.
    
    
    Parameters
    ----------
    wells : pd.DataFrame
        dataframe containing all wells, rows- and column-numbers included. 
    data_ipf : pd.DataFrame
        dataframe containing all imported flowpath data from .ipf
    xs : array
        array containing all x-coordinates of .ipf flowpath data
    ys : array
        array containing all y-coordinates of .ipf flowpath data
    report : bool
        boolean to print progress report. Either True or False. The default is False
    
    Returns
    -------
    origin : raster
        raster containing origins of flowpaths that end up in corresponding wells
        the origin numbers correspond to the well numbers in the returned dataframe "data_ipf_well"
    traveltimes : raster
        raster containing traveltimes of flowpaths that end up in corresponding wells
    data_ipf_well : pd.DataFrame
        dataframe with all .ipf flowpaths that end up in the provided wells.
    '''
    
    ## setting up dataframe for flowpaths that end up in wells
    ipf_data_well = pd.DataFrame()
    
    if report:
        print('setting up output rasters for origins and traveltimes of provided flowpaths')
    ipf_traveltimes = np.zeros((len(ipf_ys), len(ipf_xs)))
    ipf_traveltimes = ipf_traveltimes * np.nan
    ipf_origin = np.zeros((len(ipf_ys), len(ipf_xs)))
    ipf_origin = ipf_origin * np.nan
    
    if report:
        print('importing .ipf flowpath data for',str(len(wells)),'wells')
    for well_i, well_index in enumerate(wells.index):
        well_IROW = wells.loc[well_index, 'IROW']
        well_ICOL = wells.loc[well_index, 'ICOL']
        well_data = ipf_data.loc[(ipf_data.loc[:, 'EP_IROW'] == well_IROW) & (ipf_data.loc[:, 'EP_ICOL'] == well_ICOL)].copy()
        
        if len(well_data) > 0:
            well_data.loc[:, 'Well_nr'] = well_i
            well_data.loc[:, 'Well_code'] = wells.loc[well_index, 'Name']
            ipf_data_well = ipf_data_well.append(well_data)
            for flowpath_i, flowpath_index in enumerate(well_data.index):
                flowpath_SP_IROW = int(well_data.loc[flowpath_index, 'imodpath_row'])
                flowpath_SP_ICOL = int(well_data.loc[flowpath_index, 'imodpath_col'])
                
                ipf_traveltimes[flowpath_SP_IROW, flowpath_SP_ICOL] = well_data.loc[flowpath_index, 'TIME(YEARS)']
                ipf_origin[flowpath_SP_IROW, flowpath_SP_ICOL] = well_i
    
    return ipf_origin, ipf_traveltimes, ipf_data_well


