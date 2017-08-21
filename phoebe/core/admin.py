from django import forms
from django.contrib import admin

from core.models import (
    Zone,
    DeviceGroup,
    Device,
    User,
    Plugin,
)
from core.plugins import get_plugins


class PluginForm(forms.ModelForm):
    class Meta:
        model = Plugin
        fields = ('plugin_type', 'name', 'is_active')
        widgets = {
            'plugin_type': forms.Select()
        }


class PluginAdmin(admin.ModelAdmin):
    form = PluginForm
    list_display = ('name', 'is_active')

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name == "plugin_type":
            plugins = get_plugins()
            kwargs['widget'].choices = [
                (plugin.name, plugin.friendly_name) for plugin in plugins
            ]
        return super().formfield_for_dbfield(db_field, request, **kwargs)


admin.site.register(Zone)
admin.site.register(DeviceGroup)
admin.site.register(Device)
admin.site.register(User)
admin.site.register(Plugin, PluginAdmin)
