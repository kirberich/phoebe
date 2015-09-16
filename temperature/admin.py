from django.contrib import admin

from .models import TemperatureController, Nest

admin.site.register(TemperatureController)
admin.site.register(Nest)
