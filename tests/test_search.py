from search import (
    app,
    model,
    get_model,
    fetch_similar_items_from_supabase,
    SentenceTransformer,
    gc,
    HTTPException
)
import pytest
from fastapi.testclient import TestClient
from starlette.concurrency import run_in_threadpool
from unittest.mock import MagicMock
import numpy as np
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.join(current_dir, '..')
sys.path.insert(0, parent_dir)


# --- Test Fixtures/Setup ---


@pytest.fixture(scope="module")
def client():
    """Provides a TestClient instance for making requests to the FastAPI app."""
    return TestClient(app)

# Use a fixture to ensure the global model is present for testing


@pytest.fixture(autouse=True, scope="function")
def setup_model_for_tests():
    """Mocks the model loading process if it hasn't happened in main.py."""
    global model
    if model is None:
        # We need a mock model that has the necessary methods for the tests
        mock_model = MagicMock(spec=SentenceTransformer)

        # Configure the mock model's encode method
        # It must return a numpy array of shape (batch_size, embedding_dimension)
        mock_model.encode.return_value = np.array(
            [[0.1] * 768], dtype=np.float32)

        # Temporarily set the global model for testing purposes
        original_model = model
        model = mock_model

        # Yield control back to the test
        yield

        # Teardown: Restore the original global model state
        model = original_model
    else:
        # If the actual model is loaded, just use it
        yield

        # 1. get_model Unit Tests


def test_get_model_success(setup_model_for_tests):
    """Test that get_model returns the model when it is loaded."""
    # The setup_model_for_tests fixture ensures 'model' is not None
    assert get_model() is not None


def test_get_model_not_loaded(mocker):
    """Test that get_model raises a RuntimeError if the model is None."""
    global model
    original_model = model
    try:
        # Temporarily set the global model to None
        model = None
        with pytest.raises(RuntimeError) as excinfo:
            get_model()
        assert "Model not loaded" in str(excinfo.value)
    finally:
        # Restore the model state
        model = original_model
