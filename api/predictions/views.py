from django.shortcuts import render
from collections import OrderedDict
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from predictions.models import Prediction, Cleanevent
from predictions.serializers import PredictionSerializer, EventsSerializer
from api.utils_api import names_to_representation, testpredict

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


@csrf_exempt
def events_list(request):
    """
    List all code serie, or create a new serie.
    """
    if request.method == 'GET':
        events = Cleanevent.objects.all()
        serializer = EventsSerializer(events, many=True)
        return JSONResponse(serializer.data)
    else:
        return JSONResponse(status=400)



        
@csrf_exempt
def prediction_list(request):
    """
    List all code serie, or create a new serie.
    """
    if request.method == 'GET':
        predictions = Prediction.objects.all()
        serializer = PredictionSerializer(predictions, many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            A=PredictionSerializer()
            keys = list(data.keys())
            real_names=A.names_to_representation()
            for i in real_names:
                keys.insert(keys.index(i[1]), i[0])
                keys.remove(i[1])
                # remove 'class_name' and assign its value to a new key 'class'
                class_name = data.pop(i[1])
                data.update({i[0]: class_name})
                # create new OrderedDict with the order given by the 
            serializer = PredictionSerializer(data=data)
        except:
            data = JSONParser().parse(request)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        return JSONResponse(serializer.errors, status=400)

@csrf_exempt
def Prediction_detail(request, query):
    """
    Retrieve, update or delete a serie.
    """
    try:
        parameters=query.split("-")
        dict_params={}
        dict_params_to_get={}
        for i in parameters:
            split=i.split(":")
            dict_params[split[0]]=split[1]
            dict_params_to_get["parameters__"+split[0]]=split[1]
        try:
            prediction = Prediction.objects.filter(**dict_params_to_get)
        except:
            prediction=testpredict(dict_params)
            
        
    except Prediction.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = PredictionSerializer(prediction,many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        # data = JSONParser().parse(request)
        # serializer = PredictionSerializer(serie, data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return JSONResponse(serializer.data)
        #return JSONResponse(serializer.errors, status=400)
        return HttpResponse(status=400)

    elif request.method == 'DELETE':
        #serie.delete()
        #return HttpResponse(status=204)
        return HttpResponse(status=400)
    
@csrf_exempt
def Events_detail(request, query):
    """
    Retrieve, update or delete a serie.
    """
    try:
        map_columns=names_to_representation(Cleanevent)
        map_columns={i[1]:i[0] for i in map_columns}       
        parameters=query.split("-")
        dict_params={}
        for i in parameters:
            split=i.split(":")
            dict_params[map_columns[split[0]]]=split[1]
        events = Cleanevent.objects.filter(**dict_params)
        
    except Cleanevent.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = EventsSerializer(events,many=True)
        return JSONResponse(serializer.data)

    elif request.method == 'PUT':
        # data = JSONParser().parse(request)
        # serializer = PredictionSerializer(serie, data=data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return JSONResponse(serializer.data)
        #return JSONResponse(serializer.errors, status=400)
        return HttpResponse(status=400)

    elif request.method == 'DELETE':
        #serie.delete()
        #return HttpResponse(status=204)
        return HttpResponse(status=400)
