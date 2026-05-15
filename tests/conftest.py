import os
import tempfile
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base
from app.deps import get_db
from app.main import app


@pytest.fixture
def client():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    test_database_url = f"sqlite:///{db_path}"

    engine = create_engine(test_database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    os.close(db_fd)
    os.unlink(db_path)
