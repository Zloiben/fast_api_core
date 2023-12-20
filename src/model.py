from sqlalchemy import BigInteger, text, DateTime, MetaData, BinaryExpression, select, Select, Result, UnaryExpression
from sqlalchemy.orm import mapped_column, DeclarativeBase, declared_attr, selectinload, QueryableAttribute, Session, \
    Mapped
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Optional, List, Union, Self, Dict, Tuple

import datetime as dt

import re

__all__ = (
    'RequiredIdColumn',
    'RequiredUpdateAtColumn',
    'RequiredCreateAtColumn',
    'AsyncModel',
    'SyncModel'
)


metadata_obj = MetaData(naming_convention={
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
})


class Model(DeclarativeBase):
    """
    Абстрактный класс модели
    """
    __abstract__ = True
    metadata = metadata_obj

    repr_cols_num = 3
    repr_cols: Tuple[str] = tuple()

    @classmethod
    @declared_attr
    def __tablename__(cls) -> str:
        return re.sub(r'(?<!^)(?=[A-Z])', '_', cls.__name__).lower()

    def __repr__(self):
        """Relationships не используются в repr(), т.к. могут вести к неожиданным подгрузкам"""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__}. {', '.join(cols)}>"

    @classmethod
    def from_dict(cls, data: Dict) -> Self:
        """Создаёт объект из словаря."""
        return cls(**data)

    def to_dict(self) -> Dict:
        """Преобразует объект в словарь."""
        return {c.key: getattr(self, c.key) for c in getattr(self.__table__, "columns", [])}

    @classmethod
    def _prepare_select_query(
            cls,
            *expressions: BinaryExpression,
            load_columns: Optional[List[QueryableAttribute]] = None,
            order_by: Optional[UnaryExpression] = None
    ) -> Select:
        """Подготавливает запрос для модели."""
        query = select(cls)
        if expressions:
            query = query.where(*expressions)
        if load_columns:
            query = query.options(*[selectinload(column) for column in load_columns])
        query = query.order_by(order_by)
        return query

    def _select_relationship(
            self: Self,
            *args: QueryableAttribute,
            pk: QueryableAttribute,
    ) -> Select:
        """Создает запрос для загрузки связей."""
        return select(type(self)).options(
            *[selectinload(relationship) for relationship in args]
        ).where(pk == getattr(self, pk.key))

    def _load_relationship(
            self,
            result: Result,
            *args: QueryableAttribute
    ) -> None:
        """Вспомогательный метод для загрузки связей."""
        loaded_instance = result.scalars().first()
        if loaded_instance:
            for relationship in args:
                setattr(self, relationship.key, getattr(loaded_instance, relationship.key))


class AsyncModel(Model):
    __abstract__ = True

    async def save(
            self,
            session: AsyncSession,
            *,
            commit: bool = False
    ) -> None:
        session.add(self)
        await self.push(session, commit)

    @staticmethod
    async def push(
            session: AsyncSession,
            commit: bool
    ) -> None:
        """
        Метод вызывает метод определенный метод сохранения
        Важно что если commit true, то используется метод flush
        """
        method_save = session.commit if commit else session.flush
        await method_save()

    async def delete(
            self,
            session: AsyncSession,
            *,
            commit: bool = False
    ) -> None:
        """Удаляет объект из базы данных."""
        await session.delete(self)
        await self.push(session, commit)

    @classmethod
    async def get(
            cls,
            session: AsyncSession,
            *expressions: BinaryExpression,
            load_columns: Optional[List[QueryableAttribute]] = None,
            order_by: Optional[UnaryExpression] = None,
            first: bool = False
    ) -> Union[List[Self] | Self]:
        """
        Метод позволяет получить объекты с возможностью отфильтровать
        так же догрузить связи используя load_columns
        """
        query = cls._prepare_select_query(*expressions, load_columns=load_columns, order_by=order_by)
        result = await session.execute(query)
        if first:
            return result.scalars().first()
        return list(result.scalars().all())

    async def update(
            self,
            session: AsyncSession,
            *,
            commit: bool = True,
            **kwargs
    ) -> None:
        """Обновляет поля объекта и сохраняет их в базе данных."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        await self.push(session, commit)

    async def load_relationship(
            self,
            session: AsyncSession,
            pk: QueryableAttribute,
            *args: QueryableAttribute
    ) -> None:
        """Метод подгружает указанные связи"""
        stmt = self._select_relationship(*args, pk=pk)
        result = await session.execute(stmt)
        self._load_relationship(result, *args)


class SyncModel(Model):
    __abstract__ = True

    def save(
            self,
            session: Session,
            *,
            commit: bool = False
    ) -> None:
        session.add(self)
        self.push(session, commit)

    @staticmethod
    def push(
            session: Session,
            commit: bool
    ) -> None:
        """
        Метод вызывает метод определенный метод сохранения
        Важно что если commit true, то используется метод flush
        """
        method_save = session.commit if commit else session.flush
        method_save()

    def delete(
            self,
            session: Session,
            *,
            commit: bool = False
    ) -> None:
        """Удаляет объект из базы данных."""
        session.delete(self)
        self.push(session, commit)

    @classmethod
    def get(
            cls,
            session: Session,
            *expressions: BinaryExpression,
            load_columns: Optional[List[QueryableAttribute]] = None,
            order_by: Optional[UnaryExpression] = None,
            first: bool = False
    ) -> Union[List[Self] | Self]:
        """
        Метод позволяет получить объекты с возможностью отфильтровать
        так же догрузить связи используя load_columns
        """
        query = cls._prepare_select_query(*expressions, load_columns=load_columns, order_by=order_by)
        result = session.execute(query)
        if first:
            return result.scalars().first()
        return list(result.scalars().all())

    def update(
            self,
            session: Session,
            *,
            commit: bool = True,
            **kwargs
    ) -> None:
        """Обновляет поля объекта и сохраняет их в базе данных."""
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.push(session, commit)

    def load_relationship(
            self,
            session: Session,
            pk: QueryableAttribute,
            *args: QueryableAttribute
    ) -> None:
        """Метод подгружает указанные связи"""
        stmt = self._select_relationship(*args, pk=pk)
        result = session.execute(stmt)
        self._load_relationship(result, *args)


class RequiredIdColumn:
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        doc="ИД записи"
    )


class RequiredCreateAtColumn:
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        doc="Время создания"
    )


class RequiredUpdateAtColumn:
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=dt.datetime.utcnow,
        doc="Время обновления"
    )
