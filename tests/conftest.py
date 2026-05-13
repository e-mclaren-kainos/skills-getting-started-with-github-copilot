from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src import app as app_module

_INITIAL_ACTIVITIES = deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities_state():
    """Reset in-memory activities before and after each test for isolation."""
    app_module.activities = deepcopy(_INITIAL_ACTIVITIES)
    yield
    app_module.activities = deepcopy(_INITIAL_ACTIVITIES)


@pytest.fixture
def client():
    return TestClient(app_module.app)
