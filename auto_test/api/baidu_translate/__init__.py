from mangokit import singleton, DataClean
from pydantic import BaseModel, ConfigDict

from auto_test.project_config import BaiduTranslateEnum
from enums.tools_enum import AutoTestTypeEnum
from models.api_model import ApiBaseDataModel
from tools.log import log
from tools.project_public_methods import ProjectPublicMethods


@singleton
class BaiduTranslateModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    user_info: dict | None = None
    headers: dict | None = None
    test_environment: int
    base_data_model: ApiBaseDataModel
    data_clean: DataClean = DataClean()
    cache_data: dict = {}


def data_init():
    """
    登录接口，获取通用token
    :return:
    """
    data_model: BaiduTranslateModel = ProjectPublicMethods.get_data_model(BaiduTranslateModel, BaiduTranslateEnum,
                                                                          AutoTestTypeEnum.API)

    data_model.cache_data['app_id'] = "20221117001456480"
    data_model.cache_data['secret_key'] = "YU2_BJkJoiiLRyBBkL0F"

    log.info(f'{BaiduTranslateEnum.NAME.value}的API在自动化基础信息设置完成！')


data_init()
