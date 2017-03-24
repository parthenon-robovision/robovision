from app import app as flask_app
import pytest

# pytest_plugins = ['pytest_flask']

@pytest.fixture
def app():
    return flask_app
