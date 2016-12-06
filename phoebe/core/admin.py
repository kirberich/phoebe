from django.contrib import admin

from core.models import (
	Zone,
	DeviceGroup,
	Device,
)

admin.site.register(Zone)
admin.site.register(DeviceGroup)
admin.site.register(Device)
