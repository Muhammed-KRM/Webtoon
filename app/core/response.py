"""
Base Response Model (Ranker tarzı)
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """Base response model for all API responses"""
    success: bool
    message: str
    data: Optional[T] = None

    @classmethod
    def success_response(cls, data: T, message: str = "Success"):
        """Create a success response"""
        return cls(success=True, message=message, data=data)

    @classmethod
    def error_response(cls, message: str):
        """Create an error response"""
        return cls(success=False, message=message, data=None)

