import pytest
from app import create_app

@pytest.fixture()
def app(tmp_path):
    return create_app({
        "TESTING": True,
        "DATABASE": str(tmp_path / "test.db"),
        "MIN_BOOKING_MINUTES": 30,
        "MAX_BOOKING_MINUTES": 240,
        "SENSOR_THRESHOLD": 75,
    })

@pytest.fixture()
def client(app):
    return app.test_client()
