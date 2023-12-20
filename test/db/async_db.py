import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, async_scoped_session

from .models import AsyncUser
from src.model import AsyncModel


@pytest.fixture(scope="module")
async def engine():
    # Создание асинхронного движка
    engine = create_async_engine('postgresql+asyncpg://testuser:testpassword@localhost:5433/testdb', echo=True)
    async with engine.begin() as conn:
        # Асинхронное создание всех таблиц
        await conn.run_sync(AsyncModel.metadata.create_all)

    yield engine

    # Очистка после завершения тестов
    async with engine.begin() as conn:
        await conn.run_sync(AsyncModel.metadata.drop_all)


@pytest.fixture
async def db_session(engine):
    """Создает асинхронную сессию для теста."""
    # Создание асинхронной фабрики сессий
    async_session_maker = async_sessionmaker(
        engine, expire_on_commit=False
    )

    # Создание асинхронной сессии
    async with async_session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_create_user(db_session):
    # Тестирование сохранения
    new_user = AsyncUser(name="Test User")
    await new_user.save(db_session, commit=True)

    # Тестирование get
    created_user = AsyncUser.get(db_session, AsyncUser.id == new_user.id, first=True)
    assert created_user

    # Тестирование order_by
    new_user = AsyncUser(name="Test User 2")
    new_user.save(db_session, commit=True)

    user = AsyncUser.get(db_session, order_by=AsyncUser.id.asc(), first=True)
    assert user.id == 1

    user = AsyncUser.get(db_session, order_by=AsyncUser.id.desc(), first=True)
    assert user.id == 2

    # Тестирование update
    user.update(db_session, commit=True, name='qqq')
    assert user.name == 'qqq'
