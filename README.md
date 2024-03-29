Создание локальной копии главного репозитория:
Для начала нужно перейти в каталог, в котором вы хотите, чтобы появился каталог репозитория
и запустить в нем терминал. Для пользователей Linux/MacOS: запустить Терминал и с помощью команды
cd перейти в нужный каталог. Для пользователей Windows: перейти в Проводнике в нужный каталог,
щелкнуть правой кнопкой мыши в окне каталога и в контекстном меню выбрать пункт "Git Bash".
После запуска в терминале набрать команду:
```
git clone https://github.com/murekswork/week1
```
В результате в текущем каталоге будет создан подкаталог week_1, содержащий копию главного репозитория.
Для работы с репозиторием необходимо перейти в его каталог командой:
```
cd week1
```
Для работы celery и синхронизация google таблицы и бд необходимо прокинуть в корневой каталог проекта файл creds.json,
который я отправлю в чат проверяющему. Ссылка на таблицу:
```https://docs.google.com/spreadsheets/d/1CSA6uv3DJa383_CAvknhTmrDbIV3VtSz_WmfcCnFSyw/edit#gid=0```

Запуск основного контейнера приложения с основной базой данных, celery и rabbitmq набрать команду
```
docker-compose up --build api
```
Все необходимые зависимости и миграции для основной базы данных будут подключены и проведены документация
API будет доступно по адресу 0.0.0.0:8000

Для запуска тестового контейнера и тестовой базы набрать команду:
```
docker-compose up --build api_test
```
Результаты pytest будут в терминале.

Реализация задачи синхронизации таблицы и бд находится в директории app/services/task_services/
Конфигурация celery в директории celery_conf/

Блюда по акции синхронизируются с таблицей. Цена блюда, при обнаружении скидки высчитывается непосредственно перед 
выводом и хранится только в кеше до тех пор, пока блюдо или связанные с ним объекты или скидка не будут изменены 

Ручка для вывода всех меню со всеми связанными подменю и блюдами 
```
api/v1/menus
```

Реализация функции reverse находится в файле /tests/utils.py.
Тестовый сценарий из постмана находится в файле tests/test_dishes_and_submenus_count_in_menu.py.
Сложный ORM запрос для получения количества блюд и подменю находится в файле db/utils.py.


