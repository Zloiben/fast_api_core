from typing import Dict

from fastapi import status

__all__ = (
    "AppException",
)


class AppException(Exception):
    """Ошибки связанные с приложением"""

    def __init__(self, status_code: status = None, message: str = None, content: Dict = None) -> None:
        self.status_code = status_code
        self.content = content
        self.message = message

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}. doc: {self.__class__.__doc__} {self.status_code=} {self.content=}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}. doc: {self.__class__.__doc__} {self.status_code=} {self.content=}"
