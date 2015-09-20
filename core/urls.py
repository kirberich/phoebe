from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'core.views.main', name='main'),

    url(r'^api/presence/(?P<user_id>.*)/$', 'core.views.api_presence', name='api_presence'),
]
