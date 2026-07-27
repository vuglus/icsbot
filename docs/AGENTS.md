## Проект для работы с календарями (ICS/CalDAV)

- Регистрируем календари по chat_id/chat_type (tg/max)
- Загружаем события из ICS по ссылке или через CalDAV
- Отправляем уведомления о предстоящих событиях в чат-бот
- Не храним события в БД (только календари и отправленные уведомления)

## Структура проекта:

- app.py - главный файл приложения
- services/ - папка с сервисами
  - database.py - сервис для работы с базой данных
  - calendar_service.py - работа с календарями
  - notification_service.py - отправка уведомлений
  - caldav_client.py - клиент CalDAV
  - ics_parser.py - парсер ICS файлов
  - background_service.py - фоновые задачи
  - config_service.py - конфигурация
  - api_service.py - Flask приложение
  - api_endpoints/ - API эндпоинты
- entity/ - папка с объектами базы данных
  - sqlite/ - SQLite реализации
  - ydb/ - YDB реализации
- migrations/ - миграции базы данных

## Таблицы БД:
- calendars - зарегистрированные календари
- sent_notifications - отправленные уведомления (для дедупликации)