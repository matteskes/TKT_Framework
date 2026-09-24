from importlib.metadata import version
from typing import Optional

__version__: Optional[str]
try:
    __version__ = version("the-kernel-toolkit")
except ModuleNotFoundError:
    __version__ = None
