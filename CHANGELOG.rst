ChangeLog
=========

0.1.4
-----

* добавлен атрибут ``url`` в элементе конфигурации ``Application``, который
  позволяет установить regex url pattern для сервиса. Этот же сервис также
  будет доступен по url поумолчанию - */wsfactory/api/<Application["name"]>*
