from django.conf.urls import url
from django.urls import path
from predictions import views


urlpatterns = [
    path('predictions/', views.prediction_list),
    path('events/', views.events_list),
    path('predictions/<str:query>/', views.Prediction_detail),
    path('events/<str:query>/', views.Events_detail),
]
