from sqlalchemy.orm import Mapped

from src.model import RequiredPrimaryIdColumn, SyncModel, AsyncModel


class SyncUser(RequiredPrimaryIdColumn, SyncModel):
    name: Mapped[str]


class AsyncUser(RequiredPrimaryIdColumn, AsyncModel):
    name: Mapped[str]


class TestName(RequiredPrimaryIdColumn, SyncModel):
    ...


class TestNameTwo(RequiredPrimaryIdColumn, SyncModel):
    __tablename__ = 'test_name_2'
