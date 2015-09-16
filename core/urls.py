from django.conf.urls import url


urlpatterns = [
    url(r'^$', 'core.views.home', name='home'),
    url(r'^api/presence/check/$', 'core.presence.check_user_presence', name='check_presence')
]
