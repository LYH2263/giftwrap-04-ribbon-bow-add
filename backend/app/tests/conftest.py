import pytest
from app import db, seed


@pytest.fixture
def gw_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return db.DB_PATH
