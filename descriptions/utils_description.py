import sys, os


sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, HTML
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import folium
from folium import plugins
import logging
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import shapely

from constantmanager import FREQUENCY,PERCENTAGE,LONGITUDE,LATITUDE, CRS_GRID_DATA, N_CELLS_GRID, NAME_POLYGON

'''
Functions that help print data or create subsets of data
and tables and figures to save later
'''

def create_Subdata(df,variables_array):
    '''
    Create a subset of a dataframe from a list of the columns 
    that will make it up and add the Frequency column that 
    counts the occurrences when grouping by the list of variables.
    
    Arguments:
    ---------
        df: pandas dataframe
        variables_array: list of variables to create the subset
    Returns:
    -------
        subdata: result of subset dataframe
    '''
    try:
        logging.debug('Creation subdata with columns '+', '.join(variables_array))
        subdata=pd.DataFrame(df.groupby(variables_array).size(),columns=[FREQUENCY]).sort_index().reset_index()
        subdata.sort_values(FREQUENCY,ascending=0,inplace=True)
        return subdata
    except:
        msg_error = "Error in creation subset with columns "+', '.join(variables_array)
        logging.error(msg_error)
        raise Exception(msg_error)

def bar_figure_top_values(df,variable,frequency=FREQUENCY,to_show=10):
    '''
    Create a bar graph according to a variable and its frequency in a
    dataframe. If the quantity is greater than 22 just draw the top defined by
    to_show

    Arguments:
    ---------
        df: pandas dataframe with the data to show and the frequency column
        variable: name of column to show
        frequency: name frequency column
        to_show: amount of rows to plot
    Returns:
    -------
        fig: figure of plotly bar instance
    
    
    '''
    try:
        logging.debug('Creation bar figure top values with column '+str(variable))
        if len(df)>22:
            topdata=(df.sort_values(by=[frequency],ascending=False)[:to_show])
        else:
            topdata=df.sort_values(by=[frequency],ascending=False)
            
        fig = px.bar(topdata, x=frequency, y=variable, orientation='h', color = variable, 
                color_discrete_sequence = px.colors.qualitative.Prism[2:])
        fig.update_layout(yaxis={"type":"category"}, showlegend=False)
        plt.close('all')
        return fig
    except:
        msg_error = "Error in creation bar figure top values"
        logging.error(msg_error)
        raise Exception(msg_error)

def line_figure(df,variable,min_values=0,max_values=0,frequency=FREQUENCY):
    '''
    Create a line graph according to a variable and its frequency in a
    dataframe. A certain number of minimum and maximum values ​​are indicated with text.

    Arguments:
    ---------
        df: pandas dataframe with the data to show and the frequency column
        variable: name of column to show
        min_values: amount of minimun values to show
        max_values: amount of maximun values to show
        frequency: name frequency column
    Returns:
    -------
        fig: figure of plotly line instance
    '''
    try:
        logging.debug('Creation line figure with column '+str(variable))
        fig = px.line(df, x=variable, y=frequency, color_discrete_sequence = px.colors.qualitative.Prism[1:])
        fig.update_xaxes(title=variable)
        fig.update_yaxes(title=frequency)
        fig.update_layout(
            annotations=[
                go.layout.Annotation(
                x=i[0],
                y=i[1],
                xref="x",
                yref="y",
                showarrow=False,
                text=str(i[0])+" : "+str(i[1]),
                font=dict(
                    family="Courier New, monospace",
                    size=16,
                    color="black"
                ),
            ) for i in df.sort_values(frequency).head(min_values).append(df.sort_values(frequency).tail(max_values))[[variable,frequency]].values
            ]
        )
        plt.close('all')
        return fig
    except:
        msg_error = "Error in creation line figure"
        logging.error(msg_error)
        raise Exception(msg_error)

