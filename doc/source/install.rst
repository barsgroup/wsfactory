Installation and QuickStart guide
=================================

Установка
---------

Чтобы установить приложение достаточно выполнить в окружении:


.. code-block:: bash

    pip install wsfactory -i http://pypi.bars-open.ru/simple


Вместе с приложением будут установлены следующие зависимости:

* lxml
* spyne


Добавление приложения в проект
------------------------------

Как и все обычные django приложения, нужно просто добавить wsfactory в список
установленных приложений и расширить urlpatterns:


.. code-block:: python

    # где-то в settings.py

    INSTALLED_APPS += "wsfactory",

    # где-то в urls.py

    import wsfactory.urls

    urlpatterns += wsfactory.urls.urlpatterns


Теперь необходимо с конфигурировать wsfactory. Сначала скопируем болванку для
конфига, выполним менедж-комманду:


.. code-block:: bash

    cd path/to/directory/you/place/config/
    django_admin.py wsfactory_default_config


После чего в директории, в которой выполнялась команда появится файл ``wsfactory_config.xml``
примерно следующего содержания:


.. code-block:: xml

    <WSConfig xmlns="http://bars-open.ru/schema/wsfactory"
        ApplicationClass="spyne.application.Application"
        WsgiClass="spyne.server.django.DjangoApplication"
        ServiceClass="spyne.service.ServiceBase"
        ApiHandler="wsfactory.views.api_handler">
      <Protocols>
        <!-- Протоколы -->
        <Protocol code="soap11" direction="BOTH" module="spyne.protocol.soap.soap11.Soap11" name="SOAP 1.1"/>
        <Protocol code="json" direction="BOTH" module="spyne.protocol.json.JsonDocument" name="JSON Protocol"/>
        <Protocol code="http-rpc" direction="IN" module="spyne.protocol.http.HttpRpc" name="HTTP RPC"/>

        <!-- установите модуль spyne-smev и раскомментируйте следующие строки, чтобы добавить поддежку протоколв СМЭВ -->
        <Protocol code="soap11wsse" direction="BOTH" module="spyne_smev.wsse.Soap11WSSE" name="SOAP 1.1 WSSE"/>
        <Protocol code="smev256" direction="BOTH" module="spyne_smev.smev256.Smev256" name="СМЭВ 2.5.6"/>

      </Protocols>
      <ApiRegistry>
        <!-- API-методы -->
        <Api code="Code" module="some.module.ApiFunction" name="Do some action"/>
      </ApiRegistry>
      <Services>
        <!-- Сервисы, они же услуги - наборы методов-API -->
        <Service code="Service" name="Sample service">
          <Api code="Code"/>
        </Service>
      </Services>
      <SecurityProfile>
        <!-- Профили безопасности WS-Security. Требует установки модуля spyne-smev -->
        <Modules>
          <!-- Описание модулей -->
          <Module code="x509token" path="spyne_smev.wsse.protocols.X509TokenProfile" name="X509 Token Profile"/>
        </Modules>
        <Security module="x509token" code="security" name="Default security profile">
          <!-- Декларация объектов профилей безопасности -->
          <Param key="certificate" valueType="string">path_to_certificate_file</Param>
          <Param key="private_key" valueType="string">path_to_pkey_file</Param>
          <Param key="private_key_pass" valueType="string">pkey_password</Param>
        </Security>
      </SecurityProfile>
      <Applications>
        <!-- Реестр веб-сервисов (Соответствия протоколов-сервисов) -->
        <Application name="SampleApp" service="Service">
          <InProtocol code="soap11"/>
          <OutProtocol code="soap11"/>
        </Application>
      </Applications>
    </WSConfig>


Пишем код
---------

Подробно файл конфигурации, разберем позже, а пока создадим в нашем проекте
один простой сервис:

.. code-block:: python

    # гдето в проекте файл project/service.py
    from itertools import repeat
    from spyne import srpc, Integer, Unicode, Iterable

    @srpc(Unicode, Integer, _returns=Iterable(Unicode))
    def SayHello(name, times):
        return repeat(u"Hello, {0}!".format(name), times)


Декларируем веб-сервис
----------------------

