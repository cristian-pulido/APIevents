from django.contrib import admin
from predictions.models import Prediction, Cleanevent, Aditionalevent
# Register your models here.

admin.site.register(Prediction)
admin.site.register(Cleanevent)
admin.site.register(Aditionalevent)
