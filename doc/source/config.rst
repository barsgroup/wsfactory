Configuration file
==================

WSConfig
--------

Корневой элемент конфигурации - ``WSConfig``, с неймспейсом *http://bars-open.ru/schema/wsfactory*.
Этот элемент может содержать необязательные атрибуты, в которых можно перегрузить классы spyne:

====================== ===================================== =====================================
Attribute              Description                           Default value
====================== ===================================== =====================================
``ApplicationClass``   Класс spyne-приложения                spyne.application.Application
``WsgiClass``          Класс wsgi-приложения                 spyne.server.django.WsgiApplication
``ServiceClass``       Класс сервиса                         spyne.service.ServiceBase
``ApiHandler``         django view для обработки запросов    wsfactory.views.api_handler
====================== ===================================== =====================================

Таким образом, если в проекте требуется перегрузить spyne-классы, то подключить
их можно в этих атрибутах.

ApiRegistry
-----------

.. todo:: добавить текст сюда

Protocols
---------

Все протоколы, которые планируется использовать в проекте, необходимо перечислить
в конфигурации в элементе ``Protocols``. Каждому протоколу соответствует один
элемент ``Protocol``, с обязательными атрибутами ``code``, ``name``, ``module``.

* ``code`` - уникальный идентификатор (обычно, просто строка, но допускаются и числа)
* ``name`` - человечное название протокола (любой юникод)
* ``module`` - путь к модулю + имя класса протокола с точкой в качестве разделителя
  (например, "spyne.protocol.http.HttpRpc")

Протоколы - это обычные python классы, и они принимают аргументы в конструкторе.
wsfactory позволяет задать параметры для протокола, которые будут переданы
как keyword-аргументы в конструктор. Для этого нужно добавить в элемент ``Protocol``
элемент ``Param``, с обязательными аргументами ``key``, ``valueType``:

* ``key`` - имя параметра, (например `validator`)
* ``valueType`` - тип параметра, допустимые значения: "string", "int", "float", "bool", "password", "text"

Так же тут можно указать два необязательных аргумента ``name`` и ``required``,
которые используются  в приложении m3_wsfatory, где:

* ``name`` - человечное имя параметра
* ``required`` - "true" или "false", указываем является-ли атрибут обязательным

Значение параметра записывает в тексте в нутри элемента ``Param``.

.. attention::

    Параметры описанные внутри элемента ``Protocol``, будут применены ко всем
    веб-сервисам, которые используют этот протокол.


Пример:

.. code-block:: xml

    <Protocols>
      <!-- Протоколы -->

      <Protocol code="soap11" direction="BOTH" module="spyne.protocol.soap.soap11.Soap11" name="SOAP 1.1">
        <Param key="validator" valueType="string">lxml</Param>
        <Param key="pretty_print" valueType="bool">true</Param>
      </Protocol>
      <Protocol code="json" direction="BOTH" module="spyne.protocol.json.JsonDocument" name="JSON Protocol"/>
      <Protocol code="http-rpc" direction="IN" module="spyne.protocol.http.HttpRpc" name="HTTP RPC"/>

    </Protocols>


Services
--------

.. todo:: добавить текст сюда


Soap WS Security
----------------

.. note::

    Данный функционал требует установки модуля ``spyne-smev``


В элементе ``SecurityProfile`` настраиваются профили безопасности SOAP WS Security.
Впервую очередь необходимо описать модули безопасности в элементах ``Module``:

.. code-block:: xml

    <SecurityProfile>
      <!-- Профили безопасности WS-Security. Требует установки модуля spyne-smev -->
      <Modules>
        <!-- Описание модулей -->
        <Module code="x509token" path="spyne_smev.wsse.protocols.X509TokenProfile" name="X509 Token Profile"/>
      </Modules>
    </SecurityProfile>

Атрибуты ``Module``:

========== ========================================== ============
Атрибут    Описание                                   Обязательный
========== ========================================== ============
code       идентификатор модуля безопасности          да
path       путь, по которому его можно импортировать  да
name       человечье название                         да
========== ========================================== ============

Модули безопасности - это классы наследники класса spyne_smev.wsse.protocols.BaseWSS.

