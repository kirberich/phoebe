from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^api/slack/$', 'core.slack.send', name='send_slack_message'),
]
