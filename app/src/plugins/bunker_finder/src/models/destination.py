from pydantic import BaseModel, Field

class DestinationModel(BaseModel):
    dst: str = Field()
    is_active: bool = Field()
    filters: list[str] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)