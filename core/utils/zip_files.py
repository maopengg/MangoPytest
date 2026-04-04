# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2023-09-05 9:53
# @Author : 毛鹏
import datetime
import os
import zipfile

from tools import project_dir


def delete_directory_contents(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            os.remove(file_path)
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            delete_directory_contents(dir_path)
            os.rmdir(dir_path)


def zip_files():
    file_list = os.listdir(project_dir.report())
    if len(file_list) != 0:
        timestamp = datetime.datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")
        output_path = os.path.join(project_dir.reports(), f"{timestamp}.zip")
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for root, dirs, files in os.walk(project_dir.report()):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, project_dir.report()))
        delete_directory_contents(project_dir.report())
