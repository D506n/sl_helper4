from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from .unload import UnloadModel

class NodeModel(BaseModel):
    full_path: str = Field(alias='fullPath')
    version: int = Field(0)
    node_creation_date: datetime = Field(alias='nodeCreationDate')
    node_desription: str = Field('', alias='nodeDesription')
    store_date: datetime|None = Field(None, alias='storeDate')
    store_login: str|None = Field(None, alias='storeLogin')
    publish_date: datetime|None = Field(None, alias='publishDate')
    publish_login: str|None = Field(None, alias='publishLogin')
    link: str = Field('')
    mime: str = Field('')
    status: str = Field()
    data: UnloadModel|None = Field(None)

    @field_validator('node_creation_date', 'store_date', 'publish_date')
    def datetime_validator(cls, v):
        if isinstance(v, datetime):
            return v
        return datetime.strptime(v, '%Y-%m-%dT%H:%M:%S.%f%z')