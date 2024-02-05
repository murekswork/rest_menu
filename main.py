from fastapi import FastAPI

from app.routing.dish_routes import dish_router
from app.routing.menu_routes import menu_router
from app.routing.submenu_routes import submenu_router

app = FastAPI(title='Menu')

app.include_router(menu_router, prefix='/api/v1')
app.include_router(submenu_router, prefix='/api/v1')
app.include_router(dish_router, prefix='/api/v1')
