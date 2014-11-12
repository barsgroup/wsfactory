# -*- coding: utf-8 -*-

"""
urls.py

:Created: 3/19/14
:Author: timic
"""
from django.conf.urls import patterns, url

from wsfactory.config import get_url_patterns

urlpatterns = patterns(
    'wsfactory.views',
    url(r'^wsfactory/api$', 'api_list'),
    url(r'^wsfactory/api/(?P<service>[\w\-]+)(/\w*)?$', 'handle_api_call'),
    *get_url_patterns()
)