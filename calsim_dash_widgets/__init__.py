from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version(__name__)
except PackageNotFoundError:
    # calsim_dash_widgets not installed, likely developer mode
    __version__ = None

from . import alerts, assets, branding, cards, plots
