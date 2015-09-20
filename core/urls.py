from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'core.views.home', name='home'),
]
