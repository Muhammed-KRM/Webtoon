import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings

# Test Database (SQLite in-memory)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="module")
def db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="module")
def client() -> Generator:
    # Override dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c

@pytest.fixture
async def async_client() -> AsyncGenerator:
    # Override dependency
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# Mocks
@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Mock OpenAI, Stripe and Celery to avoid external calls during tests"""
    
    # Mock OpenAI
    class MockOpenAIResponse:
        choices = [type('obj', (object,), {'message': type('obj', (object,), {'content': 'Translated Text'})})]
    
    def mock_chat_completion(*args, **kwargs):
        return MockOpenAIResponse()
        
    # Mock Celery
    def mock_celery_task(*args, **kwargs):
        return type('obj', (object,), {'id': 'mock-task-id', 'state': 'PENDING'})
    
    # Mock Redis
    class MockRedis:
        def get(self, key): return None
        def set(self, key, value, ex=None, nx=None): return True
        def delete(self, key): return True
        def lock(self, *args, **kwargs): return type('obj', (object,), {'acquire': lambda: True, 'release': lambda: None})
        
    # monkeypatch.setattr("app.services.ai_translator.client.chat.completions.create", mock_chat_completion)
    pass
