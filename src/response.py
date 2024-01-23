from fastapi import status
from fastapi.responses import JSONResponse

from typing import Optional, Dict, Type, List, Union
from pydantic import BaseModel

from .utils import convert_to_set

__all__ = (
    "ResponseInterface",
    "ResponseSchema",
    "ResponsesStructure"
)


class ResponseInterface:
    """Класс для интерфейса ответов."""

    def update(self, message: str = 'Информацию изменена', data: Optional[Dict] = None) -> JSONResponse:
        """Отправить ответ, что изменение прошло успешно"""
        return self.response(status_code=status.HTTP_200_OK, message=message, data=data)

    def delete(self, message: str = 'Информация удалена', data: Optional[Dict] = None) -> JSONResponse:
        """Отправить ответ, что удаление прошло успешно"""
        return self.response(status_code=status.HTTP_200_OK, message=message, data=data)

    def insert(self, message: str = 'Информация добавлена', data: Optional[Dict] = None) -> JSONResponse:
        """Отправить ответ, что добавление прошло успешно"""
        return self.response(status_code=status.HTTP_201_CREATED, message=message, data=data)

    def not_found(self, message: str = 'Информация не найдена', data: Optional[Dict] = None) -> JSONResponse:
        """Отправить ответ, что информация не найдена"""
        return self.response(status_code=status.HTTP_404_NOT_FOUND, message=message, data=data)

    def error(
            self,
            status_code: status = status.HTTP_400_BAD_REQUEST,
            message: str = 'Произошла ошибка',
            data: Optional[Dict] = None,
            error: Optional[str] = None
    ) -> JSONResponse:
        """Отправить ответ, что произошла ошибка"""
        return self.response(status_code=status_code, message=message, data=data, error=error)

    @staticmethod
    def response(
            status_code: status,
            message: str,
            data: Optional[Dict] = None,
            error: Optional[str] = None
    ) -> JSONResponse:
        """Метод позволяет отправить ответ """

        return JSONResponse(content=dict(
            message=message, data=data, error=error
        ), status_code=status_code)


class ResponseSchema:
    """Класс позволяет создать схему ответа"""

    def __init__(self,
                 status_code: status,
                 data: Optional[Dict] = None,
                 description: Optional[str] = None,
                 model: Optional[Type[BaseModel]] = None
                 ) -> None:
        self.status_code = status_code
        self.data = data
        self.model = model
        self.description = description

    def get_schema(self) -> Dict:
        response = {
            self.status_code: {
                "description": self.description,
            }
        }
        if self.model:
            response[self.status_code]["model"] = self.model

        if self.data:
            response[self.status_code]["content"] = {
                "application/json": {
                    "example": self.data
                }
            }
        return response


class ResponsesStructure:
    """Класс позволяет делать структуру ответов"""

    def __init__(self, *schemas: ResponseSchema) -> None:
        self.__structure = convert_to_set(schemas) if structure else set()
        self.__structure.add(
            ResponseSchema(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, description="Ошибка сервера")
        )

    def add(self, response: Union[ResponseSchema, List[ResponseSchema]]) -> None:
        """Метод позволяет добавить схему ответа в структуру"""

        structure = convert_to_set(response)

        self.__structure.update(structure)

    def remove(self, response: Union[ResponseSchema, List[ResponseSchema]]) -> None:
        """Метод позволяет удалить схему ответа из структуры"""

        structure = convert_to_set(response)

        self.__structure.difference_update(structure)

    def generate(self) -> Dict:
        """
        Метод позволяет сгенерировать структуру ответов.

        Пример: {
            200: {data},
            400: {data},
        }
        """
        result = {}
        for schema in self.__structure:
            result.update(schema.get_schema())
        return result
