# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏
import json
import os.path

import pandas
import requests

from core.enums.tools_enum import StatusEnum
from core.exceptions import ToolsError, ERROR_MSG_0351
from core.models import FeiShuModel
from core.sources.element_schema import CANONICAL_ELEMENT_HEADERS
from core.utils.project_dir import project_dir


class DocumentData:

    def __init__(self):
        with open(
            os.path.join(project_dir.root_path(), "core", "settings", "feishu.json"),
            "r",
            encoding="utf-8",
        ) as f:
            self.config = FeiShuModel(**json.load(f))
        self.url = "https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/"
        self.parameter = (
            "&valueRenderOption=ToString&dateTimeRenderOption=FormattedString"
        )
        self.headers = {
            "Authorization": "Bearer t-g10442ey6YHQCZAF6EBJB4CCSJTGCOUM6N3GJ2CF",
            "Content-Type": "application/json; charset=utf-8",
        }
        self.status_enum = {v: k for k, v in StatusEnum.obj().items()}
        self.get_token()

    def get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = json.dumps(
            {"app_id": self.config.app_id, "app_secret": self.config.app_secret}
        )

        headers = {"Content-Type": "application/json"}
        response = requests.post(
            url, headers=headers, data=payload, proxies={"http": None, "https": None}
        )
        self.headers["Authorization"] = (
            f'Bearer {response.json()["tenant_access_token"]}'
        )

    def get_sheet(self, spreadsheet_token) -> list:
        response = requests.get(
            f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{spreadsheet_token}/sheets/query",
            headers=self.headers,
            proxies={"http": None, "https": None},
        )
        return response.json()["data"]["sheets"]

    def ui_element(self):
        df_list = []
        for i in self.get_sheet(self.config.surface.ui_element_id):
            url = f"{self.url}{self.config.surface.ui_element_id}/values_batch_get?ranges={i.get('sheet_id')}{self.parameter}"
            df = self.cls(url)
            df = self._canonical_element_columns(df)
            df_list.append(df.reset_index(drop=True))
        combined_df = pandas.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=["ID"], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=("UI元素表",))
        return combined_df

    @staticmethod
    def _canonical_element_columns(df: pandas.DataFrame) -> pandas.DataFrame:
        """将新旧飞书元素表统一转换为 30 个中文 ElementModel 字段。"""
        columns = [str(column).strip() for column in df.columns]
        if len(columns) == 16 and columns[:6] == [
            "ID",
            "项目名称",
            "模块名称",
            "页面名称",
            "元素名称",
            "定位方式1",
        ]:
            records = []
            for values in df.itertuples(index=False, name=None):
                row = list(values) + [None] * (16 - len(values))
                name = row[4]
                records.append(
                    [
                        row[0], row[1], row[2], row[3], name,
                        row[2] or row[3] or "通用元素",
                        "是", "是", row[15],
                        row[5], row[6], row[7], "否",
                        row[14] or f"查找元素：{name}",
                        row[8], row[9], row[10], "否", None,
                        row[11], row[12], row[13], "否", None,
                        None, None, None, None, "是", "否",
                    ]
                )
            return pandas.DataFrame(records, columns=CANONICAL_ELEMENT_HEADERS)

        aliases = {
            "*元素名称": "元素名称",
            "分类": "元素分类",
            "表达式1": "定位表达式1",
            "表达式2": "定位表达式2",
            "表达式3": "定位表达式3",
            "下标1": "元素下标1",
            "下标2": "元素下标2",
            "下标3": "元素下标3",
            "*类型-1": "定位方式1",
            "类型-2": "定位方式2",
            "类型-3": "定位方式3",
            "*定位-1": "定位表达式1",
            "定位-2": "定位表达式2",
            "定位-3": "定位表达式3",
            "元素下标-1": "元素下标1",
            "元素下标-2": "元素下标2",
            "元素下标-3": "元素下标3",
            "等待": "等待时间",
            "AI提示词": "AI定位提示词1",
        }
        normalized = df.rename(
            columns={
                source: target
                for source, target in aliases.items()
                if target not in df.columns
            }
        ).copy()
        defaults = {
            "元素分类": "通用元素",
            "AI自愈状态": "是",
            "采集快照": "是",
            "是否iframe1": "否",
            "是否iframe2": "否",
            "是否iframe3": "否",
            "可交互": "是",
            "禁用": "否",
        }
        for column, default in defaults.items():
            if column not in normalized.columns:
                normalized[column] = default
        for column in CANONICAL_ELEMENT_HEADERS:
            if column not in normalized.columns:
                normalized[column] = None
        return normalized.loc[:, CANONICAL_ELEMENT_HEADERS]

    def cls(self, url):
        response = requests.get(
            url, headers=self.headers, proxies={"http": None, "https": None}
        )
        response_dict = response.json()
        if response_dict.get("code") != 0:
            response = requests.get(
                url, headers=self.headers, proxies={"http": None, "https": None}
            )
            response_dict = response.json()
        data = response_dict["data"]["valueRanges"][0]["values"]
        return pandas.DataFrame(data[1:], columns=data[0])


if __name__ == "__main__":
    print(DocumentData().ui_element())
