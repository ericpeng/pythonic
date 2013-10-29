#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.conf.urls import patterns
from django.contrib import admin

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('topic.views',
    (r'^(?P<node_id2>\d+)/create/$','create_topic'),
    (r'^(?P<node_id>\d+)/$','node'),
    (r'^(?P<topic_id>\d+)/$','topic'),
)