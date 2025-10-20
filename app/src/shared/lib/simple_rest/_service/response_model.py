from typing import Any

from httpx import Response
from pydantic import BaseModel, Field, computed_field, field_validator

from .err_msgs import sget_error_message


class ResponseModel(BaseModel):
    status_code: int = field_validator('status_code', 'status', 'code')
    headers: dict = field_validator('headers', 'header', 'head')
    data: dict|bytes|str|list = field_validator('data', 'result', 'results', 'body')
    exception: Any|None = Field(None, exclude=True, )

    @computed_field
    @property
    def detail(self) -> str|None:
        if self.status_code == -1:
            return sget_error_message(self.status_code).format(str(self.exception))
        return sget_error_message(self.status_code)

    @classmethod
    def from_response(cls, response: Response) -> 'ResponseModel':
        match response.headers.get('Content-Type'):
            case 'application/json':
                data = response.json()
            case 'text/html':
                data = response.text
            case _:
                data = response.content
        return cls(status_code=response.status_code, headers=response.headers, data=data)

    @classmethod
    def from_exception(cls, exception: Exception) -> 'ResponseModel':
        if not isinstance(exception, Exception):
            raise ValueError(f'exception must be an instance of {type(Exception())} not {type(exception)}')
        return cls(status_code=-1, headers={}, data={}, exception=exception)

    @property
    def is_success(self) -> bool:
        return self.status_code in range(200, 300)

    def get(self, key: str, default: Any = None) -> Any:
        if not isinstance(self.data, dict):
            raise ValueError(f'data must be a dict not {type(self.data)}')
        return self.data.get(key, default)