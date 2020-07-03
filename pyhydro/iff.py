import numpy as np
import pandas as pd
import geopandas as gpd
import shapely

#%%

def import_iff(path_iff, report=False):
    '''
    Import data from .iff iMOD flowpath file and return dataframe
    
    
    Parameters
    ----------
    path_iff : str
        Path to .iff file
    report : bool
        boolean to print progress report. Either True or False. The default is False

    Returns
    -------
    data : pd.DataFrame
        dataframe with flowpath data of imported .iff file
    '''
    
    
    ## Open .iff file
    iff_header = {}
    iff = open(path_iff, 'r')
    if report:
        print('Importing',path_iff,'to dataframe')
    
    ## Import header of .iff file
    # Read number of columns in .iff file
    ncols = int(iff.readline().strip('\n'))

    # Read column names in .iff file
    for i in range(ncols):
        iff_header[i] = iff.readline().strip('\n')
    
    ## Import flowpath data of .iff file
    data = []
    line = ''
    while line != '\n':
        line = iff.readline()
        if not line:
            break
        line = line.strip('\n')
        lineparts = line.split(' ')
        lineparts = np.array(lineparts)[np.array([len(part) > 0 for part in lineparts]) == True].astype(np.float)
        data.append(lineparts)
    data = pd.DataFrame(data=data, columns=list(iff_header.values()))

    ## Close .iff file
    iff.close()
    if report:
        print('iMOD flowpath file .iff imported with',len(data.loc[:, 'PARTICLE_NUMBER'].unique()),'flowpaths.')
    return data


def extract_endpointwell(data, well_cells, report=False):
    '''
    Extract all flowpaths which end up at wells. 
    
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with imported .iff flowpath data
    well_cells : list
        List containing locations [row, column] of all well cells.
        Example for two wells at cells (10,20) and (5, 10): well_cells = [[10, 20], [5, 10]]
    report : bool
        boolean to print progress report of function. Either True or False. The default is False.

    Returns
    -------
    data_output : pd.DataFrame
        Dataframe containing flowpath data of all flowpaths that end up in given well cells.

    '''

    if report:
        print('Starting extraction of flowpaths that end up in wells.')
        print('Provided wells:')
        print('     ',well_cells)
    particles = []
    for i, well_cell in enumerate(well_cells):
        row, col = well_cell
        particles_endpoint = data.loc[(data.loc[:, 'IROW'] == row) & (data.loc[:, 'ICOL'] == col), 'PARTICLE_NUMBER'].unique()
        particles.extend(particles_endpoint)
    
    if report:
        print('Flowpaths extracted.')
        print('Saving extracted flowpaths to DataFrame...')
    data_output = []
    for i, particle in enumerate(particles):
        data_particle = data.loc[data.loc[:, 'PARTICLE_NUMBER'] == particle].values
        data_output.extend(data_particle)
    data_output = pd.DataFrame(data=data_output, columns=data.columns)
    if report:
        print('Extracted flowpaths saved to DataFrame.')
    return data_output


def invert_flowpath(data, report=False):
    '''
    Function to change direction of flow of particle along a flowpath, thus inverting the travel time along a flowpath.
    
    
    Parameters
    ----------
    data : pd.DataFrame
        Dataframe of imported .iff IMOD Flowpath File of which flowdirection needs to be inverted.
    report: bool
        boolean to print progress report of function. Either True or False. The default is False.
    
    Returns
    -------
    data_inverted : pd.DataFrame
        DataFrame containing flowpath data with inverted direction of flow.
    '''
    
    particles = data['PARTICLE_NUMBER'].unique()
    if report:
        print('Inverting direction of flow of',len(particles),'particles in .iff IMOD Flowpath File.')
    
    ## For every particle in .iff file, reverse time, by substracting time of particle from maximum time.
    data_inverted = data.copy()
    for particle in particles:
        index_max = data_inverted.loc[data_inverted.loc[:, 'PARTICLE_NUMBER'] == particle, 'TIME(YEARS)'].idxmax()
        data_inverted.loc[data_inverted.loc[:, 'PARTICLE_NUMBER'] == particle, 'TIME(YEARS)'] = data_inverted.loc[index_max, 'TIME(YEARS)'] - data_inverted.loc[data_inverted.loc[:, 'PARTICLE_NUMBER'] == particle, 'TIME(YEARS)']
    
    return data_inverted


