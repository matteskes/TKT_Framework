from importlib.metadata import version
from typing import Optional

from TKT import (
    cli,  # noqa: F401
    distro_configs,  # noqa: F401
    fetch,  # noqa: F401
    kernel_config,  # noqa: F401
)

__version__: Optional[str]
try:
    __version__ = version("the-kernel-toolkit")
except ModuleNotFoundError:
    __version__ = None
