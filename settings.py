from envparse import Env

env = Env()

#TODO: Подумать стоит ли поднимать отдельный контейнер для самого проекта, если нет то возможно стоит
#TODO: убрать парсинг URL из окружения

REAL_DATABASE_URL = env.str('REAL_DATABASE_URL', default='postgresql+asyncpg://postgres:postgres@0.0.0.0:5432/postgres')