def cutoff_flowpath(data, tmax=25, report=False):
    '''
    Function to cutoff flowpaths at give time tmax. 

    Parameters
    ----------
    data : pd.DataFrame
        Dataframe which contains the imported flowpath data.
    tmax : np.float
        Time in years at which the flowpaths in 'data' are cutted off. Default is 25 years.
    report: bool
        boolean to print progress report of function. Either True or False. The default is False.
    
    Returns
    -------
    Data : pd.DataFrame
        Dataframe which contains the flowpaths which are cutted off at time tmax.
    '''
    
    if report:
        print('Cutting off time of flowpaths at', str(tmax),'year(s).')
    data_output = data.copy()
    data_output = data_output.loc[data_output.loc[:, 'TIME(YEARS)'] < tmax]
    
    return data_output


def get_geometry(data, line_type='single_line', crs={'init':'epsg:28992'}, save_shp=False, path_output='Output_lines.shp', report=False):
    '''
    Retrieves geometry data of flowpath dataframe and optionally saves geodataframe to shapefile.


    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing flowpath data of which line geometry is retrieved.
    line_type : str
        Defines the output line type. Each flowpath is either saved as a single part line (single_line), 
        or divided in multi parts lines (multi_line). The default is 'single_line'.
    crs : dictionary
        Describes coordinate reference system of shapefile. The default is {'init':'epsg:28992'}, which is RD_new.
    save_shp : bool
        Either True or False. If True, derived geometry of flowpaths is saved to shapefile. The default is False.
    path_output : str
        Output path of shapefile. The default is 'Output_lines.shp'.
    report: bool
        boolean to print progress report of function. Either True or False. The default is False.

    Returns
    -------
    flowpaths_gdf : gpd.GeoDataFrame
        Output geopandas GeoDataFrame with flowpaths, in single_line or multi_line format.
        In case when save_shp is True, the GeoDataFrame is saved to an Esri Shapefile called path_output.

    '''
    
    ## Copy data of flowpaths
    particles = data.loc[:, 'PARTICLE_NUMBER'].unique()

    ## Save each flowpath as a single line
    if line_type == 'single_line':
        if report:
            print('Deriving geometry for single-part flowpaths.')

        line_particle_data = []
        for i, particle in enumerate(particles):
            data_particle = data.loc[data.loc[:, 'PARTICLE_NUMBER'] == particle, :]
            data_particle = data_particle.sort_values(by='TIME(YEARS)', ascending=True)
            coordinates_particle = [xy for xy in zip(data_particle['XCRD.'], data_particle['YCRD.'])]
            if len(coordinates_particle) > 1:
                ## merge all parts of flowpath to a single Linestring
                line_particle = shapely.geometry.LineString(coordinates_particle)
                line_particle_data.append([particle,
                                          data_particle.loc[:, 'TIME(YEARS)'].min(),
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmin(), 'XCRD.'],
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmin(), 'YCRD.'],
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmin(), 'ZCRD.'],
                                          data_particle.loc[:, 'TIME(YEARS)'].max(),
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmax(), 'XCRD.'],
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmax(), 'YCRD.'],
                                          data_particle.loc[data_particle.loc[:, 'TIME(YEARS)'].idxmax(), 'ZCRD.'],
                                          line_particle])
        gdf_singles = gpd.GeoDataFrame(data=line_particle_data, crs=crs,
                                       columns=['PARTICLE_NUMBER', 'T_start', 'X_start', 'Y_start', 'Z_start', 'T_end', 'X_end', 'Y_end', 'Z_end', 'geometry'])

        ## In case of save_shp == True, the geodataframe is saved to a shapefile as well.
        flowpaths_gdf = gdf_singles.copy()
        if save_shp:
            flowpaths_gdf.to_file(drive='Esri Shapefile', filename=path_output)
            if report:
                print('Geometry of single part flowpath is saved to shapefile:',path_output)



    ## Save all individual parts of each flowpath.
    elif line_type == 'multi_line':
        if report:
            print('Deriving geometry for multi-part flowpaths.')
            
        line_particle_data = []
        for particle in particles:
            data_particle = data.loc[data.loc[:, 'PARTICLE_NUMBER'] == particle, :]
            data_particle = data_particle.sort_values(by='TIME(YEARS)', ascending=True)
            coordinates_particle = [xy for xy in zip(data_particle['XCRD.'], data_particle['YCRD.'])]
            index_particle = data_particle.index
            
            if len(coordinates_particle) > 1:
                ## Write all indidual parts of flowpath to multiple linestrings. 
                for i in np.arange(1, len(coordinates_particle), 1):
                    coordinates_step = [coordinates_particle[i-1], coordinates_particle[i]]
                    line_particle = shapely.geometry.LineString(coordinates_step)
                    line_particle_data.append([particle, 
                                                data_particle.loc[index_particle[i-1], 'TIME(YEARS)'],
                                                data_particle.loc[index_particle[i-1], 'XCRD.'],
                                                data_particle.loc[index_particle[i-1], 'YCRD.'],
                                                data_particle.loc[index_particle[i-1], 'ZCRD.'],
                                                data_particle.loc[index_particle[i], 'TIME(YEARS)'],
                                                data_particle.loc[index_particle[i], 'XCRD.'],
                                                data_particle.loc[index_particle[i], 'YCRD.'],
                                                data_particle.loc[index_particle[i], 'ZCRD.'],
                                                line_particle])

        flowpaths_gdf = gpd.GeoDataFrame(data=line_particle_data, crs=crs, columns=['Particle', 'T_start', 'X_start', 'Y_start', 'Z_start', 'T_end', 'X_end', 'Y_end', 'Z_end', 'geometry'])
        
        ## In case of save_shp == True, the geodataframe is saved to a shapefile as well.
        if save_shp:
            flowpaths_gdf.to_file(drive='Esri Shapefile', filename=path_output)
            if report:
                print('Geometry of multi parts flowpaths is saved to shapefile:',path_output)
    return flowpaths_gdf