После чего отредактируем файл ``wsfactory_config.xml``. Сперва добавим api-метод
в соответствующую секцию - в теге ApiRegistry:

.. code-block:: xml

    <ApiRegistry>
      <Api code="SayHello" module="project.service.SayHello" name="Приветствие"/>
    </ApiRegistry>

Где атрибут ``code`` - это уникальный идентификатор метода, ``module`` - путь, по
которому можно импортировать этот метод, ``name`` - человечное название метода.
Все атрибуты являются обязательными.

.. tip::
    Для редактирования xml лучше использовать IDE или редактор с поддержкой xsd-схем,
    т.к. в данном случае, будет автокомплит и проверка типов. xsd-схема
    конфигурации лежит в пакете ``wsfactory``, и если файл конфигурации был создан
    менедж-коммандой, то она будет подключена к файлу конфигурации через xsi:schemaLocation.

Дальше задекларируем сервис - то есть набор api-методов:


.. code-block:: xml

    <Services>
      <Service code="SayHelloService" name="Say Hello Service">
        <Api code="SayHello"/>
      </Service>
    </Services


Здесь атрибут ``code`` также является идентификатором, а ``name`` человечным названием.
В элементе ``Service`` обязательно должен содержаться хотя бы один элемент ``Api``, у которого в
атрибуте ``code`` указывается ссылка на api-метод из элемента ``ApiRegistry``.


Теперь осталось задекларировать сам веб-сервис:


.. code-block:: xml

    <Applications>
      <Application name="SayHelloService" service="SayHelloService" tns="http://company.domain/tns">
        <InProtocol code="http-rpc"/>
        <OutProtocol code="json"/>
      </Application>
    </Applications>

Здесь атрибут ``name`` является идентификатором веб-сервиса, атрибут ``service``
ссылкой на сервис описанный в елементе ``Services``, a ``tns`` - это неймспейс,
который будет использоваться для wsdl-документа.

В элементах ``InProtocol`` и ``OutProtocol`` в атрибутах ``code`` указывается
ссылка на протоколы, описанные в элементе ``Protocols``. В нашем примере мы
выбрали spyne-протоколы HttpRpc на входе и JsonDocument на выходе.

.. note::
    Тут же можно указать параметры инициализации протоколов, а так же профиль
    безопасности ws-security, но об этом будет сказано дальше.

В итоге должен получиться такой xml-документ:


.. code-block:: xml

      <WSConfig xmlns="http://bars-open.ru/schema/wsfactory"
        ApplicationClass="spyne.application.Application"
        WsgiClass="spyne.server.django.DjangoApplication"
        ServiceClass="spyne.service.ServiceBase"
        ApiHandler="wsfactory.views.api_handler">
      <Protocols>
        <!-- Протоколы -->
        <Protocol code="soap11" direction="BOTH" module="spyne.protocol.soap.soap11.Soap11" name="SOAP 1.1"/>
        <Protocol code="json" direction="BOTH" module="spyne.protocol.json.JsonDocument" name="JSON Protocol"/>
        <Protocol code="http-rpc" direction="IN" module="spyne.protocol.http.HttpRpc" name="HTTP RPC"/>

        <!-- установите модуль spyne-smev и раскомментируйте следующие строки, чтобы добавить поддежку протоколв СМЭВ -->
        <Protocol code="soap11wsse" direction="BOTH" module="spyne_smev.wsse.Soap11WSSE" name="SOAP 1.1 WSSE"/>
        <Protocol code="smev256" direction="BOTH" module="spyne_smev.smev256.Smev256" name="СМЭВ 2.5.6"/>

      </Protocols>
      <ApiRegistry>
        <!-- API-методы -->
        <Api code="SayHello" module="project.service.SayHello" name="Приветствие"/>
      </ApiRegistry>
      <Services>
        <!-- Сервисы, они же услуги - наборы методов-API -->
        <Service code="SayHelloService" name="Say Hello Service">
          <Api code="SayHello"/>
        </Service>
      </Services>
      <SecurityProfile>
        <!-- Профили безопасности WS-Security. Требует установки модуля spyne-smev -->
        <Modules>
          <!-- Описание модулей -->
          <Module code="x509token" path="spyne_smev.wsse.protocols.X509TokenProfile" name="X509 Token Profile"/>
        </Modules>
        <Security module="x509token" code="security" name="Default security profile">
          <!-- Декларация объектов профилей безопасности -->
          <Param key="certificate" valueType="string">path_to_certificate_file</Param>
          <Param key="private_key" valueType="string">path_to_pkey_file</Param>
          <Param key="private_key_pass" valueType="string">pkey_password</Param>
        </Security>
      </SecurityProfile>
      <Applications>
        <!-- Реестр веб-сервисов (Соответствия протоколов-сервисов) -->
        <Application name="SayHelloService" service="SayHelloService">
          <InProtocol code="http-rpc"/>
          <OutProtocol code="json"/>
        </Application>
    </WSConfig>


