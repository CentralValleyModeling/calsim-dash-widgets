from pathlib import Path
from typing import Generator

import dash
import dash_bootstrap_components as dbc
import pandss as pdss
import pytest


@pytest.fixture(scope="session")
def dss_file() -> Path:
    here = Path(__file__).parent
    return here / "assets" / "DV.dss"


@pytest.fixture(scope="session")
def dss(dss_file: Path) -> Generator[pdss.DSS, None, None]:
    with pdss.DSS(dss_file) as dss:
        yield dss


@pytest.fixture(scope="session")
def rts(dss: pdss.DSS) -> Generator[pdss.RegularTimeseries, None, None]:
    path = pdss.DatasetPath(b="asdfasdfasdf")
    yield dss.read_rts(path)


@pytest.fixture(scope="function")
def app():
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
    yield app
