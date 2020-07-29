import gdal
import osr


#%%

def save_ipf_as_tif(Raster, ipf_xs, ipf_ys, file_path, file_name):
    '''
    saves .ipf rasters as .tif files, in RD_new format. 
    
    
    Parameters
    ----------
    Raster : array
        Raster containing raw data of saved .tif file
    ipf_xs : array
        x-coordinates of imported .ipf file. In RD_new crs format!
    ipf_ys : array
        y-coordinates of imported .ipf file. In RD_new crs format!
    file_path : str
        Basepath to saved .tif file
    file_name : str
        Basename of saved .tif file
    report : bool
        boolean to print progress report. Either True or False. The default is False
    
    Returns
    -------
    
    '''
    
    ## Setting up GeoTransform, by calculating dx and dy. 
    dx = (ipf_xs[1:-1] - ipf_xs[0:-2]).mean()
    dy = (ipf_ys[1:-1] - ipf_ys[0:-2]).mean()
    ## GeoTransform [x_ul, dx, x_rtn, y_ul, y_rtn, dy]. x_rtn = rotation over x, y_rtn = rotation over y. 
    ## Assumes that ipf_coordinates refer to cellcenters, while .tif refers to upperleft corner of cells. 
    GeoTrans = [ipf_xs.min()-dx/2, dx, 0.0, ipf_ys.max()-dy/2, 0.0, dy]      
    
    ## Set up driver
    Driver = gdal.GetDriverByName("GTiff")  
    Driver_data = Driver.Create(file_path+'\\'+file_name+'.tif', Raster.shape[1], Raster.shape[0], 1, gdal.GDT_Float32)
    Driver_data.SetGeoTransform(GeoTrans)
    
    ## Set up spatial referencing using Proj4
    ## Assumes RD_new format!!!
    SRS = osr.SpatialReference()
    Proj4_string = "+proj=sterea +lat_0=52.1561605555556 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +y_0=463000 +ellps=bessel +towgs84=565.2369,50.0087,465.658,-0.406857330322398,0.350732676542563,-1.8703473836068,4.0812 +units=m +no_defs"
    SRS.ImportFromProj4(Proj4_string)
    
    ## Apply spatial referencing, raster information and no data value to driver. 
    Driver_data.SetProjection( SRS.ExportToWkt() )
    Driver_data.GetRasterBand(1).WriteArray(Raster)
    Driver_data.GetRasterBand(1).SetNoDataValue(9999)
    
    ## Close Driver, aka save your geotiff!!
    Driver_data = None
    return print('GeoTiff saved in',file_path)