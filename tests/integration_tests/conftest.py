import pytest

from backend.src.app import app as flask_app
from CNN.src.app import app as cnn_app
from CNN.src.app import load_cnn_model


@pytest.fixture(scope='session')
def init_flask_app():
    return flask_app.run(host="0.0.0.0", port=8000, debug=True)


@pytest.fixture(scope='session')
def init_cnn_app():
    load_cnn_model()
    return cnn_app.run(host="0.0.0.0", port=7000, debug=True)
