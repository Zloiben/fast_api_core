from sqlalchemy.orm import Mapped

from src.model import RequiredIdColumn, SyncModel, AsyncModel


class SyncUser(RequiredIdColumn, SyncModel):
    name: Mapped[str]


class AsyncUser(RequiredIdColumn, AsyncModel):
    name: Mapped[str]


class TestName(RequiredIdColumn, SyncModel):
    ...


class TestNameTwo(RequiredIdColumn, SyncModel):
    __tablename__ = 'test_name_2'
