import sys, os

sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

import open_cp
import pyproj
import logging
from open_cp import geometry
import shapely
import geopandas as gpd
import pandas as pd
import json
from pulp import *

from constantmanager import CRS_GRID_DATA, DATE_HOUR, LATITUDE,LONGITUDE, NAME_POLYGON, PREDICT_COLUMN

import requests

url = "http://34.125.152.201/predictions/"
response = requests.get(url+"file:test2-type:Counter")
data,parameters=response.json()["predict_json"]["features"],response.json()["parameters"]
gdf = gpd.GeoDataFrame.from_features(data,crs=parameters["crs_data"])

gdf.set_index("index",inplace=True)

Areas=gdf.index.values
Calls=gdf.Intensity.to_dict()
centroid=gdf.geometry.centroid.to_dict()

Distances={}
Contiguity={}
for i in centroid:
    row_d={}
    Contiguity[i]=[]
    for j in centroid:
        row_d[j]=centroid[i].distance(centroid[j])
        if gdf.loc[i].geometry.intersection(gdf.loc[j].geometry).length>0 and i!=j:
            Contiguity[i].append(j)
    Distances[i]=row_d

TotalBeats = 2 #Sets the number of areas to cluster
#This says what the maximum amount of allowable calls in a particular area
SumCalls = sum(Calls.values())
Disparity = 0.2
MaxIneq = (SumCalls/TotalBeats)*(1 + Disparity) #20% disparity allowed

#1 set up the problem
ChoosePatrol = LpProblem("Creating_Patrol_Areas",LpMinimize)

#2 create decision variables
assign_areas = LpVariable.dicts("Sources and Destinations", [(s,d) for s in Areas for d in Areas], lowBound=0, upBound=1, cat=LpInteger)   

#3 set up the function to minimize  
ChoosePatrol += lpSum(Distances[s][d]*Calls[d]*assign_areas[(s,d)] for s in Areas for d in Areas), "Minimize weighted travel"

#4 Constraint - maximum number of beats
ChoosePatrol += lpSum(assign_areas[(s,s)] for s in Areas) == TotalBeats, "Setting Max number of beats"

#5 Constraint - No offbeat if local beat is not assigned
for s in Areas:
    for d in Areas:
        ChoosePatrol += assign_areas[s,d] <= assign_areas[s,s], "No off-beat if local beat is not assigned, %s %s" % (s,d)

#6 Constraint - every destination area must be covered at least once
for d in Areas:
  ChoosePatrol += sum(assign_areas[(s,d)] for s in Areas) == 1, "Destination Area %s must be covered at least once" % (d)   

#7 Constraint - no source area should have too high a workload
for s in Areas:
  ChoosePatrol += sum(assign_areas[(s,d)]*Calls[d] for d in Areas) <= MaxIneq, "Source Area %s needs to have less call weight than %s"% (s,MaxIneq)

#8 Constraint - areas need to be contiguous
for s in Areas:
    for d in Areas:
        ChoosePatrol += lpSum(assign_areas[(s,a)] for a in Contiguity[d]) >= assign_areas[(s,d)]

ChoosePatrol.solve()
print("Status is %s, The total weighted travel is %d" % (LpStatus[ChoosePatrol.status],value(ChoosePatrol.objective)))
results = []
for s in Areas:
    for d in Areas:
        if assign_areas[(s,d)].varValue == 1.0:
            results.append((s,d,Distances[s][d],Calls[d],Calls[d]*Distances[s][d]))

r={"index":[],"cluster":[]}
for i in results:
    r["index"].append(i[1])
    r["cluster"].append(i[0])

clusters=pd.DataFrame(r).set_index("index")

opti=pd.merge(gdf,clusters,left_index=True,right_index=True).reset_index()

flags=0
for idx,i in enumerate(opti.cluster.unique()):
    flags+=(opti.cluster == i)*(idx+1)
opti["cluster_id"]=flags

print(opti)