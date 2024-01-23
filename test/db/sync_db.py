import pytest
from sqlalchemy import create_engine, Inspector
from sqlalchemy.orm import sessionmaker, Session

from .models import SyncUser
from src.model import SyncModel


@pytest.fixture(scope="module")
def engine():
    return create_engine('postgresql://testuser:testpassword@localhost:5433/testdb')


@pytest.fixture(scope="module")
def tables(engine):
    SyncModel.metadata.create_all(engine)
    yield
    SyncModel.metadata.drop_all(engine)


@pytest.fixture
def db_session(engine, tables):
    """Создает сессию для теста."""
    session_maker = sessionmaker(engine, expire_on_commit=False)
    with session_maker() as session:
        yield session


@pytest.fixture(scope="module")
def inspector(engine):
    """Создает инспектор для работы с метаданными базы данных."""
    return Inspector.from_engine(engine)


def test_table_exists(tables, inspector):
    """Проверяет, существует ли таблица 'user' в базе данных."""
    tables = inspector.get_table_names()

    assert "sync_user" in tables

    # Проверка функции преобразования названия класса в название таблицы
    assert "test_name" in tables

    # Проверка переопределения __tablename__
    assert "test_name_2" in tables


# Тесты
def test_create_user(db_session):
    # Тестирование сохранения
    new_user = SyncUser(name="Test User")
    new_user.save(db_session, commit=True)

    # Тестирование get
    created_user = SyncUser.get(db_session, SyncUser.id == new_user.id, first=True)
    assert created_user

    # Тестирование order_by
    new_user = SyncUser(name="Test User 2")
    new_user.save(db_session, commit=True)

    user = SyncUser.get(db_session, order_by=SyncUser.id.asc(), first=True)
    assert user.id == 1

    user = SyncUser.get(db_session, order_by=SyncUser.id.desc(), first=True)
    assert user.id == 2

    # Тестирование update
    user.update(db_session, commit=True, name='qqq')
    assert user.name == 'qqq'
