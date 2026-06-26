## Проект для работы с ics файлами

- загружаем ics файлы по ссылке в БД 
- выдаём актуальные события по запросу пользователя

## Структура проекта:

- app.py - главный файл приложения
- services/ - папка с сервисами
-- database.py  - сервис для работы с базой данных
- config - папка с конфигурацией (config.yml)
- entities/ - папка с объектами базы данных для каждого типа базы данных
- entities/sqlite/ - entities для sqlite
- entities/ydb/ - entities для YDB
- controllers/ - папка с api endpints 

