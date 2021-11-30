import sys, os


sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))

## funciones limpieza y descripcion
from descriptions.utils_description import *
import os
import matplotlib.pyplot as plt
#matplotlib.use('Agg')
from constantmanager import ADITIONAL_TYPES, DATETIME, DATE_FORMAT, ID, EVENTS_TYPE, N_CELLS_GRID, CRS_GRID_DATA, NAME_POLYGON,DATE_HOUR, DATE, TIME, YEAR, MONTH, DAY_WEEK, HOUR_NUMBER
import logging
from folium import plugins


def clean_df(dataframe,ID=ID,datetime=DATETIME,LAT=LATITUDE,LON=LONGITUDE,
             data_polygons=None,n_cells=N_CELLS_GRID,crs_data=CRS_GRID_DATA
            ):
    '''
    From the database and other map files it generates the cleaning procesing of this
    
    Arguments:
    ---------
        dataframe: pandas daframe with the data
        ID: Unique identifier of the events
        datetime: events´s date
        LAT: latitude variable
        LON: longitude variable
        data_polygons: geopandas dataframe with polygon information
        n_cells: number of cells in x-axis for creation grid if data_polygons not given
        crs_data: Coordinate Reference Systems for points and grid
    Returns:
    -------
        log: Information about qualty of data
    '''
    try:
        logging.debug('Start function clean_df')
        log = []
        # Report rows, columns, cells with unknown values, and repeating rows
        log.append("Length: "+str(dataframe.shape))
        log.append("Size: "+str(dataframe.size))
        log.append("Percentage of empty cells: "+str(dataframe.isna().mean().mean()*100)+'%')
        log.append("Percentage cells with value'-': "+str((dataframe == "-").mean().mean()*100)+'%')
        log.append("Duplicated rows "+str(dataframe.duplicated().sum()))
        dataframe.replace("-",np.NaN,inplace=True)
        #Eliminacion de duplicados
        dataframe.drop_duplicates(inplace=True)
        log.append("Events after drop duplicates: "+str(len(dataframe)))


        ## The variable 'ID' is taken as the unique identifier of the events and the total number of events found is updated
        data=dataframe.drop_duplicates(subset=ID).reset_index(drop=True)
        log.append("Unique Events Found: "+str(len(data)))
        logging.debug('Phase quality data')
    except:
        msg_error = "Error in Phase quality data function clean_df"
        logging.error(msg_error)
        raise Exception(msg_error)


    try:
        ## space formatting and related variable addition
        if not isinstance(data_polygons,gpd.geodataframe.GeoDataFrame):
            data_polygons = create_grid(data[[LON,LAT]],n_cells=n_cells,crs=crs_data)
        real_polys=refill_geo(data[[LON,LAT]].values,data_polygons,NAME_POLYGON)
        data[[NAME_POLYGON,LON,LAT]] = real_polys

        log.append("Records not found in geometry given: "+str(data[NAME_POLYGON].isna().sum()))
        data.dropna(subset=[NAME_POLYGON],inplace=True)
        log.append("Events after drop records not found: "+str(len(dataframe)))
        data[NAME_POLYGON]=data[NAME_POLYGON].astype(str)
        data_polygons=data_polygons[data_polygons[NAME_POLYGON].isin(data[NAME_POLYGON].unique())]

        logging.debug('Phase format space')
    except:
        msg_error = "Error in Phase format space clean_df"
        logging.error(msg_error)
        raise Exception(msg_error)
    
    try:
        ## Time variable formatting and related variable addition
        data[DATE_HOUR]=pd.to_datetime(data[datetime],format=DATE_FORMAT,errors='coerce')
        log.append("Records with out date or hour: "+str(data[DATE_HOUR].isna().sum()))
        # Deletion of records without date and time
        data=data.dropna(subset=[DATE_HOUR])
        log.append("Resulting records: "+str(len(data)))
        data[DATE] =data[DATE_HOUR].dt.date
        data[TIME]=data[DATE_HOUR].dt.time
        data[DAY_WEEK]=data[DATE_HOUR].dt.day_name()
        data[MONTH]=data[DATE_HOUR].dt.month_name()
        data[HOUR_NUMBER]=data[DATE_HOUR].dt.hour
        data[YEAR]=data[DATE_HOUR].dt.year
        # Fecha Inicio y fin de los datos
        log.append("Start: "+str(data[DATE_HOUR].min()))
        log.append("End: "+str(data[DATE_HOUR].max()))
        # Semanas en total
        weeks_between=int((data[DATE_HOUR].max()-data[DATE_HOUR].min()).days/7)
        log.append("Total weeks: "+str(weeks_between))
        logging.debug('Phase format date and hour')
        
        return data, data_polygons, log
    except:
        msg_error = "Error in Phase format date and hour function clean_df"
        logging.error(msg_error)
        raise Exception(msg_error)


