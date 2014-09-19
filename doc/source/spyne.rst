Spyne
=====

Как обычно, пишутся веб-сервисы на spyne?

Мы создаем сервис, наследуясь от класса ServiceBase, и реализуем в нём методы нашего api.
Потом нужные нам методы заворачиваем в декораторы ``rpc`` или ``srpc``:


.. code-block:: python

    class Service(ServiceBase):

        @srpc(_returns=Datetime):
        def GetNow():
            return datetime.datetime.now()

        @srpc(Unicode, _returns=Unicode)
        def Echo(string):
            return string


Потом созданный сервис связывается с протоколами через ``Application``, который
далее передается в wsgi-приложение:


.. code-block:: python

    app = Application(
        [Service], "tns", "name",
        in_protocol=HttpRpc(),
        out_protocol=JsonDocument())

    wsgi_app = DjangoApplication(app)


Разберем, что тут означает каждая переменную:

* ``class Service`` - spyne-сервис, набор api-методов. Для удобства далее
  будем называть их просто сервисами или "услуга"

* ``def GetNow`` - метод сервиса, или api-метод

* ``app`` - spyne-приложение, это некий клей, который связывает между собой,
  сервисы и протоколы

* ``wsgi_app`` - wsgi-приложение, непосредственно обработчик запросов

Связку wsgi-приложения и spyne-приложения, для простоты, будет называть - "веб-сервис".


Используя wsfactory, вам необходимо только описать каждый api-метод отдельно
главное, чтобы их можно было импортировать через ``importlib.import_module``.:

.. code-block:: python

    # где-то в проекте, например в project/api.py

    @srpc(_returns=Datetime):
    def GetNow():
        return datetime.datetime.now()

    @srpc(Unicode, _returns=Unicode)
    def Echo(string):
        return string


Далее нужно перечислить их в файле конфигурации.
Протоколы, услуги и веб-сервисы декларируются в файле конфигурации.
