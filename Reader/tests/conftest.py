import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..database import Base, get_db
from ..main import app
from ..config import settings

# Override database settings for testing
settings.DATABASE_URL = "sqlite:///:memory:"

# Create test database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create test database tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override database dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def client():
    """Create test client."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def db_session():
    """Create database session."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Create test user."""
    from ..models import User
    user = User(
        email="test@example.com",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_collection(db_session, test_user):
    """Create test collection."""
    from ..models import Collection
    collection = Collection(
        name="Test Collection",
        description="Test Description",
        user_id=test_user.id
    )
    db_session.add(collection)
    db_session.commit()
    db_session.refresh(collection)
    return collection

@pytest.fixture
def test_document(db_session, test_collection):
    """Create test document."""
    from ..models import Document
    document = Document(
        title="Test Document",
        content="Test Content",
        collection_id=test_collection.id
    )
    db_session.add(document)
    db_session.commit()
    db_session.refresh(document)
    return document

@pytest.fixture
def test_token(test_user):
    """Create test JWT token."""
    from ..auth.security import create_access_token
    return create_access_token(data={"sub": test_user.email}) 