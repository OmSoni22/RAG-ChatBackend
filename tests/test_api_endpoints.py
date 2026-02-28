"""
Integration tests for User API endpoints.

These tests verify the full request/response cycle.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_create_user_endpoint(client: TestClient, sample_user_data: dict):
    """Test POST /api/v1/users endpoint."""
    # Act
    response = client.post("/api/v1/users/", json=sample_user_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == sample_user_data["name"]
    assert data["description"] == sample_user_data["description"]
    assert "id" in data


@pytest.mark.integration
def test_list_users_endpoint(client: TestClient, sample_user_data: dict):
    """Test GET /api/v1/users endpoint."""
    # Arrange - Create some users first
    client.post("/api/v1/users/", json=sample_user_data)
    client.post("/api/v1/users/", json={"name": "Another User"})
    
    # Act
    response = client.get("/api/v1/users/")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.integration
def test_create_user_validation_error(client: TestClient):
    """Test validation error for invalid user data."""
    # Act - Missing required 'name' field
    response = client.post("/api/v1/users/", json={"description": "No name"})
    
    # Assert
    assert response.status_code == 422
    data = response.json()
    assert "error" in data
    assert data["error"] is True


@pytest.mark.integration
def test_health_check(client: TestClient):
    """Test health check endpoint."""
    # Act
    response = client.get("/api/health")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.integration
def test_request_id_in_response(client: TestClient):
    """Test that request ID is included in response headers."""
    # Act
    response = client.get("/api/health")
    
    # Assert
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0
