# -*- coding: utf-8 -*-

"""
views.py

:Created: 3/19/14
:Author: timic
"""

import logging
logger = logging.getLogger(__name__)

from functools import wraps
from django.conf import settings
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt

from config import Settings
from _helpers import get_cache


def track_config(fn):

    @wraps(fn)
    def inner(*args, **kwargs):
        if not Settings.configured():
            config_path = getattr(settings, "WSFACTORY_CONFIG_FILE")
            logger.info(
                "Not configured yet. Load configuration %s" % config_path)
            Settings.load(config_path)
        cache = get_cache("wsfactory")
        if Settings.hash() != cache.get(Settings.CACHE_KEY):
            logger.info("Configuration file was changed. Reloading ...")
            Settings.reload()

        return fn(*args, **kwargs)

    return inner


@track_config
def api_list(request):
    """

    TODO: придумать как отдавать доку по сервисам
    """
    raise Http404("Not implemented yet")


@track_config
def handle_api_call(request, service):
    service_handler = Settings.get_service_handler(service)
    if service_handler:
        logger.debug("Hitting service %s" % service)
        return csrf_exempt(service_handler)(request)
    else:
        msg = "Service %s not found" % service
        logger.info(msg)
        raise Http404(msg)

