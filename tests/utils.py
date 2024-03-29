from typing import Any

from fastapi.routing import APIRoute

from main import app

app_routes = app.routes


async def reverse(route_name: str, **kwargs: Any) -> str:
    """
    Function takes route and optionally kwargs, then checks for existence of
    route in app routes and returns route url if exists, otherwise raises exception
    """
    for route in app_routes:
        if isinstance(route, APIRoute) and route.name == route_name:
            url = route.path
            for key, value in kwargs.items():
                url = url.replace('{' + key + '}', str(value))
            return url
    raise ValueError('Invalid route name')
