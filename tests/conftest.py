# pylint: disable=missing-docstring, import-error

from app import app as flask_app # pylint disable=import-error
import pytest

# pytest_plugins = ['pytest_flask']

@pytest.fixture
def app():
    return flask_app
