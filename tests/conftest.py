import pytest
import shutil
from src.storage.vectorstore import VectorStore

@pytest.fixture
def vectorstore_tmp(tmp_path):
    """VectorStore isolé avec base ChromaDB temporaire."""
    db_path = tmp_path / "chromadb"
    vs = VectorStore(persist_directory=str(db_path))
    yield vs
    shutil.rmtree(db_path, ignore_errors=True)
