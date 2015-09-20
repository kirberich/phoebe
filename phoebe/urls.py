from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^power/', include('power.urls')),
    url(r'^', include('core.urls')),
    url(r'^admin/', include(admin.site.urls)),
]