Внути элемента ``Module``, по аналогии с ``Protocol``, можно указать параметры по умолчанию:

.. code-block:: xml

    <Module code="x509token" path="spyne_smev.wsse.protocols.X509TokenProfile" name="X509 Token Profile">
      <Param key="private_key_path" valueType="string">/path/to/private_key</Param>
      <Param key="certificate_path" valueType="string">/path/to/certificate</Param>
      <Param key="private_key_pass" valueType="password">P@ssw0rd</Param>
    </Module>

Далее декларируем профили в элементах ``Security``:

.. code-block:: xml

    <SecurityProfile>
      <!-- Профили безопасности WS-Security. Требует установки модуля spyne-smev -->
      <Modules>
        <!-- Описание модулей -->
        <Module code="x509token" path="spyne_smev.wsse.protocols.X509TokenProfile" name="X509 Token Profile"/>
      </Modules>
      <Security module="x509token" code="security" name="Default security profile">
        <Param key="certificate" valueType="string">path_to_certificate_file</Param>
        <Param key="private_key" valueType="string">path_to_pkey_file</Param>
        <Param key="private_key_pass" valueType="string">password</Param>
      </Security>
      <Security module="x509token" code="second-security" name="Second security profile">
        <Param key="certificate" valueType="string">path_to_second_certificate</Params>
        <Param key="private_key" valueType="string">path_to_second_pkey_file</Param>
        <Param key="private_key_pass" valueType="string">second-password</Param>
      </Security>
    </SecurityProfile>


Applications
------------

Здесь описываются веб-сервисы в элементах ``Application``:


.. code-block:: xml

    <Applications>
      <!-- Реестр веб-сервисов (Соответствия протоколов-сервисов) -->
      <Application name="SampleApp" service="Service">
        <InProtocol code="soap11"/>
        <OutProtocol code="soap11"/>
      </Application>
    </Application>

Атрибуты ``Application``:

============= ===================================================================== ================
Атрибут       Описание                                                              Обязательный
============= ===================================================================== ================
``name``      уникальный идентификатор, который также будет использоваться в урле   да
``service``   код сервиса, ссылка на сервис описанный в элементах ``Service``       да
``tns``       неймспейс для веб-сервиса                                             нет
``url``       regex URL, по умолчанию /wsfactory/api/<Application.name>/            нет
============= ===================================================================== ================

Внутри элемента ``Application`` в обязательном порядке должны содержаться элементы
``InProtocol`` и ``OutProtocol``.

Атрибуты ``InProtocol``/``OutProtocol``

============= ===================================================================== ================
Атрибут       Описание                                                              Обязательный
============= ===================================================================== ================
``code``      код протокола, ссылка на протокол в элементах ``Protocol``            да
``security``  код сервиса, ссылка на профиль безопасноти в элементах ``Service``    да
============= ===================================================================== ================

Так же внутри каждого из этих протоколов можно задать параметры инициализации, которые могут
перекрывать параметры поумолчанию описанные в протоколе:

.. code-block:: xml

    <Applications>
      <!-- Реестр веб-сервисов (Соответствия протоколов-сервисов) -->
      <Application name="SampleApp" service="Service">
        <InProtocol code="soap11">
          <Param key="pretty_print" valueType="bool">true</Param>
        </InProtocol>
        <OutProtocol code="soap11"/>
      </Application>
    </Application>


Валидация, схема, загрузка и request
====================================

Схема конфигурации находиться в пакете по пути wsfactory/schema/wsfactory.xsd.
В ней описаны все аспекты файла конфигурации и можно использовать её как
документацию к файлу конфигурации.

При первом запросе к сервисам, произойдет чтение файла, и выполнится валидация
по схеме. Если файл валидный, то запрос продолжит свое выполнение, wsfactory
сконструирует на основе файла конфигурации веб-сервис и передаст ему request.

Если вы допустили ошибку и файл не прошел валидацию, то будет возбуждено исключение
``wsfactory.config.ImproperlyConfigured``, с текстом ошибки похожим на формат
вывода утилиты xmllint.

.. todo:: добавить пример ошибки (pull-request приветствуется)


