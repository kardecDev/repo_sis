# api/schemas.py
from pydantic import BaseModel

class ErrorResponse(BaseModel):
    detail: str