Подключение файла конфигурации
------------------------------

Теперь осталось подключить файл конфигурации, для этого гдето в settings.py добавим:


.. code-block:: python

    WSFACTORY_CONFIG_FILE = "/path/to/config/file/wsfactory_config.xml"


Проверяем
---------

Запустим dev-сервер и наш сервис станет доступен по урлу::

    http://localhost:8000/wsfactory/api/SayHelloService


Выполним запрос::

    curl "http://localhost:8000/wsfactory/api/SayHelloService/SayHello?name=Tim&times=4 | python -m json.tool


В результате получим:

.. code-block:: json

    [
        "Hello, Tim!",
        "Hello, Tim!",
        "Hello, Tim!",
        "Hello, Tim!"
    ]

Допустим нам понадобилось чтобы, этот же сервис отдавал данные по спецификации Soap 1.1.
Все что нам нужно - это просто добавить новый ``Application`` в конфигурацию:

.. code-block:: xml

      <Applications>
        <!-- Реестр веб-сервисов (Соответствия протоколов-сервисов) -->
        <Application name="SayHelloService" service="SayHelloService">
          <InProtocol code="http-rpc"/>
          <OutProtocol code="json"/>
        </Application>
        <Application name="SayHelloSoap" service="SayHelloSercice">
          <InProtocol code="http-rpc"/>
          <OutProtocol code="soap11"/>
        </Application>
      </Applications>


Чтобы новая версия конфигурации применилась необходимо либо перезапустить сервер,
либо выполнить менедж-комманду::

    django_admin.py wsfactory_reload


Ещё раз повторим запрос, немного изменив урл::

    curl "http://localhost:8000/wsfactory/api/SayHelloSoap/SayHello?name=Tim&times=4 | python -m json.tool


И получим результат:

.. code-block:: xml

    <senv:Envelope xmlns:tns="http://company.domain/tns" xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/">
      <senv:Body>
        <tns:SayHelloResponse>
          <tns:SayHelloResult>
            <tns:string>Hello, Tim!</tns:string>
            <tns:string>Hello, Tim!</tns:string>
            <tns:string>Hello, Tim!</tns:string>
            <tns:string>Hello, Tim!</tns:string>
          </tns:SayHelloResult>
        </tns:SayHelloResponse>
      </senv:Body>
    </senv:Envelope>


Немного модифицируем наш api-метод:

.. code-block:: python

    @srpc(Unicode, Integer,
          _returns=Iterable(Unicode, member_name="Greeting"),
          _out_variable_name="Greetings")
    def SayHello(name, times):
        return repeat(u"Hello, {0}!".format(name), times)


Перезапустим сервер, поновой выполним запрос и получим результат:

.. code-block:: xml

    <senv:Envelope xmlns:tns="http://company.domain/tns" xmlns:senv="http://schemas.xmlsoap.org/soap/envelope/">
      <senv:Body>
        <tns:SayHelloResponse>
          <tns:Greetings>
            <tns:Greeting>Hello, Tim!</tns:Greeting>
            <tns:Greeting>Hello, Tim!</tns:Greeting>
            <tns:Greeting>Hello, Tim!</tns:Greeting>
            <tns:Greeting>Hello, Tim!</tns:Greeting>
          </tns:Greetings>
        </tns:SayHelloResponse>
      </senv:Body>
    </senv:Envelope>


Таким образом, мы написали в коде api-метод, а сам веб-сервис описали декларативно
в конфигурации.