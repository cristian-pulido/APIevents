
from rest_framework import serializers
from .models import Cleanevent, Prediction
from collections import OrderedDict
from api.utils_api import names_to_representation

class PredictionSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Prediction
        fields = ('id', 'parameters', 'predict_json')


    def to_representation(self, obj):
        # call the parent method and get an OrderedDict
        data = super(PredictionSerializer, self).to_representation(obj)
        # generate a list of the keys and replace the key 'class_name'
        keys = list(data.keys())
        real_names=names_to_representation(Prediction)
        for i in real_names:
            keys.insert(keys.index(i[0]), i[1])
            keys.remove(i[0])
            # remove 'class_name' and assign its value to a new key 'class'
            class_name = data.pop(i[0])
            data.update({i[1]: class_name})
            # create new OrderedDict with the order given by the keys
        response = OrderedDict((k, data[k]) for k in keys)
        return response
    
    
class EventsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Cleanevent
        fields = tuple((f.name for f in Cleanevent._meta.get_fields()))[2:]


    def to_representation(self, obj):
        # call the parent method and get an OrderedDict
        data = super(EventsSerializer, self).to_representation(obj)
        # generate a list of the keys and replace the key 'class_name'
        keys = list(data.keys())
        real_names=names_to_representation(Cleanevent)
        for i in real_names:
            keys.insert(keys.index(i[0]), i[1])
            keys.remove(i[0])
            # remove 'class_name' and assign its value to a new key 'class'
            class_name = data.pop(i[0])
            data.update({i[1]: class_name})
            # create new OrderedDict with the order given by the keys
        aditionals=obj.aditionalevent_set.all()
        for i in aditionals:
            keys.append(i.name_column)
            data.update({i.name_column:i.values_column})
        response = OrderedDict((k, data[k]) for k in keys)
        return response