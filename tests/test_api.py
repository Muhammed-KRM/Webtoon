import pytest
from app.models.job import TranslationJob
from app.models.user import User
from app.core.security import create_access_token

# Mock user and auth headers
@pytest.fixture
def normal_user_token(client):
    # In a real db test we would create a user. 
    # For now we might depend on database init or mocking override in client
    # but let's assume valid token generation if user exists.
    # Since we use in-memory sqlite, we need to create a user first.
    from app.services.user_service import UserService
    from app.schemas.auth import UserRegister
    
    try:
        user = UserService.create_user(client.app.dependency_overrides[get_db](), UserRegister(
            username="testuser", email="test@test.com", password="password123"
        ))
    except:
        pass # Might already exist
        
    return create_access_token("testuser")

def test_translation_editor_endpoints_existence(client):
    """Simple test to verify endpoints are registered"""
    # We can't easily test full logic without complex file mocking,
    # but we can check if 401 Unauthorized is returned (meaning endpoint exists)
    
    response = client.post("/api/v1/translation/edit", json={})
    assert response.status_code == 401  # Should require auth

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
