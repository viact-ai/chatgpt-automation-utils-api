from typing import Any, Optional

from pydantic import BaseModel


class APIResponse(BaseModel):
    error: Optional[bool] = None
    message: Optional[str] = None
    data: Optional[Any] = None