def bar_figure_probabilities(df,variable,values_order=None,media_factor=1,frequency=FREQUENCY):
    '''
    Create a bar graph with the probabilities according to a variable and its 
    frequency in a dataframe. 
    
    Arguments:
    ---------
        df: pandas dataframe with the data to show and the frequency column
        variable: name of column to show
        values_order: order of values ​​to present the variable
        media_factor: number of times each of the variables is repeated
        frequency: name frequency column
    Returns:
    -------
        fig: figure of plotly bar instance
    '''
    try:
        if values_order == None:
            values_order=df[variable].unique()
        logging.debug('Creation bar figure probabilities with column '+str(variable))
        df[PERCENTAGE]=df[frequency]/df[frequency].sum()*100
        fig=px.bar(df,x=PERCENTAGE,color=variable,y=variable,orientation='h',
                category_orders={variable: values_order},
                color_discrete_sequence = px.colors.qualitative.Prism[1:])
        fig.update(layout_showlegend=False)

        fig.add_trace(go.Scatter(
            x=[df.Percentage.mean()]*2,
            y=[values_order[0],values_order[-1]],
            text=['Mean='+str(round(df[frequency].mean()/media_factor,2)),
                ''
                ],
            line=dict(color='black', width=2),
            mode="text+lines",
        ))
        fig.add_trace(go.Scatter(
            x=[df.Percentage.mean()+df.Percentage.std()]*2,
            y=[values_order[0],values_order[-1]],
            text=['',
                'std='+str(round(df[frequency].std()/media_factor,2)),
                ],
            line=dict(color='black', width=2,
                                    dash='dash'),
            mode="text+lines",
        ))
        fig.add_trace(go.Scatter(
            x=[df.Percentage.mean()-df.Percentage.std()]*2,
            y=[values_order[0],values_order[-1]],
            text=['',
                'std='+str(round(df[frequency].std()/media_factor,2)),
                ],
            line=dict(color='black', width=2,
                                    dash='dash'),
            mode="text+lines",
        ))
        plt.close('all')
        return fig
    except:
        msg_error = "Error in creation bar figure probabilities"
        logging.error(msg_error)
        raise Exception(msg_error)

def bubbles_figure_probabilities(df,var1,var2,var1_order=[],var2_order=[],frequency=FREQUENCY):
    '''
    Create a bubble plot with the joint probabilities between two variables.
    
    Arguments:
    ---------
        df: pandas dataframe with the data to show and the joint frequency column
        var1: name of column first variable to show
        var2: name of column second variable to show
        var1_order: order of values of first variable ​​to present
        var2_order: order of values of second variable ​​to present
        frequency: name frequency column
    Returns:
    -------
        fig: figure of plotly bubble instance
    '''
    try:
        if len(var1_order) == 0:
            var1_order = df[var1].unique()
        if len(var2_order) == 0:
            var2_order = df[var2].unique()
        logging.debug('Creation bubble figure probabilities with columns '+str(var1) +" and "+str(var2))
        df[PERCENTAGE]=df[frequency]/df[frequency].sum()*100
        fig = px.scatter(df, x=var1, y=PERCENTAGE, size=PERCENTAGE, color=var2,
                        width=1000, height=600, color_discrete_sequence = px.colors.qualitative.Prism[1:],
                        category_orders={var2: var2_order}, hover_name=var2, size_max=40)
        fig.update_xaxes(tickangle=0,categoryorder="array", categoryarray=var1_order)
        if len(df[var1].unique()) > 10:
            fig.update_xaxes(tickangle=90)
        plt.close('all')
        return fig
    except:
        msg_error = "Error in creation bubble figure probabilities"
        logging.error(msg_error)
        raise Exception(msg_error)

def get_probabilities_matrices(df,var1,var2,var1_order=[],var2_order=[],frequency=FREQUENCY):
    '''
    Create the joint and conditional probability matrices given two variables
    
    Arguments:
    ---------
        df: pandas dataframe with the data to show and the joint frequency column
        var1: name of column first variable to show
        var2: name of column second variable to show
        var1_order: order of values of first variable ​​to present
        var2_order: order of values of second variable ​​to present
        frequency: name frequency column
    Returns:
    -------
        M: list of resuts matrices(pandas dataframes) joint - given column - given rows
    '''
    try:
        logging.debug('Creation tables probabilities matrices with columns '+str(var1) +" and "+str(var2))
        A=df.copy()
        A[PERCENTAGE]=A[frequency]/A[frequency].sum()
        join=(A.pivot(var1,var2,PERCENTAGE)).fillna(0)
        if len(var1_order) == 0:
            var1_order = df[var1].unique()
        if len(var2_order) == 0:
            var2_order = df[var2].unique()
        join = join.reindex(var2_order, axis=1)
        join = join.reindex(var1_order)
        gc=join/join.sum(axis=0)
        gf=(join.T/join.sum(axis=1)).T
        M=[join,gc,gf]
        return M

    except:
        msg_error = "Error in creation tables probabilities matrices"
        logging.error(msg_error)
        raise Exception(msg_error)