def dissolve_geometry(data_gdf, save_shp=False, path_output='Output_DissolvedLines.shp', report=False):
    '''
    Function to dissolve geometry of imported flowpath data.


    Parameters
    ----------
    data_gdf : gpd.GeoDataFrame
        GeoDataFrame containing geometry of the imported flowpath data
    save_shp : bool
        Either True or False. If True, the dissolved flowpaths are saved to shapefile. The default is False.
    path_output : str
        Output path of shapefile. The default is Output_DissolvedLines.shp'.
    report: bool
        boolean to print progress report of function. Either True or False. The default is False.

    Returns
    -------
    data_gdf_dissolved : gpd.GeoDataFrame
        Output GeoDataFrame containing geometry of the dissolved flowpath data.

    '''
    
    if report:
        print('Dissolving geometry of flowpaths.')
    lines = []
    indices = data_gdf.index
    ## Stacking Linestrings of flowpaths into MultiLineString.
    for index in indices:
        coords_line = data_gdf.loc[index, 'geometry'].coords[:]
        lines.append(tuple(coords_line))
    lines_dissolved = shapely.geometry.MultiLineString(lines)
    
    ## Saving dissolved flowpath data to geodataframe.
    data_gdf_dissolved = gpd.GeoDataFrame(columns=['Name', 'geometry'])
    data_gdf_dissolved.loc[0] = ['Dissolved', lines_dissolved]
    
    if save_shp:
        data_gdf_dissolved.to_file(filename=path_output, drive='Esri Shapefile')
        if report:
            print('Geometry of dissolved flowpaths is saved to shapefile:',path_output)
    return data_gdf_dissolved
    

def get_convexhull(data_gdf_dissolved, save_shp=False, path_output='Output_ConvexHull.shp', report=False):
    '''
    Function to generate convex hull of dissolved flowpaths.

    Parameters
    ----------
    data_gdf_dissolved : gpd.GeoDataFrame
        GeoDataFrame which contains geometry of dissolved flowpaths
    save_shp : bool
        Either True or False. If True, the convex hull is saved to shapefile. The default is False.
    path_output : str
        Output path of shapefile. The default is Output_ConvexHull.shp'.
    report: bool
        boolean to print progress report of function. Either True or False. The default is False.
    
    Returns
    -------
    data_gdf_convexhull : gpd.GeoDataFrame
        Output GeoDataFrame containing the geometry of generated convex hull.

    '''
    
    if report:
        print('Generating convex hull of dissolved flowpaths.')
    convexhull_geom = data_gdf_dissolved.convex_hull.loc[0]
    data_gdf_convexhull = gpd.GeoDataFrame(columns=['Name', 'geometry'])
    data_gdf_convexhull.loc[0] = ['ConvexHull', convexhull_geom]
    
    if save_shp:
        data_gdf_convexhull.to_file(filename=path_output, drive='Esri Shapefile')
        if report:
            print('Geometry of generated convex hull is saved to shapefile:',path_output)
    return data_gdf_convexhull

