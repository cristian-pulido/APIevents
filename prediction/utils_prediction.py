import sys, os

sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

import open_cp
import pyproj
import logging
from open_cp import geometry
import shapely
import geopandas as gpd

from constantmanager import CRS_GRID_DATA, DATE_HOUR, LATITUDE,LONGITUDE, NAME_POLYGON, PREDICT_COLUMN

def getOpenCPData(df, projectionStr='EPSG:3857',date_hour=DATE_HOUR,lon=LONGITUDE,lat=LATITUDE):
    '''
    Convert the data to OpenCP format
    
    Parameters
    ----------
    df: pandas.DataFrame
        The date frame with the points to train the model
    projectionStr: str
        String to set the projection with pyproj ('EPSG:3857' default)
    
    Returns
    -------
    points: open_cp.TimePoints
        array of time points in open cp format
        
    Raises
    ------
    Exception if the projections returns no values for the dataframes
    
    '''
    try:
        logging.debug("Creation openCP data")
        proj = pyproj.Proj( projectionStr )
        
        timestamps = df[date_hour].values
        # Activo si hay que proyectar de geográficas a planas------------------------------------------------
        xcoords, ycoords = proj(df[lon].values, df[lat].values)
        # Si no hay datos lanza una exception
        if len(xcoords)==0:
            raise Exception('No projection for the given dataframe longitudes and latitudes')
        
        points = open_cp.TimedPoints.from_coords(timestamps, xcoords, ycoords)
        return points
    except:
        msg_error = "Error in creation opencp data function getOpenCPData"
        logging.error(msg_error)
        raise Exception(msg_error)


def prepare_data_region(df,name,df_polys,wX,wY,col_poly=NAME_POLYGON,projectionStr='EPSG:3857'):
    '''
    configure data and polygons to format used by OpenCP
    
    Parameters
    ----------
    df: pandas.DataFrame
        The date frame with the points to train the model
    name: str
        The name of polygon used 
    df_polys: geopandas.geodataframe.GeoDataFrame
        The data frame with information about polygons
    wX: int
        x block size
    wY: int
        y block size
    col_poly: str
        Name of column dataframes that contains the names of polygons
    projectionStr: str
        String to set the projection with pyproj ('EPSG:3857' default)
    
    Returns
    -------
    data_test: open_cp.TimePoints
        array of time points in open cp format
    grid2: open_cp.data.MaskedGrid 
    '''
    try:
        logging.debug("Format data and polygons to OpenCP functions")
        data_test=df[ df[col_poly] == name]
        poly=df_polys[df_polys[col_poly] == name]
        poly.to_crs(projectionStr,inplace=True)
        geo=list(poly.geometry)[0]
        grid=open_cp.data.Grid(wX,wY,0,0)
        grid2=geometry.mask_grid_by_intersection(geo, grid)
        return data_test, grid2
    except :
        msg_error = "Error in format data  function prepare_data_region"
        logging.error(msg_error)
        raise Exception(msg_error)
    
    
def predict_to_geopandas(Predict,column_predict=PREDICT_COLUMN,projectionStr=CRS_GRID_DATA):
    '''
    convert prediction openCP to geopandas dataframe
    
    Parameters
    ----------
    Predict: open_cp.predictors.GridPredictionArray
        Array of prediction given by opencp
    column_predict: str
        The name of prediction column y resulting df
    projectionStr: str
        String to set the projection with pyproj ('CRS_GRID_DATA' default)
    
    Returns
    -------
    R: geopandas.geodataframe.GeoDataFrame
        geopnadas dataframe resulting
    '''
    try:
        logging.debug("Convert prediction openCP to geopandas")
        y_index,x_index=Predict.intensity_matrix.shape
        y_index,x_index

        x_coors,y_coors=Predict.mesh_data()[0],Predict.mesh_data()[1]

        result = []
        for i in range(x_index):
            for j in range(y_index):
                x0= x_coors[i]
                x1 = x_coors[i+1]
                y0= y_coors[j]
                y1 = y_coors[j+1]
                result.append( [ Predict.intensity_matrix[j][i],shapely.geometry.box(x0, y0, x1, y1) ])

        R=gpd.GeoDataFrame(result,columns=[column_predict,"geometry"],crs="EPSG:3857")
        R.to_crs(projectionStr,inplace=True)
        R= R.reset_index()
        R["index"]=R["index"].astype(str)
        #R.to_file("predict.geojson", driver='GeoJSON')
        return R
    except :
        msg_error = "Error in convert prediction openCP to geopandas dataframe  function predict_to_geopandas"
        logging.error(msg_error)
        raise Exception(msg_error)
    