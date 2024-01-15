# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
from pydantic import BaseModel


class LoginModel(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    expires_in: int
    scope: str


class ResponseModel(BaseModel):
    error: str | None = None
    error_description: str | None = None
    data: LoginModel | None
    status: int | str | None
    message: str | None

    @classmethod
    def get_obj(cls, result: dict):
        return cls(status=result.get('status'),
                   message=result.get('message'),
                   data=result.get('data'),
                   error=result.get('error'),
                   error_description=result.get('error_description'))
