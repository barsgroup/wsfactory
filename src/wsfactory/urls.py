# coding: utf-8
from __future__ import absolute_import

from django.conf.urls import url

from .config import get_url_patterns
from .views import api_list
from .views import handle_api_call


urlpatterns = [
    url(r'^wsfactory/api$', api_list),
    url(r'^wsfactory/api/(?P<service>[\w\-]+)(/\w*)?$', handle_api_call),
] + get_url_patterns()
