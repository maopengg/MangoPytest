# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-10 10:26
# @Author : 毛鹏
from pydantic import BaseModel, Field

from enums.api_enum import IDTypeEnum


class PropertiesModel(BaseModel):
    # setattr(properties, 'extra_field', 'value')
    lib: str = Field(alias='$lib')
    os_version: str = Field(alias='$os_version')
    lib_version: str = Field(alias='$lib_version')
    os: str = Field(alias='$os')
    maunfacturer: str = Field(alias='$maunfacturer')
    wifi: bool = Field(alias='$wifi')
    ip: str = Field(alias='$ip')
    province: str = Field(alias='$province')
    city: str = Field(alias='$city')


class TrackModel(BaseModel):
    distinct_id: str
    distinct_type: IDTypeEnum
    time: int
    type: str = 'track'
    event: str
    project: str
    time_free: bool
    properties: PropertiesModel


class TrackSignup(BaseModel):
    distinct_id: str
    distinct_type: IDTypeEnum
    original_id: str
    original_type: IDTypeEnum
    time: str
    type: str = 'track_signup'
    event: str
    project: str
    properties: PropertiesModel


class ProfileSetModel(BaseModel):
    distinct_id: str
    distinct_type: IDTypeEnum
    time: int
    type: str = "profile_set"
    project: str
    properties: PropertiesModel
