import pytest
import shutil
from src.storage.vectorstore import VectorStore
from src.storage.models import AuditLogger


@pytest.fixture
def vectorstore_tmp(tmp_path):
    """VectorStore isolé avec base ChromaDB temporaire."""
    db_path = tmp_path / "chromadb"
    vs = VectorStore(persist_directory=str(db_path))
    yield vs
    shutil.rmtree(db_path, ignore_errors=True)

@pytest.fixture
def logger_tmp(tmp_path):
    db_path = tmp_path / "audit.db"
    logger = AuditLogger(db_path=db_path)
    yield logger
    shutil.rmtree(db_path, ignore_errors=True)


