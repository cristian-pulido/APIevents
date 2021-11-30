from django import db
from django.db import models
from model_utils import Choices
import sys, os
# Create your models here.
sys.path.append(os.path.dirname(os.path.dirname((os.path.dirname(os.path.abspath(__file__))))))

from constantmanager import ID, DATETIME,EVENTS_TYPE,LATITUDE,LONGITUDE,ADITIONAL_TYPES,ADITIONAL_COLUMNS
from constantmanager import NAME_POLYGON, DATE_FORMAT, DATE_HOUR, DATE, TIME, YEAR, MONTH, DAY_WEEK, HOUR_NUMBER
from constantmanager import PARAMETERS_PREDICT, PREDICT_JSON


class Prediction(models.Model):

    parameters=models.JSONField(db_column=PARAMETERS_PREDICT)
    predict_json=models.JSONField(db_column=PREDICT_JSON)
    
class Cleanevent(models.Model):
    # JAN,FEB,MAR,APR,MAY,JUN,JUL,AUG,SEP,OCT,NOV,DEC='JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER'   
    # MONTH_CHOICES = (
    #                     (JAN, "January"),
    #                     (FEB, "February"),
    #                     (MAR, "March"),
    #                     (APR, "April"),
    #                     (MAY, "May"),
    #                     (JUN, "June"),
    #                     (JUL, "July"),
    #                     (AUG, "August"),
    #                     (SEP, "September"),
    #                     (OCT, "October"),
    #                     (NOV, "November"),
    #                     (DEC, "December"),
    #                 )

    
    id_ori=models.PositiveIntegerField(db_column=ID,unique=True)
    date_time=models.DateTimeField(db_column=DATETIME)
    if len(EVENTS_TYPE) > 0:
        event_type=models.CharField(max_length=50,db_column=EVENTS_TYPE)
    latitude=models.FloatField(db_column=LATITUDE)
    longitude=models.FloatField(db_column=LONGITUDE)
    
    name_poly=models.CharField(max_length=50,db_column=NAME_POLYGON,blank=True)            
    date_hour=models.DateTimeField(db_column=DATE_HOUR)
    date=models.DateField(db_column=DATE)
    time=models.TimeField(db_column=TIME, auto_now=False, auto_now_add=False)
    year=models.PositiveIntegerField(db_column=YEAR)
    month = models.CharField(max_length=20,db_column=MONTH)
    day_week = models.CharField(max_length=50,db_column=DAY_WEEK)
    hour_number=models.PositiveIntegerField(db_column=HOUR_NUMBER)
    
    
class Aditionalevent(models.Model):
    
    event = models.ForeignKey("Cleanevent",on_delete=models.CASCADE)
    column_choices = Choices(*(ADITIONAL_COLUMNS+ADITIONAL_TYPES))
    name_column=models.CharField(max_length=50,choices=column_choices)
    values_column = models.CharField(max_length=50,blank=True)    