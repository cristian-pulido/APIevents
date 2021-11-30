import sys, os


sys.path.append(os.path.dirname((os.path.dirname(os.path.abspath(__file__)))))
from prediction.utils_prediction import getOpenCPData

import geopandas as gpd
import open_cp
import open_cp.naive as baseline
from open_cp import geometry

class PredictionModel:
    '''
    Class to define the prediction models to use
    
    Attributes
    ----------
    nameModel: str
        The name of the model used
    dfTrainData: pandas.DataFrame
        The data to use in the training of the model
    wX: int
        size in meters of the longitude in an analysis block
    wY: int
        size in meters of the longitude in an analysis block
    training_data: open_cp.points
        the training data after the Open CP formating
    regionWork:
        the region to use in the prediction
    grid: open_cp.grid
        the spatial grid after the Open CP formating
    region: open_cp.RectangularRegion
        rectangular region which includes the geo 
    dataFilters: dict
        dictionary of filters used to get the data
    '''
    def __init__(self, nameModel, dfTrain, regionWork, grid, wX, wY):
        self.dfTrainData = dfTrain
        self.wX = wX
        self.wY = wY
        self.nameModel = nameModel
        self.grid = grid
        self.region = regionWork
        self.training_data = None
       

    def predict(self, minDate, maxDate):
        ''' Predict the values using the instantiated model
        
        Parameters
        ----------
        minDate: datetime
            Minimum Date used to get the prediction
        maxDate: datetime
            Maximum Date used to get the prediction
        '''
        raise NotImplementedError("The method not implemented")
    
    
    def getTrainingData(self):
        '''
        Returns
        -------
        train_data:
            the train data in Open CP format
        '''
        return self.training_data
    
    
    def getName(self):
        '''
        Returns
        -------
        nameModel: str
            the name of the model
            
        '''
        return self.nameModel
    
    
    def getRegion(self):
        '''
        Returns
        -------
        region: 
            the region to run the prediction model
            
        '''
        return self.region

    
    def getGrid(self):
        '''
        Returns
        -------
        grid: 
            the projected grid to run the prediction model
            
        '''
        return self.grid
    
    def getValidTrain(self):
        '''
        Returns
        -------
        ValidTrain: boolean 
            Indicates if is a valid trained model
            
        '''
        return self.validTrain
    
    
# - -- --- ----- ------- ----------- ------------- ----------------- -------------------
    
    def getDataPerShift(self, shift):
        '''
        Get the data in the specific day of the week and/or day shift
        
        Parameters
        ----------
        shift: int
            a number indicating the turn of the day
        
        Returns
        -------
        dfTrainDataFiltered: pandas.DataFrame
            the dataframe corresponding with the indicated shift
        '''
        if shift != -1:
            dfTrainDataFiltered = self.dfTrainData
            dfTrainDataFiltered = dfTrainDataFiltered[dfTrainDataFiltered['turno_id_dia']==shift]
        return dfTrainDataFiltered
    
    def getDataPerDay(self, dayWeek):
        '''
        Get the data in the specific day of the week and/or day shift
        
        Parameters
        ----------
        dayWeek: int 
            a number between [0, 6] correponding with the day of the week starting in monday
        
        Returns
        -------
        dfTrainDataFiltered: pandas.DataFrame
            the dataframe corresponding with the indicated day
        
        Raise
        -----
        ValueError if the day is incorrect
        '''
        if dayWeek >= 0 and dayWeek <= 6 :
            dfTrainDataFiltered = self.dfTrainData
            dfTrainDataFiltered = dfTrainDataFiltered[dfTrainDataFiltered['dia_semana']==dayWeek]
        else:
            raise ValueError("The day is not in the range")
            
        return dfTrainDataFiltered
    
    def getDataByConditions(self, filters):
        '''
        Get the data which fulfill the given conditions
        
        Parameters
        ----------
        conditiond: dict
            dictionary with the key and the values to filter in the column named as the key
            ej. {'turno_id_dia': [0, 2], 'dia_semana': 4
            
        Returns
        -------
        dfTrainDataFiltered: pandas.DataFrame
            the dataframe corresponding with the indicated conditions
        '''
        if not len(filters) > 0 :
            raise ValueError("Dictionary empty, the dictionary must have at least one pair(key:value)")
            
        columns = self.dfTrainData
        keys = list(filters.keys())
        for k in keys:
            if k not in columns:
                raise ValueError("the key",k," is not a column in the dataframe")
        
        dfTrainDataFiltered = self.dfTrainData
        for key, values in filters.items():
            for val in values: 
                dfTrainDataFiltered = dfTrainDataFiltered[dfTrainDataFiltered[key]==val]
            
        return dfTrainDataFiltered
        
# - -- --- ----- -------
# - -- --- ----- ------- ----------- ------------- ----------------- -------------------

class Counter(PredictionModel):
    '''
    Class to predict values using a counter model considering all data
    '''
    def __init__(self, nameModel, dfTrain, regionWork, grid, wX, wY):
        ''' Creates a new instance of the Counter predictor
        
        Raises
        ------
        ValueError: Exception
            If the given dataframe with the training data does not have enough records
        '''
        PredictionModel.__init__(self, nameModel, dfTrain, regionWork, grid, wX, wY)
        if self.dfTrainData.shape[0] <= 1 :
            raise ValueError("Not enough records in the train data for Counter")

        training_data = getOpenCPData( self.dfTrainData )
        self.training_data = training_data 
        
        
    def predict(self, minDate, maxDate):
        # Construye un predictor basado en conteo
        countingGridPredictor = baseline.CountingGridKernel(self.wX, self.wY, region = self.region)
        # Fija todos los datos para el conteo
        countingGridPredictor.data = self.training_data
        return countingGridPredictor.predict()
    