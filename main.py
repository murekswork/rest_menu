from fastapi import FastAPI

from app.routing.routers import main_router

app = FastAPI(title='Menu')

app.include_router(main_router, prefix='/api/v1', tags=['main'])
