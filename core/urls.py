from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'core.views.main', name='main'),

    url(r'^api/user/(?P<user_id>.*)/presence/$', 'core.views.api_presence', name='api_presence'),
]
