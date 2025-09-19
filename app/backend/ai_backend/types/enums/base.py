from typing import Union
from enum import Enum, unique, IntEnum
import json

import logging

import autologging


__all__ = [
    "BaseEnum",
    "use_enum_values",
    "values_callable",
    "Locale",
    "LogLevel",
]


@unique
class BaseEnum(str, Enum):

    @property
    def describe(self):
        # self is the member here
        return self.name, self.value


    def __str__(self) -> str:
        return str(self.value)


    def __repr__(self) -> str:
        return json.dumps(self.value)


    def __eq__(cls, v):
        return cls.value == cls.of(v).value


    # @classmethod
    # def _missing_(cls, type):
    #     if isinstance(type, str):
    #         for item in cls:
    #             if item.value.lower() == type.lower():
    #                 return item
    #     else:
    #         for item in cls:
    #             if item.value == type:
    #                 return item

    @classmethod
    def _missing_(cls, type):
        try:
            if isinstance(type, str):
                matched = [
                    item for item in cls if item.value.lower() == type.lower()
                ]
            else:
                matched = [item for item in cls if item.value == type]
            return matched[0]

        except IndexError:
            raise ValueError(f"'{type}' is not in {cls.__name__}")


    def ignore_case(self) -> str:
        return str(self.value).lower()


    @classmethod
    def of(cls, type):
        return cls._missing_(type)


def use_enum_values(x: Union[Enum, BaseEnum]):
    # (cls._member_map_[name] for name in cls._member_names_)
    return [e.value for e in x]


def values_callable(x: Union[Enum, BaseEnum]):
    # (cls._member_map_[name] for name in cls._member_names_)
    return [e.value for e in x]


class Locale(BaseEnum):
    KO = "ko"
    EN = "en"


class LogLevel(IntEnum):

    CRITICAL = logging.CRITICAL  # 50
    FATAL = logging.FATAL        # 50

    ERROR = logging.ERROR        # 40

    WARNING = logging.WARNING    # 30
    WARN = logging.WARN          # 30

    INFO = logging.INFO          # 20

    DEBUG = logging.DEBUG        # 10

    TRACE = autologging.TRACE    # 1

    NOTSET = logging.NOTSET      # 0


    @classmethod
    def _missing_(cls, type):
        try:
            if isinstance(type, str):
                matched = [
                    item for item in cls if item.name.lower() == type.lower()
                ]
            else:
                matched = [item for item in cls if item.value == type]
            return matched[0]

        except IndexError:
            raise ValueError(f"'{type}' is not in {cls.__name__}")


    @classmethod
    def of(cls, type):
        return cls._missing_(type)
