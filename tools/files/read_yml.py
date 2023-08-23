import os

import yaml

from models.tools_model import EmailModel, TestEnvironmentModel


class YmlReader:

    def __init__(self, environment: str, path):
        self.environment = environment
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.file_path = os.path.join(script_dir, path)
        with open(self.file_path, 'r', encoding="utf-8") as file:
            try:
                self.data = yaml.safe_load(file)
            except yaml.YAMLError as e:
                print("读取YAML文件时出错:", e)

    def get_environment(self) -> TestEnvironmentModel:
        data = self.data.get(self.environment)

        return TestEnvironmentModel(**data)

    def get_wechat(self) -> str:
        return self.data.get('wechat').get('webhook')

    def get_email(self) -> EmailModel:
        data = self.data.get('email')
        return EmailModel(**data)

    def get_project_name(self) -> str:
        return self.data.get('project_name')

    def get_tester_name(self) -> str:
        return self.data.get('tester_name')


if __name__ == '__main__':
    print(YmlReader.get_environment('test'))
    print(YmlReader.get_environment('pre'))
    print(YmlReader.get_environment('pro'))
    print(YmlReader.get_wechat())
    print(YmlReader.get_email())
    print(YmlReader.get_project_name())
    print(YmlReader.get_tester_name())
