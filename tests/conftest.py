import os

import pytest

from app import create_app


@pytest.fixture
def app():
    os.environ.setdefault("OPENCODEGO_API_KEY", "test-api-key")
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
