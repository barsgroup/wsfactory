# -*- coding: utf-8 -*-

"""
config.py

:Created: 5/12/14
:Author: timic
"""
import logging
logger = logging.getLogger(__name__)

import hashlib
import os

from lxml import etree

import _helpers


VALUE_TYPES = {
    "unicode": unicode,
    "int": int,
    "bool": lambda x: x in ("True", "true", True)
}


def parse_params(params):
    return dict((
        param.attrib["key"],
        VALUE_TYPES.get(param.attrib["valueType"])(param.text)
    ) for param in params)


class ImproperlyConfigured(Exception):
    pass


class Settings(object):

    __instance = None

    NAMESPACE = "http://bars-open.ru/schema/wsfactory"
    DEFAULT_TNS = "http://bars-open.ru/inf"
    CACHE_KEY = "wsfactory_config_file_hash"
    SCHEMA = _helpers.load_schema(os.path.join(os.path.dirname(
        __file__), "schema", "wsfactory.xsd"))

    def __new__(cls, *more):
        if not cls.__instance:
            obj = cls.__instance = super(Settings, cls).__new__(cls, *more)

            obj._app_cache = {}
            obj._configured = False
            obj._config_path = None
            obj._hash = None
            obj._api_handler = None
            obj._app_cls = None
            obj._django_cls = None
            obj._document = None

        return cls.__instance

    @classmethod
    def reload(cls):
        if not cls.configured():
            raise ImproperlyConfigured(
                "Not configured yet!")
        config_path = cls.config_path()
        cls.__instance = None
        cls.load(config_path)

    @classmethod
    def validate(cls, xml):
        schema = _helpers.load_schema(os.path.join(os.path.dirname(
            __file__), "schema", "wsfactory.xsd"))
        if not schema.validate(etree.fromstring(etree.tostring(xml))):
            raise ImproperlyConfigured(
                "Config file didn't pass schema validation: %s\n"
                % "\n".join(err.message for err in schema.error_log))

    @classmethod
    def load(cls, config_path):
        logger.debug("Load configuration file %s" % config_path)
        cls.__instance = None
        config = cls()
        config._config_path = config_path

        # Читаем настройки

        if not os.path.exists(config_path):
            raise ImproperlyConfigured(
                "Configuration file `%s` does not exist!" % config_path)

        document_tree = _helpers.load_xml(config_path)
        cls.validate(document_tree)

        config._document = document_tree.getroot()

        # Посчитаем хеш-сумму файла конфигурации, и запишем её в кэш django
        with open(config_path, "rb") as fd:
            config._hash = hashlib.md5(fd.read()).hexdigest()

        cache = _helpers.get_cache("wsfactory")
        cache.set(cls.CACHE_KEY, config._hash)
        config._configured = True

        logger.debug(
            "Configuration file %s successfully loaded" % config_path)

    @classmethod
    def dump(cls, config_path):
        if not cls.configured():
            raise ImproperlyConfigured("Configuration does not loaded yet")
        self = cls()
        cls.validate(self._document)

        logger.debug("Dump configutation file %s" % config_path)
        if not os.access(os.path.exists(
            config_path) and config_path or os.path.dirname(
                config_path), os.W_OK):
            raise ImproperlyConfigured("Permission denied `%s`" % config_path)
        # Записываем результат в файл
        with open(config_path, "w") as fd:
            fd.write(etree.tostring(
                self._document, pretty_print=True, encoding="utf8"))

        logger.debug(
            "Configuration file %s successfully dumped" % config_path)

    def _create_protocol(self, code, params, security=None):
        proto_el = self._document.Protocols.find('*[@code="{0}"]'.format(code))
        proto_params = parse_params(proto_el.getchildren())
        proto_params.update(params)
        if security:
            security_el = self._document.SecurityProfile.find(
                '*[@code="{0}"'.format(security))
            security_params = parse_params(security_el.getchildren())
            security_cls = _helpers.load(
                self._document.SecurityProfile.Modules.find(
                    '*[@code="{0}"'.format(security_el["module"])))
            proto_params["wsse_security"] = security_cls(**security_params)
        proto_cls = _helpers.load(proto_el["module"])
        return proto_cls(**proto_params)

    def _create_app(self, app_name):
        app_el = self._document.Applications.find(
            '*[@service="{0}"]'.format(app_name))
        service_name = app_el["service"]
        service_el = self._document.Services.find(
            '*[@code="{0}"]'.format(service_name))
        api = map(
            lambda api_code: (api_code, _helpers.load(
                self._document.ApiRegistry.find(
                    '*[@code="{0}"]'.format(api_code)))),
            service_el.xpath["*/@code"])
        service = _helpers.create_service(service_name, api)

        in_protocol, out_protocol = self._create_app_protocols(app_el)

        app = _helpers.create_application(
            self._get_app_cls(),
            self._get_django_cls(),
            app_name, app_el.get("tns", self.DEFAULT_TNS),
            service, in_protocol, out_protocol)
        self._app_cache[app_name] = app
        return app

    def _create_app_protocols(self, app_el):

        in_proto_params = dict(app_el.InProtocol.iteritems())
        in_proto_params["params"] = parse_params(
            app_el.InProtocol.getchildren())
        out_proto_params = dict(app_el.OutProtocol.iteritems())
        out_proto_params["params"] = parse_params(
            app_el.OutProtocol.getchildren())

        return (
            self._create_protocol(**in_proto_params),
            self._create_protocol(**out_proto_params))
    
    def _get_app_cls(self):
        if self._app_cls:
            return self._app_cls

        app_cls_path = self._document.System.xpath(
            '*[@key="Application"]/text()')

        from spyne.application import Application
        if app_cls_path:
            self._app_cls = _helpers.load(app_cls_path[0])
            if not issubclass(self._app_cls, Application):
                raise ImproperlyConfigured(
                    "{0} is not subclass of spyne Application".format(
                        self._app_cls.__name__))
        else:
            self._app_cls = Application
        return self._app_cls

    def _get_django_cls(self):
        if self._django_cls:
            return self._django_cls

        django_cls_path = self._document.System.xpath(
            '*[@key="DjangoApplication"]/text()')

        from spyne.server.django import DjangoApplication
        if django_cls_path:
            self._django_cls = _helpers.load(django_cls_path[0])
            if not issubclass(self._django_cls, DjangoApplication):
                raise ImproperlyConfigured(
                    "{0} is not subclass of spyne DjangoApplication".format(
                        self._django_cls.__name__))
        else:
            self._app_cls = DjangoApplication
        return self._app_cls

    @classmethod
    def get_service_handler(cls, service_name):
        self = cls()
        if not service_name in self._applications.iterkeys():
            return None
        return self._app_cache.setdefault(
            service_name, self._create_app(service_name))

    @classmethod
    def configured(cls):
        self = cls()
        return self._configured

    @classmethod
    def config_path(cls):
        return cls()._config_path

    @classmethod
    def hash(cls):
        self = cls()
        return self._hash

    @classmethod
    def get_api_handler(cls):
        self = cls()
        api_handler_module = getattr(self, "ApiHandler", None)
        if api_handler_module:
            self._api_handler = _helpers.load(api_handler_module)
        return self._api_handler

    @classmethod
    def get_element_root(cls, registry):
        self = cls()
        self._document.find(".//{{{0}}}{1}".format(
            Settings.NAMESPACE, registry))