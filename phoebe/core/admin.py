from django.contrib import admin

from core.models import (
	Zone,
	DeviceGroup,
	Device,
	User,
)

admin.site.register(Zone)
admin.site.register(DeviceGroup)
admin.site.register(Device)
admin.site.register(User)