def heatmap_figure_probabilities(df,given='join'):
    '''
    Create a heat map plot with the given probabilities between two variables.
    
    Arguments:
    ---------
        df: pandas dataframe with the data to show
    Returns:
    -------
        fig: figure of matplotlib heatmap instance
    '''
    try:
        logging.debug("Creation heatmap figure probabilities")
        fig, ax = plt.subplots(1,1,sharex=True, sharey=True)
        fig.set_size_inches(10, 9)
        rows,cols=df.shape
        if rows > 12:
            order_rows=df.index
            row_index=list(df.sum(axis=1).sort_values(ascending=False).head(12).index)
            row_index=list(pd.Series(order_rows)[pd.Series(order_rows).isin(row_index)].values)
        else:
            row_index = df.index
        if cols > 12:
            order_cols=df.columns
            col_index=list(df.sum().sort_values(ascending=False).head(12).index)
            col_index=list(pd.Series(order_cols)[pd.Series(order_cols).isin(col_index)].values)
        else:
            col_index = df.columns
            
        df=df[df.index.isin(row_index)][col_index]
        g=sns.heatmap(df,vmin=0, vmax=0.4,annot=True,fmt=".1%",linewidths=0,cmap="Blues",cbar=False)
        g.set_yticklabels(g.get_yticklabels(), rotation = 0)
        if (given == 'join') | (given == 'column'):
            ax.vlines(np.arange(cols+1), *ax.get_ylim())
        if (given == 'join') | (given == 'row'):            
            ax.hlines(np.arange(rows+1), *ax.get_xlim())
        fig.patch.set_facecolor('white')
        plt.close('all')
        return fig
    except:
        msg_error = "Error in creation heatmap figure probabilities"
        logging.error(msg_error)
        raise Exception(msg_error)

def heatmap_geo(df,zoom_start=10,lat=LATITUDE,lon=LONGITUDE):
    '''
    Create a heatmap plot with the geographic information
    
    Arguments:
    ---------
        df: pandas dataframe with the data to show
        zoom_start: number tha determine zoom of 
        lat: name column latitude
        lon: name column longitude
    Returns:
    -------
        map_hooray: map of folium heatmap instance
    '''
    try:
        logging.debug("Creation heatmap")
        POS=df[[lat,lon]].astype(str).applymap(lambda x: str(x.replace(',','.').replace(';',''))).astype(float)
        subdata=POS.dropna()
        map_hooray = folium.Map(location=subdata.median(axis=0),
                            zoom_start = zoom_start)
        hm = plugins.HeatMap(subdata,radius=zoom_start)
        hm.add_to(map_hooray)
        #map_hooray.save(os.path.join("results","mapa.html"))
        plt.close('all')
        return map_hooray
    except:
        msg_error = "Error in creation heatmap"
        logging.error(msg_error)
        raise Exception(msg_error)

def verify_inside_poly(poly,coors):
    '''
    check if a coordinate (long, lat) is inside a polygon
    
    Arguments:
    ---------
        poly: polygon, extracted from the geometry column of a geopandas df
        coors: shape coordinate (longitude, latitude)
    Returns:
    -------
        True / False according to the result
    '''
    # coors=(longitud,latitud)
    try:
        point=Point(coors)
        return point.within(poly)
    except:
        msg_error = "Error in function verify_inside_poly"
        logging.error(msg_error)
        raise Exception(msg_error)


