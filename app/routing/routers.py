from fastapi import APIRouter

from app.routing.dish_routes import dish_router
from app.routing.menu_routes import menu_router
from app.routing.submenu_routes import submenu_router

main_router = APIRouter()
main_router.include_router(dish_router)
main_router.include_router(menu_router)
main_router.include_router(submenu_router)
