Создание локальной копии главного репозитория: 
Для начала нужно перейти в каталог, в котором вы хотите, чтобы появился каталог репозитория 
и запустить в нем терминал. Для пользователей Linux/MacOS: запустить Терминал и с помощью команды
cd перейти в нужный каталог. Для пользователей Windows: перейти в Проводнике в нужный каталог,
щелкнуть правой кнопкой мыши в окне каталога и в контекстном меню выбрать пункт "Git Bash". 
После запуска в терминале набрать команду 
```
git clone https://github.com/oyasnev/test
``` 
В результате в текущем каталоге будет создан подкаталог week_1, содержащий копию главного репозитория. 
Для работы с репозиторием необходимо перейти в его каталог командой 
```
cd week_1
```
Далее в корневом каталоге развернуть виртуальное окружение python командой
```
python3 -m venv .venv
```
Создать и запустить контейнер с postgresql
```
docker-compose up -d --build
```
Активировать виртуальное окружение и установить зависимости проекта
```
source .venv/bin/activate
pip install -r requirements.txt
```
Для миграций базы данных проинициализировать файлы alembic
```
alembic init migrations
```
В появившемся в корне проекта файле alembic.ini изменить строку sqalchemy.url
```
sqlalchemy.url = postgresql://postgres:postgres@0.0.0.0:5432/postgres
```
В файле migrations/env.py импортировать Base и поменять target_metadata
```
from db.models import Base
target_metadata = Base.metadata
```
Выполнить миграции
```
alembic revision --autogenerate
alembic upgrade heads
```
Запустить сервер приложения
```
uvicorn main:app --reload
```