def verify_inside_for_perm(poly,coors):
    '''
    check if a coordinate (long, lat) is inside a polygon through
    permutations of signs and position
    
    Arguments:
    ---------
        poly: polygon, extracted from the geometry column of a geopandas df
        coors: shape coordinate (longitude, latitude)
    Returns:
    -------
        numpy array of (long,lat) what is really inside the polygon
        o np.array([0,0]) if no permutation falls within
    ''' 
    # coors=(longitud,latitud)
    try:
        lx=coors[0]
        ly=coors[1]
        permutaciones=[(ly , lx),(-ly , lx),(-ly, -lx),(ly , -lx),(lx , ly),(-lx , ly),(-lx, -ly),(lx , -ly)]
        results=[verify_inside_poly(poly,i) for i in permutaciones]
        
        if sum(results) > 0:
            return np.array(permutaciones)[results][0] 
        else:
            return np.array([0,0])
    except:
        msg_error = "Error in function verify_inside_for_perm"
        logging.error(msg_error)
        raise Exception(msg_error)

def get_name_poly(df_polys,name_polys,coors):
    '''
    check if a coordinate (long, lat) is inside a set of polygons
    by permutations of the signs and the position and returns the name of the
    polygon if found and None otherwise

    Arguments:
    ---------
        df_polys: geopanda dataframe containing the polygon information
        name_polys: variable of the df_polys dataframe containing the names of the polygons
        coors: shape coordinate (longitude, latitude)
    Returns:
    -------
        polygon name or None according to the result
    ''' 
    try:
        
        for geo,name in zip(df_polys.geometry.values,df_polys[name_polys].values):
            res=verify_inside_for_perm(geo,coors).sum()
            if res != 0:
                return str(name)
            
        return None
    except:
        msg_error = "Error in function get_name_poly"
        logging.error(msg_error)
        raise Exception(msg_error)

def refill_geo(coors,df_polys,name_polys):
    '''
    From a list of coordinates [[long_1, lat_1], ... [long_n, lat_n]] identifies
    the polygon to which each belongs and creates a list with the name of the polygon and
    the correct coordinates.

    Arguments:
    ---------
        coors: list of coordinates of the form [[long_1, lat_1], ... [long_n, lat_n]]
        df_polys: geopanda dataframe containing the polygon information
        name_polys: variable of the df_polys dataframe containing the names of the polygons
    Returns:
    -------
        result: list with the polygon name and the correct coordinates, of the form
        [[name_1,long_1,lat_1],...[name_n,long_n,lat_n]]
    ''' 
    try:
        logging.debug("Creation array refill geo")
        results=[]
        for i in coors:
            poly_name=get_name_poly(df_polys,name_polys,i)
            if poly_name != None:
                poly=df_polys[df_polys[name_polys] == poly_name].geometry.values[0]
                coors_real=verify_inside_for_perm(poly,i)
                results.append([poly_name,*coors_real])
            else:
                results.append([poly_name,0,0])
                
                
        return np.array(results)
    except:
        msg_error = "Error in function refill_geo"
        logging.error(msg_error)
        raise Exception(msg_error)
    
def merge_geoNdata(df_polys,name_polys,df,col_names):
    '''
    From a pandas dataframe with polygon names and values ​​and a geopandas dataframe
    with the geometry data create a merged dataframe with all information
    
    Arguments:
    ---------
        df_polys: geopandas dataframe with polygon information
        name_polys: variable of the df_polys dataframe containing the names of the polygons (must match those of the df)
        df: dataframe with quantitative values ​​of the polygon names
        col_names: column of polygon names
    Returns:
    -------
        df: resuling dataframe of merge both tables
    '''    
    try:
        df=df_polys.merge(df,left_on=name_polys,right_on=col_names)
        return df
    except:
        msg_error = "Error in function merge_geoNdata"
        logging.error(msg_error)
        raise Exception(msg_error)

def map_polygons(df,col_vals,vmin=None,vmax=None,figsize=(10,10)):
    '''
    From a pandas dataframe with polygon names and values ​​create a choroplethic map with
    colors representing values.
    
    Arguments:
    ---------
        df: geopandas dataframe with polygon and values information
        col_vals: column of the values ​​in the polygons
    Returns:
    -------
        fig: figure of matplotlib choroplethic map instance
    '''  
    
    try:
        fig, ax = plt.subplots(figsize=figsize)
        ax.axis('off')
        df.plot(cmap='viridis',column=col_vals,legend=True,ax=ax,vmin=vmin,vmax=vmax) 
        fig.patch.set_facecolor('white')
        plt.close('all')
        return fig
    except:
        msg_error = "Error in function map_polygons"
        logging.error(msg_error)
        raise Exception(msg_error)


