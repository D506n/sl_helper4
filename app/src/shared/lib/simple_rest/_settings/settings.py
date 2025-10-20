import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class LocalizationModel(BaseModel):
    error_400: str
    error_401: str
    error_402: str
    error_403: str
    error_404: str
    error_405: str
    error_406: str
    error_407: str
    error_408: str
    error_409: str
    error_410: str
    error_411: str
    error_412: str
    error_413: str
    error_414: str
    error_415: str
    error_416: str
    error_417: str
    error_418: str
    error_419: str
    error_421: str
    error_422: str
    error_423: str
    error_424: str
    error_425: str
    error_426: str
    error_428: str
    error_429: str
    error_431: str
    error_449: str
    error_451: str
    error_499: str
    error_500: str
    error_501: str
    error_502: str
    error_503: str
    error_504: str
    error_505: str
    error_506: str
    error_507: str
    error_508: str
    error_509: str
    error_510: str
    error_511: str
    error_520: str
    error_521: str
    error_522: str
    error_523: str
    error_524: str
    error_525: str
    error_526: str
    error_300: str
    error_unknown: str
    limit_reached: str
    limit_refreshed: str
    except_work: str
    sess_closed: str

    @classmethod
    def from_json(cls, path: Path) -> 'LocalizationModel':
        with path.open(encoding='UTF-8') as f:
            return cls(**json.load(f))

class ConfigModel(BaseModel):
    request_limit: int = Field(default=200)
    request_limit_period: int = Field(default=60)
    chunk_size: int = Field(default=1024)
    max_parallel_requests: int = Field(default=5)
    debug_mode: bool = Field(default=False)
    encoding: str = Field(default='utf-8')
    loc: str = Field(default='ru', exclude=True)
    texts: LocalizationModel = Field(default=LocalizationModel.from_json(Path(__file__).parent.joinpath('langs', 'ru.json')))

    @property
    def localization(self) -> str:
        return self.loc

    @localization.setter
    def localization(self, value: Literal['ru', 'en']) -> None:
        self.loc = value
        self.texts = LocalizationModel.from_json(Path(__file__).parent.joinpath('langs', f'{value}.json'))

CONFIG = ConfigModel()