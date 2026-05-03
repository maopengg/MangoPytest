# -*- coding: utf-8 -*-
"""
文件 Repository
"""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.base import BaseRepository
from auto_tests.bdd_api_mock.data_factory.entities.file.file_entity import FileEntity


class FileRepo(BaseRepository[FileEntity]):
    """文件 Repository"""
    model = FileEntity
    CODE_FIELD = "file_id"

    def __init__(self, session: Session):
        super().__init__(session)

    def get_by_file_id(self, file_id: str) -> Optional[FileEntity]:
        """根据文件ID获取文件"""
        stmt = select(FileEntity).where(FileEntity.file_id == file_id)
        return self.session.execute(stmt).scalar_one_or_none()

    def get_by_uploader(self, uploader_id: int, limit: int = 100) -> List[FileEntity]:
        """根据上传者获取文件"""
        stmt = select(FileEntity).where(
            FileEntity.uploader_id == uploader_id
        ).limit(limit)
        return list(self.session.execute(stmt).scalars().all())
