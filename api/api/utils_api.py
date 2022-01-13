import pandas as pd
import sys, os
import geopandas as gpd

from predictions.models import Prediction,Aditionalevent, Cleanevent
from predictions.models import ADITIONAL_COLUMNS, ADITIONAL_TYPES, ID
import json

sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))))

from descriptions.clean_descripcion_DB import clean_df
from prediction.prediction import do_predict
from constantmanager import CRS_GRID_DATA
def names_to_representation(model):
    try:
        relations=[]
        for field in model._meta.fields:
            relations.append(field.get_attname_column())
        return relations[1:]
    except:
        return Exception("Error function names_to_representation")

def uploadCleanData(df):
    
    try:
        
        map_columns=names_to_representation(Cleanevent)
        map_columns={i[1]:i[0] for i in map_columns}
        df=df.set_index(ID)
        dict_data=df.to_dict("index")
        
        list_items = []
        for i in dict_data:
            dict_object={map_columns[ID]:i}
            for j in map_columns:
                if j == ID:
                    continue
                dict_object[map_columns[j]]=dict_data[i][j]
            list_items.append(dict_object)
        clean_records=[Cleanevent(**i) for i in list_items]
        Cleanevent.objects.bulk_create(clean_records)
        
        created=Cleanevent.objects.filter(id_ori__in=list(dict_data.keys()))
        list_aditional=[]
        for i in created:
            id = i.id_ori
            for j in ADITIONAL_COLUMNS + ADITIONAL_TYPES:
                list_aditional.append({"event":i,"name_column": j, "values_column": dict_data[id][j]})
        
        
        add_records = [Aditionalevent(**i) for i in list_aditional]
        
        Aditionalevent.objects.bulk_create(add_records)
        
        return len(clean_records)
    except:
        return Exception("Error function uploadCleanData")
    
def makecleandata(data):
    try:
        data, data_polygons, log = clean_df(data)
        return data, data_polygons, log
    except:     
        return Exception("Error in funcion makecleandata")

def testuploddata():
    xls = pd.ExcelFile('/home/cpulido/TM/TM_proyect/TM cases and logs.xlsx')
    events = pd.read_excel(xls, 'CaseLog')
    data,data_polygons,log = makecleandata(events)
    uploadCleanData(data)
    parameters={"file":"polygons","crs_data":CRS_GRID_DATA}
    parameters= json.loads(json.dumps(parameters,indent=4))
    json_predict=json.loads(data_polygons.to_json())
    Prediction.objects.get_or_create(parameters=parameters,predict_json=json_predict)
    
def testpredict(parameters):
    
    P=Prediction.objects.get(parameters__file="polygons")
    gdf = gpd.GeoDataFrame.from_features(P.predict_json["features"],crs=P.parameters["crs_data"])
    events=Cleanevent.objects.all()
    events=pd.DataFrame.from_records(events.values("latitude","longitude","name_poly","date_hour"))
    map_columns=names_to_representation(Cleanevent)
    map_columns={i[0]:i[1] for i in map_columns}
    events=events.rename(columns={i:map_columns[i] for i in events.columns})
    predict_gpd=do_predict(events,gdf,"746",50000,50000)
    
    parameters["crs_data"]=CRS_GRID_DATA
    parameters= json.loads(json.dumps(parameters,indent=4))
    json_predict=json.loads(predict_gpd.to_json())
    P=Prediction.objects.get_or_create(parameters=parameters,predict_json=json_predict)
    return P[0]    
