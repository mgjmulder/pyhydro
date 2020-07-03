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
    data : pd.DataFrame
        Dataframe containing the imported .ipf data
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
    header = []
    for i in range(Nheader):
        header.append(file.readline().strip())
    file.readline().strip()
    
    ## Import data lines. 
    data = []
    for i in range(Ndata):
        data.append(file.readline().strip().split())
    file.close()
    
    ## Convert imported data to dataframe.
    if report:
        print('Converting .ipf-data to DataFrame')
    data = pd.DataFrame(data=data, columns=header, dtype=np.float)    
    return data


def ipf_to_coords(data_ipf, dx=25.0, report=False):
    '''
    takes .ipf data and extracts x- and y-coordinates of raster
    so basically extracts the extent of the .ipf data and converts to x- and y-coordinates.
    
    
    Parameters
    ----------
    data_ipf : pd.DataFrame
        Dataframe containing the imported .ipf data
    dx : float
        distance between x- and y- coordinates of .ipf data
    report : bool
        boolean to print progress report. Either True or False. The default is False
        
    Returns
    -------
    xs : array
        array containing all x-coordinates of .ipf data
    ys : array
        array containing all y-coordinates of .ipf data
    '''
    
    ## get extent of imported .ipf data
    dy=dx
    xmin = data_ipf.loc[:, 'SP_XCRD.'].min()
    ymax = data_ipf.loc[:, 'SP_YCRD.'].max()
    xmax = data_ipf.loc[:, 'SP_XCRD.'].max()
    ymin = data_ipf.loc[:, 'SP_YCRD.'].min()
    extent = [xmin-dx/2, ymax+dy/2, xmax+dx/2, ymin-dy/2]
    if report:
        print('Extent of imported .ipf data: [x_ul, y_ul, x_lr, y_lr] = ',extent)

    ## get distance along x- and y-axis
    xdist = (xmax + dx/2) - (xmin - dx/2)
    ydist = (ymax + dy/2) - (ymin - dy/2)
    
    ## count number of rastercells along x- and y-axis
    xcells = int(xdist / dx)
    ycells = int(ydist / dy)
    
    ## extract x- and y- coordinates
    xs = np.linspace(xmin, xmax, xcells)
    ys = np.linspace(ymax, ymin, ycells)
    
    return xs, ys

def get_well_cells(wells, xs, ys, dx=25, report=False):
    '''
    takes a dataframe with wells and converts coordinates to cell-numbers. 
    so, basically converts x- and y- coordinates to column and row numbers.
    
    
    Parameters
    ----------
    wells : pd.DataFrame
        Dataframe containing the wells to extract flowpath data from.
        Dataframe contains at least a column "X" with x-coordinates and a column "Y" with y-coordinates.
    xs : array
        array containing all x-coordinates of .ipf data
    ys : array
        array containing all y-coordinates of .ipf data
    dx : float
        distance between x- and y- coordinates of .ipf data
    report : bool
        boolean to print progress report. Either True or False. The default is False
    
    Returns
    -------
    wells : pd.DataFrame
        Original dataframe with added columns "ICOL" and "IROW", containing the row and column numbers.
    well_bundle : raster
        raster with marked locations of the wells. 
    '''
    
    dy=dx
    
    ## setting up output raster with well locations
    well_bundle = np.zeros((len(ys), len(xs)))
    well_bundle =  well_bundle * np.nan
    
    if report:
        print('convert coordinates for',str(len(wells)),'wells')
    
    for well_i, well_index in enumerate(wells.index):
        well_x = wells.loc[well_index, 'X']
        well_y = wells.loc[well_index, 'Y']
        ## get x-coordinate of wells
        for i, x in enumerate(xs):
            if (well_x > (x-dx/2)) & (well_x < (x+dx/2)):
                well_ICOL = i
                wells.loc[well_index, 'ICOL'] = well_ICOL + 1
                break
            ## get y-coordinate of wells
        for j, y in enumerate(ys):
            if (well_y < (y+dy/2)) & (well_y > (y-dy/2)):
                well_IROW = j   
                wells.loc[well_index, 'IROW'] = well_IROW + 1
                break
        well_bundle[j,i] = 1
    if report:
        print('x- and y- coordinates of wells converted to row- and column-numbers')
    return wells, well_bundle


def flowpath_origin(wells, data_ipf, xs, ys, report=False):
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
    data_ipf_well = pd.DataFrame()
    
    if report:
        print('setting up output rasters for origins and traveltimes of provided flowpaths')
    traveltimes = np.zeros((len(ys), len(xs)))
    traveltimes = traveltimes * np.nan
    origin = np.zeros((len(ys), len(xs)))
    origin = origin * np.nan
    
    if report:
        print('importing .ipf flowpath data for',str(len(wells)),'wells')
    for well_i, well_index in enumerate(wells.index):
        well_IROW = wells.loc[well_index, 'IROW']
        well_ICOL = wells.loc[well_index, 'ICOL']
        well_data = data_ipf.loc[(data_ipf.loc[:, 'EP_IROW'] == well_IROW) & (data_ipf.loc[:, 'EP_ICOL'] == well_ICOL)].copy()
        
        if len(well_data) > 0:
            well_data.loc[:, 'Well_nr'] = well_i
            well_data.loc[:, 'Well_code'] = wells.loc[well_index, 'Name']
            data_ipf_well = data_ipf_well.append(well_data)
            for flowpath_i, flowpath_index in enumerate(well_data.index):
                ## note that python starts its counting at 0,0, while iMOD starts at 1,1. We need to correct for this. 
                flowpath_SP_IROW = int(well_data.loc[flowpath_index, 'SP_IROW']) -1
                flowpath_SP_ICOL = int(well_data.loc[flowpath_index, 'SP_ICOL']) -1
                
                traveltimes[flowpath_SP_IROW, flowpath_SP_ICOL] = well_data.loc[flowpath_index, 'TIME(YEARS)']
                origin[flowpath_SP_IROW, flowpath_SP_ICOL] = well_i
    
    return origin, traveltimes, data_ipf_well
