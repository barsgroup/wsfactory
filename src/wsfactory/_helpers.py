# -*- coding: utf-8 -*-

"""
factory.py

:Created: 3/13/14
:Author: timic
"""
import os
from threading import RLock
from functools import wraps
from importlib import import_module
from StringIO import StringIO
from lxml import etree, objectify

from spyne.service import ServiceBase


def load(path):
    mod, obj = path.rsplit('.', 1)
    mod = import_module(mod)
    return getattr(mod, obj)


def lock(fn):
    _lock = RLock()

    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            _lock.acquire()
            result = fn(*args, **kwargs)
        finally:
            _lock.release()
        return result

    return wrapper


def load_xml(xml_path):
    """
    Загружает xml в etree.ElementTree
    """
    if os.path.exists(xml_path):
        xml_io = open(xml_path, 'rb')
    else:
        raise ValueError(xml_path)
    xml = objectify.parse(xml_io)
    xml_io.close()
    return xml


def load_schema(schema_path):
    """
    Загружает схему xsd
    """
    if schema_path.startswith('http://') or schema_path.startswith('https://'):
        import requests
        response = requests.get(schema_path)
        schema_io = StringIO(response.text)
    elif os.path.exists(schema_path):
        schema_io = open(schema_path, 'rb')
    else:
        raise ValueError(schema_path)
    schema = etree.XMLSchema(file=schema_io)
    schema_io.close()
    return schema


def create_application(
        app_cls, wsgi_cls, name, tns, service, in_protocol, out_protocol):

    app = app_cls(
        [service], tns,
        name=name,
        in_protocol=in_protocol,
        out_protocol=out_protocol)
    wsgi_app = wsgi_cls(app)

    return wsgi_app


def create_service(service_name, api_list):

    bases = (ServiceBase,)
    api_dict = dict(api_list)
    return type(str(service_name), bases, api_dict)


def get_cache(backend):
    from django.core.cache import (
        get_cache as django_get_cache, InvalidCacheBackendError)
    try:
        cache = django_get_cache(backend)
    except InvalidCacheBackendError:
        cache = django_get_cache('default')
    return cache