import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    with TestClient(app, follow_redirects=False) as client:
        yield client


@pytest.fixture
def mock_session():
    with patch('src.models.session') as mock:
        yield mock


@pytest.fixture
def mock_user():
    return Mock(id=1, name="Test User", email="test@test.com", telegram_id=123456)


@pytest.fixture
def mock_flight():
    return Mock(flight_id=1, origin="Moscow", destination="London", date="2024-01-01")