def create_grid(df_points,lat=LATITUDE,lon=LONGITUDE,name_polygons=NAME_POLYGON,n_cells=N_CELLS_GRID,crs=CRS_GRID_DATA):
    '''
    From a pandas dataframe with Latitude and Longitude values create a geopandas 
    dataframe with a grid that contains the points
    
    variables:
    df_points: pandas dataframe with columns LATITUDE and LONGITUDE
    lat: name column latitude
    lon: name column longitude
    name_polygons: column name of new polygons
    n_cells: number of cells in x-axis
    crs: Coordinate Reference Systems for points and grid
    return:
    cells: geopandas dataframe with poligons that contains the data
    '''    
    try:
        logging.debug("Creation grid polygons")
        gdf = gpd.GeoDataFrame(df_points, 
            geometry=gpd.points_from_xy(df_points[lon], df_points[lat]),
            crs=crs)
        xmin, ymin, xmax, ymax= gdf.total_bounds
        cell_size = (xmax-xmin)/(n_cells-1)
        grid_cells = []
        for x0 in np.arange(xmin, xmax+cell_size, cell_size ):
            for y0 in np.arange(ymin, ymax+cell_size, cell_size):
                # bounds
                x1 = x0-cell_size
                y1 = y0+cell_size
                grid_cells.append( shapely.geometry.box(x0, y0, x1, y1)  )
        cells = gpd.GeoDataFrame(grid_cells, columns=['geometry'], 
                                        crs=crs).reset_index()
        cells.rename(columns={'index':name_polygons},inplace=True)
        cells[name_polygons]=cells[name_polygons].astype(str)
        # cell.to_file("cells.geojson", driver='GeoJSON')     
        return cells                  
        
    except:
        msg_error = "Error in function create_grid"
        logging.error(msg_error)
        raise Exception(msg_error)
    
      

def map_polygons_html(df,name_polys,col_vals=FREQUENCY,zoom_start=5,crs=CRS_GRID_DATA):
    '''
    From a pandas dataframe with polygon names and values ​​create a choroplethic map with
    colors representing values in a html embebing.
    
    Arguments:
    ---------
        df: geopandas dataframe with polygon and values information
        name_polys: name colomns polygons
        col_vals: column of the values ​​in the polygons
        zoom_start: number tha determine zoom of map
        crs: Coordinate Reference Systems for plot data
    Returns:
    -------
        mymap: figure of folium choroplethic map instance
    variables:
    '''    
    try:
        df=df.to_crs(crs)
        geo = gpd.GeoSeries(df.set_index(name_polys)['geometry']).to_json()
        x_map=df.centroid.x.mean()
        y_map=df.centroid.y.mean()
        mymap = folium.Map(location=[y_map, x_map], zoom_start=zoom_start,tiles=None)
        folium.TileLayer('CartoDB positron',name="Light Map",control=False).add_to(mymap)

        folium.Choropleth(
            geo_data = geo,
            name = 'Choropleth',
            data = df,
            columns = [name_polys,col_vals],
            key_on = 'feature.id',
            fill_color = 'YlGnBu',
            fill_opacity = 0.5,
            line_opacity = 1,
            legend_name = str(col_vals),
            smooth_factor=  0
        ).add_to(mymap)

        style_function = lambda x: {'fillColor': '#ffffff', 
                                    'color':'#000000', 
                                    'fillOpacity': 0.1, 
                                    'weight': 0.1}
        highlight_function = lambda x: {'fillColor': '#000000', 
                                        'color':'#000000', 
                                        'fillOpacity': 0.50, 
                                        'weight': 0.1}
        NIL = folium.features.GeoJson(
            df,
            style_function=style_function, 
            control=False,
            highlight_function=highlight_function, 
            tooltip=folium.features.GeoJsonTooltip(
                fields=[name_polys,col_vals],
                #aliases=['Neighborhood: ','Resident foreign population in %: '],
                style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;") 
            )
        )
        mymap.add_child(NIL)
        mymap.keep_in_front(NIL)
        folium.LayerControl().add_to(mymap)
        return mymap
    except:
        msg_error = "Error in function map_polygons"
        logging.error(msg_error)
        raise Exception(msg_error)