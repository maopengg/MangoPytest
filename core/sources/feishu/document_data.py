# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2024-04-01 22:11
# @Author : 毛鹏
import json
import os.path

import pandas
import pandas as pd
import requests
from mangotools.enums import NoticeEnum

from core.enums.api_enum import MethodEnum, IsSchemaEnum
from core.enums.tools_enum import EnvironmentEnum, ClientEnum, StatusEnum
from core.enums.ui_enum import ElementExpEnum
from core.exceptions import ToolsError, ERROR_MSG_0351
from core.models.tools_model import FeiShuModel
from core.utils.project_dir import project_dir


class DocumentData:

    def __init__(self):
        print(project_dir.root_path())
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
            element_exp_reversal = ElementExpEnum.reversal_obj()
            df["定位方式1"] = (
                df["定位方式1"].map(element_exp_reversal).fillna(df["定位方式1"])
            )

            try:
                mask2 = df["定位方式2"].notna() & (df["定位方式2"] != "")
                if mask2.values.any():  # 使用 .values 属性来获取底层 numpy 数组
                    df.loc[mask2, "定位方式2"] = (
                        df.loc[mask2, "定位方式2"]
                        .map(element_exp_reversal)
                        .fillna(df.loc[mask2, "定位方式2"])
                    )
            except:
                pass  # 如果处理失败，保持原值不变

            # 处理定位方式3
            try:
                mask3 = df["定位方式3"].notna() & (df["定位方式3"] != "")
                if mask3.values.any():  # 使用 .values 属性来获取底层 numpy 数组
                    df.loc[mask3, "定位方式3"] = (
                        df.loc[mask3, "定位方式3"]
                        .map(element_exp_reversal)
                        .fillna(df.loc[mask3, "定位方式3"])
                    )
            except:
                pass  # 如果处理失败，保持原值不变
            df = df.rename(
                columns={
                    "ID": "id",
                    "项目名称": "project_name",
                    "模块名称": "module_name",
                    "页面名称": "page_name",
                    "元素名称": "ele_name",
                    "定位方式1": "method1",
                    "表达式1": "locator1",
                    "下标1": "nth1",
                    "定位方式2": "method2",
                    "表达式2": "locator2",
                    "下标2": "nth2",
                    "定位方式3": "method3",
                    "表达式3": "locator3",
                    "下标3": "nth3",
                    "等待": "sleep",
                }
            )
            df_list.append(df)
        combined_df = pd.concat(df_list, ignore_index=True)
        duplicate_ids = combined_df[combined_df.duplicated(subset=["id"], keep=False)]
        if not duplicate_ids.empty:
            raise ToolsError(*ERROR_MSG_0351, value=("UI元素表",))
        return combined_df



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
    print(DocumentData().api_test_case())
    print(DocumentData().api_info())
    print(DocumentData().ui_element())
    print(DocumentData().ui_test_case())
    print(DocumentData().other_test_case())
    print(DocumentData().project())
