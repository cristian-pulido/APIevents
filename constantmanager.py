#COLUMNS DATA
ID = "CaseID"
DATETIME = "StartTime"
EVENTS_TYPE = "CaseTypeName"
LATITUDE = "Location_Lat"
LONGITUDE = "Location_Lng"
ADITIONAL_TYPES = ["ShipType"]
ADITIONAL_COLUMNS = ["CloseTime",'NumLogs','CaseTypeId']

#COLUMNS GEOJSON DATA
NAME_POLYGON='poly_name'

#FORMAT DATA
DATE_FORMAT="%Y-%m-%d %H:%M:%S"
CRS_GRID_DATA="EPSG:4326"#"+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +a=6371007.181 +b=6371007.181 +units=m +no_defs"
N_CELLS_GRID =30

#NEW COLUMNS NAMES FOR DATA
FREQUENCY = "Frequency"
PERCENTAGE = "Percentage"
DATE_HOUR =  "Date_Hour"
DATE = "DATE"
TIME = "Time"
YEAR = "Year"
MONTH = "Month"
DAY_WEEK = "Day_week"
HOUR_NUMBER = "Hour"
#NEW COLUMNS NAMES FOR TABLES API
PARAMETERS_PREDICT = "parameters"
PREDICT_JSON = "predict_json"





PREDICT_COLUMN = "Intensity"

#Folder particular proyect 
FOLDER_PROYECT = "/home/cpulido/TM/TM_proyect/"
