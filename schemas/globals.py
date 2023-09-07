from typing import TypeVar, List, Generic

from pydantic import BaseModel

T = TypeVar("T")


class DataAndCount(BaseModel, Generic[T]):
    data: List[T]
    count: int
