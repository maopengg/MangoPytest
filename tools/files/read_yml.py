import os

import yaml

from config.settings import CONFING_PATH
from models.tools_model import EmailModel, TestEnvironmentModel


class YmlReader:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, CONFING_PATH)
    with open(file_path, 'r', encoding="utf-8") as file:
        try:
            data = yaml.safe_load(file)
        except yaml.YAMLError as e:
            print("读取YAML文件时出错:", e)

    @classmethod
    def get_environment(cls, environment) -> TestEnvironmentModel:
        data = cls.data.get(environment)

        return TestEnvironmentModel(**data)

    @classmethod
    def get_wechat(cls) -> str:
        return cls.data.get('wechat').get('webhook')

    @classmethod
    def get_email(cls) -> EmailModel:
        data = cls.data.get('email')
        return EmailModel(**data)

    @classmethod
    def get_project_name(cls) -> str:
        return cls.data.get('project_name')

    @classmethod
    def get_tester_name(cls) -> str:
        return cls.data.get('tester_name')


if __name__ == '__main__':
    print(YmlReader.get_environment('test'))
    print(YmlReader.get_environment('pre'))
    print(YmlReader.get_environment('pro'))
    print(YmlReader.get_wechat())
    print(YmlReader.get_email())
    print(YmlReader.get_project_name())
    print(YmlReader.get_tester_name())
