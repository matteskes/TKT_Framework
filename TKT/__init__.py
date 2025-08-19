from importlib.metadata import version

__version__: str | None
try:
    __version__ = version("the-kernel-toolkit")
except ModuleNotFoundError:
    __version__ = None
