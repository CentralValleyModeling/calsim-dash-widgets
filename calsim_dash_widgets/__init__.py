from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # calsim_dash_widgets not installed, likely developer mode
    __version__ = None

from . import cards
