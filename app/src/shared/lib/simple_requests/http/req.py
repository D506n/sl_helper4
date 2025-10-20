from httpx import Response, Request, URL
from pydantic import BaseModel, Field, ConfigDict, AliasChoices, computed_field
from typing import AsyncGenerator

class HTTPRequest(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    original_request: Request|None = Field(None)
    original_response: Response|None = Field(None)

    status: int = Field(-1, alias=AliasChoices("status_code", "statusCode", "Status", "StatusCode"))
    stream: bool = Field(False)

    req_url: URL = Field()
    req_method: str = Field()
    req_headers: dict|None = Field()
    req_body: dict|None = Field()

    resp_model: type[BaseModel]|None = Field(None)

    resp_headers: dict|None = Field(None)
    resp_body: dict|BaseModel|Response|None = Field(None)

    @computed_field
    @property
    def is_success(self) -> bool:
        return 200 >= self.status < 300

    @classmethod
    def from_request(cls, request: Request, body: dict) -> 'HTTPRequest':
        return cls(original_request=request, 
                   req_url=request.url, 
                   req_method=request.method, 
                   req_headers=request.headers, 
                   req_body=body)

    def parse_resp_body(self, response: Response) -> dict|BaseModel:
        if self.is_success and response.headers.get("Content-Type") == "application/json":
            resp_body = response.json() if self.resp_model is None else self.resp_model.model_validate(response.json())
        return resp_body

    def parse_response(self, response: Response) -> 'HTTPRequest':
        self.original_response = response
        self.status = response.status_code
        self.resp_headers = response.headers
        if not self.stream:
            self.resp_body = self.parse_resp_body(response)
        else:
            self.resp_body = response
        return self

    def body_to_model(self, model: type[BaseModel]):
        return model.model_validate(self.req_body)

    async def aclose(self):
        if self.original_response is not None:
            await self.original_response.aclose()

    async def iter_raw(self, chunk_size: int|None = None) -> AsyncGenerator[bytes, None]:
        if self.original_response is not None:
            async for chunk in self.original_response.aiter_raw(chunk_size=chunk_size):
                yield chunk

    async def iter_lines(self) -> AsyncGenerator[str, None]:
        if self.original_response is not None:
            async for line in self.original_response.aiter_lines():
                yield line

    async def iter_text(self, chunk_size: int|None = None) -> AsyncGenerator[str, None]:
        if self.original_response is not None:
            async for line in self.original_response.aiter_text(chunk_size=chunk_size):
                yield line

    async def iter_bytes(self, chunk_size: int|None = None) -> AsyncGenerator[bytes, None]:
        if self.original_response is not None:
            async for line in self.original_response.aiter_bytes(chunk_size=chunk_size):
                yield line