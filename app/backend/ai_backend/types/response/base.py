from typing import Optional, Dict, Any, TypedDict, Union
import datetime as dt
import collections

from .response_code import ResponseCode
from pydantic import BaseModel, Field, model_validator
from pydantic.json import timedelta_isoformat
from .exceptions import HandledException

__all__ = [
    "BaseResponse",
    "CommonResponse",
    "ErrorResponse",
]


def _dt_to_timemilis(time: dt.datetime):
    return round(time.timestamp() * 1000)


class Result(Dict):     # 5/6 heeseok : TypedDict --> Dict로 변경. TypedDict일때 기동 시 Type Exception 발생
    code: int
    message: str


class BaseResponse(BaseModel):

    timestamp: Optional[dt.datetime] = None
    code: Optional[int] = None
    message: Optional[str] = None
    traceId: Optional[str] = None
    data: Optional[Any] = Field(
        None, title="the output",  # max_length=300
    )

    class Config:
        # Pydantic v2 호환성을 위해 제거된 설정들
        json_encoders = {
            dt.datetime: _dt_to_timemilis,
            dt.timedelta: timedelta_isoformat,
        }


class CommonResponse(BaseResponse):

    @model_validator(mode='before')
    @classmethod
    def _init(cls, values):
        if isinstance(values, dict):
            values["timestamp"] = dt.datetime.utcnow()
            rc = ResponseCode.SUCCESS
            values["code"] = rc.code
            values["message"] = rc.message
            values["traceId"] = None
        return values


class ErrorResponse(BaseResponse):
    """에러 응답 클래스 - BaseResponse를 직접 상속"""
    
    @model_validator(mode='before')
    @classmethod
    def _init(cls, values):
        if isinstance(values, dict):
            # e가 딕셔너리 형태로 전달된 경우 처리
            if 'e' in values:
                e = values['e']
                if isinstance(e, HandledException):
                    values["code"] = e.code
                    values["message"] = e.message
                else:
                    # 일반 Exception의 경우 기본 에러 코드 사용
                    values["code"] = ResponseCode.UNDEFINED_ERROR.code
                    values["message"] = ResponseCode.UNDEFINED_ERROR.message
            else:
                # e가 없는 경우 기본 에러 코드 사용
                values["code"] = ResponseCode.UNDEFINED_ERROR.code
                values["message"] = ResponseCode.UNDEFINED_ERROR.message
            
            # 기본값 설정
            values["timestamp"] = dt.datetime.utcnow()
            values["traceId"] = None
        return values