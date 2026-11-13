"""Minimal method+path router."""

from frostline.core.errors import NotFound

ROUTES = {}


def route(method, path):
    def decorator(func):
        ROUTES[(method.upper(), path)] = func
        return func

    return decorator


def dispatch(method, path):
    handler = ROUTES.get((method.upper(), path))
    if handler is None:
        raise NotFound("no route for %s %s" % (method, path))
    return handler
