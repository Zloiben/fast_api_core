from enum import Enum

__all__ = (
    'HTTPMethod',
)


class HTTPMethod(str, Enum):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    PUT = 'PUT'
    PATCH = 'PATCH'
