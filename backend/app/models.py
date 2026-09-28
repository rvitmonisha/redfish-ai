from typing import Any
from pydantic import BaseModel


class RedfishResponse(BaseModel):
    endpoint: str
    data: Any