import imod
import numpy as np

#%%
def import_idf(path_idf):
    '''
    Function to import .idf file as a raster. 
    Returns idf raster values, coordinates and extent. 
    
    Parameters
    ----------
    path_idf : str
        path to the .idf file. 

    Returns
    -------
    idf_values : array
        array containing all .idf raster values.
    idf_extent : array
        coordinates of upper left and lower right corner: [UL_x, UL_y, LR_x, LR_y].
    idf_xs : array
        x-coordinates of imported raster. coordinates refer to cell-centers.
    idf_ys : array
        y-coordinates of imported raster. coordinates refer to cell centers.
    
    '''
    
    ## Import idf via path
    idf = imod.idf.open_dataset(path_idf)
    idf_key = list(idf.keys())[0]
    idf_data = idf[idf_key]
    
    ## Get raster values
    idf_values = idf_data.values
    
    ## Get raster coordinates
    idf_xs = idf_data.x.values
    idf_ys = idf_data.y.values
    
    ## Get dx and dy
    idf_dx = np.float(idf_data.dx.values)
    idf_dy = np.float(idf_data.dy.values)
    
    ## Get coordinates of extent, and correct at corners using dx and dy.
    ul_idf_x, ul_idf_y = idf_xs[0], idf_ys[0]
    lr_idf_x, lr_idf_y = idf_xs[-1], idf_ys[-1]
    ul_extent_x = ul_idf_x - abs(idf_dx)/2
    ul_extent_y = ul_idf_y + abs(idf_dy)/2
    lr_extent_x = lr_idf_x + abs(idf_dx)/2
    lr_extent_y = lr_idf_y - abs(idf_dy)/2
    
    ## Define extent, using upper left and lower right coordinates.
    idf_extent = [ul_extent_x, ul_extent_y, lr_extent_x, lr_extent_y]
    return idf_values, idf_extent, idf_xs, idf_ys