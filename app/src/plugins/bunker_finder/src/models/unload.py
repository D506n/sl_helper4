from pydantic import BaseModel, Field
from .destination import DestinationModel

class UnloadModel(BaseModel):
    is_active: bool = Field()
    source: str = Field()
    comment: str = Field('')
    artifact_path: str = Field('')
    destinations: list[DestinationModel] = Field(default_factory=list)