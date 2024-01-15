# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
from pydantic import BaseModel


class SubAccount(BaseModel):
    id: int
    subAccountName: str
    subAccountId: str
    status: int
    createTime: str
    updateTime: str
    rtbAdvertiserId: str
    mediaAccountId: str
    mediaAccountName: str
    mediaPlatformName: str = None
    mediaPlatformPlatformCode: str = None
    brandAdvertiserId: str
    brandAdvertiser: str
    accountIndustry: str


class LoginModel(BaseModel):
    avatar: str
    email: str
    nickName: str
    token: str
    userId: int
    userName: str


class ResponseModel(BaseModel):
    data: LoginModel | SubAccount | list | dict | None
    status: int
    message: str | None

    @classmethod
    def get_obj(cls, result: dict):
        return cls(status=result.get('status'),
                   message=result.get('message'),
                   data=result.get('data'))
