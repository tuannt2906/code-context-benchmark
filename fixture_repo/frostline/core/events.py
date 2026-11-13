"""Tiny synchronous event bus.

Handlers subscribe to a topic with ``@subscribe(topic)``. ``EventBus.publish``
invokes the handlers of a topic in the order they were subscribed, passing the
payload and the bus context (which carries the database and settings).
"""

_SUBSCRIBERS = {}


def subscribe(topic):
    def decorator(func):
        _SUBSCRIBERS.setdefault(topic, []).append(func)
        return func

    return decorator


class EventBus:
    def __init__(self, context):
        self.context = context
        self.published = []

    def publish(self, topic, payload):
        self.published.append(topic)
        results = []
        for handler in _SUBSCRIBERS.get(topic, []):
            results.append(handler(payload, self.context))
        return results


def subscribers(topic):
    return [f.__name__ for f in _SUBSCRIBERS.get(topic, [])]
