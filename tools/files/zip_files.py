# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-09-05 9:53
# @Author : 毛鹏
import datetime
import os
import zipfile

from config.settings import REPORT_PATH, ZIP_REPORT_PATH


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
    file_list = os.listdir(REPORT_PATH)
    if len(file_list) != 0:
        timestamp = datetime.datetime.now().strftime("%Y年%m月%d日%H时%M分%S秒")
        output_path = os.path.join(ZIP_REPORT_PATH, f"{timestamp}.zip")
        with zipfile.ZipFile(output_path, 'w') as zipf:
            for root, dirs, files in os.walk(REPORT_PATH):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, REPORT_PATH))
        delete_directory_contents(REPORT_PATH)


zip_files()
