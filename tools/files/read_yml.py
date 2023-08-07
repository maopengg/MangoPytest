import os

import yaml

from models.tools_model import EmailModel, TestEnvironmentModel


class YAMLReader:

    @classmethod
    def read_yaml(cls):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        relative_path = "../../config/config.yml"
        file_path = os.path.join(script_dir, relative_path)
        with open(file_path, 'r', encoding="utf-8") as file:
            try:
                data = yaml.safe_load(file)
                return data
            except yaml.YAMLError as e:
                print("读取YAML文件时出错:", e)

    @classmethod
    def get_environment(cls, environment) -> TestEnvironmentModel:
        data = cls.read_yaml().get(environment)
        return TestEnvironmentModel(**data)

    @classmethod
    def get_wechat(cls) -> str:
        return cls.read_yaml().get('wechat').get('webhook')

    @classmethod
    def get_email(cls) -> EmailModel:
        data = cls.read_yaml().get('email')
        return EmailModel(**data)

    @classmethod
    def get_project_name(cls) -> str:
        return cls.read_yaml().get('project_name')

    @classmethod
    def get_tester_name(cls) -> str:
        return cls.read_yaml().get('tester_name')


if __name__ == '__main__':
    print(YAMLReader.get_environment('test'))
    print(YAMLReader.get_environment('pre'))
    print(YAMLReader.get_environment('pro'))
    print(YAMLReader.get_wechat())
    print(YAMLReader.get_email())
    print(YAMLReader.get_project_name())
    print(YAMLReader.get_tester_name())
