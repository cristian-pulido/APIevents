import sys, os


sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

from prediction.utils_prediction import *
from prediction.PredictionModels import *


def do_predict(data,data_polygons,name_poly,wX,wY):
    '''
    
    
    Parameters
    ----------
    Predict: open_cp.predictors.GridPredictionArray
        Array of prediction given by opencp
   
    Returns
    -------
    R: geopandas.geodataframe.GeoDataFrame
        geopnadas dataframe resulting
    '''
    try:
        logging.debug("process predict")
        data_test, grid = prepare_data_region(data,name_poly,data_polygons,wX,wY,col_poly=NAME_POLYGON,projectionStr='EPSG:3857')
        PM=Counter('ej',data_test,grid.region(),grid,wX,wY)
        Predict=PM.predict("a","b")
        Predict=Predict.renormalise()
        predict_gpd=predict_to_geopandas(Predict)
        return predict_gpd
        
    except :
        msg_error = "Error in process predict function do_predict"
        logging.error(msg_error)
        raise Exception(msg_error)
    