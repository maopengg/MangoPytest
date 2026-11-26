from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class TargetInput(BaseModel):
    type: Literal["project", "file", "node", "feature"] = "project"
    id: str = ""


class RunOptionsInput(BaseModel):
    markers: list[str] = Field(default_factory=list, max_length=20)
    keyword: str = Field(default="", max_length=300)
    workers: int = Field(default=1, ge=1, le=16)
    reruns: int = Field(default=0, ge=0, le=10)
    max_failures: int = Field(default=0, ge=0, le=1000)


class CreateRunInput(BaseModel):
    project: str
    environment: Literal["dev", "test", "pre", "prod"] = "test"
    target: TargetInput = Field(default_factory=TargetInput)
    options: RunOptionsInput = Field(default_factory=RunOptionsInput)
    runtime_overrides: dict[str, str] = Field(default_factory=dict)
    production_confirmation: str = ""

    @field_validator("production_confirmation")
    @classmethod
    def confirmation_length(cls, value: str) -> str:
        if len(value) > 100:
            raise ValueError("生产确认内容过长")
        return value
