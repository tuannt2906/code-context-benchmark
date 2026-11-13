"""Optional plugins. Importing this package registers every plugin.

Plugins are imported after the built-in packages (see api/app.py), so a plugin
registered with ``replace=True`` takes precedence over a built-in component.
"""

from frostline.plugins import express, island, insurance  # noqa: F401
