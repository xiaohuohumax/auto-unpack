from importlib.metadata import PackageNotFoundError, version

from .app import App

try:
    __version__ = version(__package__)
except PackageNotFoundError:
    __version__ = "unknown"

__all__ = ['App']
