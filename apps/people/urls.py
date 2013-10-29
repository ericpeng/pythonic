#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from django.conf.urls import patterns

urlpatterns = patterns('people.views',
    (r'^(\d{1,10})/$','home'),
)