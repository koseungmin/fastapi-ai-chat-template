from enum import IntEnum
from .base import BaseEnum


__all__ = [
    "Sort",
]

class Sort(BaseEnum):
    desc = "desc"
    asc = "asc"

class SortOrder(IntEnum):
    DESC = 1
    ASC = -1
