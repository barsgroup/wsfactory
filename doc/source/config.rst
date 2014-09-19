Configuration file
==================

#TODO


ApiRegistry
-----------

#TODO

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

    Параметры описанные внутри элемента ``Protocol`, будут применены ко всем
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

#TODO

WS Security
-----------

#TODO

Applications
------------

#TODO

