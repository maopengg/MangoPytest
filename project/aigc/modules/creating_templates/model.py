# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-08 11:25
# @Author : 毛鹏
from pydantic import BaseModel


class CreatingTemplatesModel(BaseModel):
    createTime: str
    updateTime: str
    id: int
    accountId: str
    accountName: str
    brandName: str
    marketingTarget: str
    grade: str
    business: str
    firstLevel: str
    secondLevel: str
    kpis: str | None
    userId: int
    user: str
    status: int


class ResponseModel(BaseModel):
    data: list[CreatingTemplatesModel] | None
    status: int
    message: str | None

    @classmethod
    def get_obj(cls, result: dict):
        return cls(status=result.get('status'),
                   message=result.get('message'),
                   data=result.get('data'))
