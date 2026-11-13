"""Component registry.

Implementations announce themselves with the ``register`` decorator and are
looked up by (kind, name) at runtime, usually with a name taken from settings.
Registering the same (kind, name) twice is an error unless ``replace=True`` is
passed, in which case the newest registration wins.
"""

from frostline.core.errors import RegistryError

_REGISTRY = {}


def register(kind, name, replace=False):
    def decorator(cls):
        key = (kind, name)
        if key in _REGISTRY and not replace:
            raise RegistryError("duplicate registration %s/%s" % key)
        _REGISTRY[key] = cls
        cls.registry_name = name
        return cls

    return decorator


def resolve(kind, name):
    try:
        return _REGISTRY[(kind, name)]
    except KeyError:
        raise RegistryError("nothing registered for %s/%s" % (kind, name))


def names(kind):
    return sorted(n for (k, n) in _REGISTRY if k == kind)
