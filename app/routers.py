import logging
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from app.schemas import SubmenuRead, DishRead
from db.models import Dish, Menu, SubMenu
from db.session import get_db
from app import schemas
from db.crud import MenuDAL

from .routing.dish_routes import dish_router
from .routing.menu_routes import menu_router
from .routing.submenu_routes import submenu_router

main_router = APIRouter()
main_router.include_router(dish_router)
main_router.include_router(menu_router)
main_router.include_router(submenu_router)
