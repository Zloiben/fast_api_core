from typing import TypeVar, Set


__all__ = (
    'is_iterable',
    'convert_to_set'
)

T = TypeVar('T')


def is_iterable(obj: T) -> bool:
    """Функция для проверки является ли объект итерируемым"""

    if isinstance(obj, str):
        return False
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def convert_to_set(obj: T) -> Set:
    """Функция для конвертации различных данных в множество"""

    if not is_iterable(obj):
        return {obj}
    return set(obj)
