from django.conf.urls import url


urlpatterns = [
    url(r'^api/user/(?P<user_id>\d+)/toggle_switch/(?P<switch_id>\d+)/$', 'power.views.toggle_switch', name='api_toggle_switch'),
]