def descriptive_process(data,data_polygons,event_types=EVENTS_TYPE,
                        aditional_types=ADITIONAL_TYPES
                        ):
    '''
    From the clean database and other map files it generates the descriptive analysis
    
    Arguments:
    ---------
        data: pandas daframe with the data
        data_polygons: geopandas dataframe with polygon information
        event_type: name of column with event types
        aditional_types: list of colums names with event types
    Returns:
    -------
        figures: Dict of resulting univariate figures that can be instances of
                 matplotlib, seaborn, plotly or folium figures
        tables: Dict of resulting univariate tables in pandas dataframes
        figures_BI: Dict of resulting bivariate figures that can be instances of
                    matplotlib, seaborn, plotly or folium figures
        tables_BI: Dict of resulting univariate tables in pandas dataframes
    '''
    try:
        figures={}
        tables={}
        logging.debug('Start phase univariate description')
        ## Temporal behavior graph
        fecha_data = create_Subdata(data,[DATE]).sort_values(DATE)
        tables["date_events"]=fecha_data
        figures["date_events"]=line_figure(fecha_data,variable=DATE,min_values=1,max_values=2)

        anio=create_Subdata(data,[YEAR]).reset_index(drop=True)
        tables["year_bar"]=anio
        figures["year_bar"]=bar_figure_top_values(anio.astype(str),YEAR)

        semana=create_Subdata(data,[DAY_WEEK])
        semana[PERCENTAGE]=semana[FREQUENCY]/semana[FREQUENCY].sum()*100
        weeks_between=int((data[DATE_HOUR].max()-data[DATE_HOUR].min()).days/7)
        values_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday","Sunday"]
        media_factor = weeks_between
        tables["day_bar"]=semana
        figures["day_bar"]=bar_figure_probabilities(semana,'Day_week',values_order,media_factor)

    
        subdata = create_Subdata(data,[HOUR_NUMBER]).sort_values(HOUR_NUMBER)
        subdata[PERCENTAGE]=semana[FREQUENCY]/semana[FREQUENCY].sum()*100
        tables["hour_line"]=subdata
        figures["hour_line"]=line_figure(subdata,variable=HOUR_NUMBER,min_values=1,max_values=1)

        ## Porcentaje de eventos encontrados en los meses del año  

        years_to_compare=[]
        for i in data[YEAR].unique():
            min_day=data[data[YEAR] == i][DATE_HOUR].min().timetuple().tm_yday
            max_day=data[data[YEAR] == i][DATE_HOUR].max().timetuple().tm_yday
            if max_day-min_day > 360:
                years_to_compare.append(i)
                
        

        if len(data[YEAR].unique()) == 1:
            years_to_compare=data[YEAR].unique()
            
        if len(years_to_compare) != 0:

            subdata = create_Subdata(data[data.Year.isin(years_to_compare)],[MONTH])
            subdata[PERCENTAGE]=semana[FREQUENCY]/semana[FREQUENCY].sum()*100
            tables["bar_month"]=subdata

            values_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
            media_factor = len(years_to_compare)
            figures["bar_month"]=bar_figure_probabilities(subdata,MONTH,values_order,media_factor)

        #Mapa de calor basado en la frecuencia y distancia de la georeferenciación de los registros
        figures["heatmap"]=heatmap_geo(data)
        #map_hooray.save(os.path.join("results","mapa.html"))

        
        subdata=create_Subdata(data,[NAME_POLYGON])
        figures["Choroplethmap"]=map_polygons_html(merge_geoNdata(data_polygons,NAME_POLYGON,subdata,NAME_POLYGON),NAME_POLYGON,col_vals=FREQUENCY,zoom_start=5,crs=CRS_GRID_DATA)

        if not ((event_types == None) or (len(event_types) == 0)) :
            subdata = create_Subdata(data,[event_types])
            subdata[PERCENTAGE]=semana[FREQUENCY]/semana[FREQUENCY].sum()*100
            tables["bar_event_type"]=subdata
            figures["bar_event_type"]=bar_figure_top_values(subdata,event_types)


        for idx,event_type in enumerate(aditional_types):

            subdata = create_Subdata(data,[event_type])
            subdata[PERCENTAGE]=semana[FREQUENCY]/semana[FREQUENCY].sum()*100
            tables["bar_aditional_type_"+str(idx)]=subdata
            figures["bar_aditional_type_"+str(idx)]=bar_figure_top_values(subdata,event_type)

        

    except Exception as e:
        msg_error = "Error in Phase univariate description function descriptive_process"
        logging.error(msg_error)
        raise Exception(msg_error + " / "+ str(e))

    # Análisis Bivariado
    try:
        logging.debug('Start phase bivariate description')
        figures_BI={}
        tables_BI={}

        if not ((event_types == None) or (len(event_types) == 0)) :
            for k in [event_types]+aditional_types:
                for i in [YEAR,MONTH,HOUR_NUMBER,DAY_WEEK]:
                    values_order=[]
                    subdata=create_Subdata(data,[k,i])
                    if (i == YEAR) or (i == HOUR_NUMBER):
                        values_order=sorted(subdata[i].unique())
                        values_order=[str(i) for i in values_order]
                        subdata[i]=subdata[i].astype(str)
                    if i == DAY_WEEK:
                        values_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday","Sunday"]
                    if i == MONTH:
                        values_order = ['January','February','March','April','May','June','July','August','September','October','November','December']

                    figures_BI["bubble_eventtypes_"+i]=bubbles_figure_probabilities(subdata,k,i,var2_order=values_order)
                    M=get_probabilities_matrices(subdata,k,i,var2_order=values_order)
                    for j,type in zip(M,['join','column','row']):
                        tables_BI[type+'_'+k+'_'+i]=j
                        figures_BI[type+'_'+k+'_'+i]=heatmap_figure_probabilities(j,type)



        for i in [event_types]+aditional_types + [YEAR,MONTH,HOUR_NUMBER,DAY_WEEK] :
            if (i == None) or (len(i) == 0) :
                continue
            values_order=[]
            subdata=create_Subdata(data,[NAME_POLYGON,i])
            if (i == YEAR) or (i == HOUR_NUMBER):
                    values_order=sorted(subdata[i].unique())
                    values_order=[str(i) for i in values_order]
                    subdata[i]=subdata[i].astype(str)
            if i == DAY_WEEK:
                values_order = ["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday","Sunday"]
            if i == MONTH:
                values_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
            M=get_probabilities_matrices(subdata,NAME_POLYGON,i,var2_order=values_order)
            for j,type in zip(M,['join','column','row']):
                tables_BI[type+'_'+NAME_POLYGON+'_'+i]=j
                figures_BI[type+'_'+NAME_POLYGON+'_'+i]=heatmap_figure_probabilities(j,type)

        subdata=create_Subdata(data,[HOUR_NUMBER,DAY_WEEK])
        subdata.sort_values(HOUR_NUMBER,inplace=True)

    
        values_order_days=["Monday", "Tuesday", "Wednesday", "Thursday","Friday","Saturday","Sunday"]
        fig = px.line(subdata, x=HOUR_NUMBER, y=FREQUENCY, facet_row=DAY_WEEK, color=DAY_WEEK,
                      width=800, height=1400,  color_discrete_sequence = px.colors.qualitative.Prism[1:],
                      category_orders={DAY_WEEK: values_order_days},
                      labels={DAY_WEEK:"Day"})
        fig.update_layout(title_text="",
                         showlegend=False)
        plt.close('all')
        figures_BI["day_hour"]=fig
        values_order=sorted(subdata[HOUR_NUMBER].unique())
        values_order=[str(i) for i in values_order]
        subdata[HOUR_NUMBER]=subdata[HOUR_NUMBER].astype(str)
        M=get_probabilities_matrices(subdata,HOUR_NUMBER,DAY_WEEK,values_order,values_order_days)
        for j,type in zip(M,['join','column','row']):
            tables_BI[type+'_'+"hour_day"]=j
            figures_BI[type+'_'+"hour_day"]=heatmap_figure_probabilities(j,type)

    except Exception as e:
        msg_error = "Error in phase bivariate description function descriptive_process"
        logging.error(msg_error)
        raise Exception(msg_error + " / "+ str(e))

    return figures,tables,figures_BI,tables_BI
