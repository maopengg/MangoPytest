# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-12-21 11:15
# @Author : 毛鹏


class RandomFileData:
    """获取文件对象"""

    # @classmethod
    # def get_file_obj(cls, **kwargs) -> BinaryIO:
    #     """传入文件名称，返回文件对象,参数：file_name"""
    #     project_id = kwargs.get('project_id')
    #     file_name = kwargs.get('data')
    #     file_path = os.path.join(InitPath.get_upload_files(), file_name)
    #     if os.path.exists(file_path):
    #         return open(file_path, 'rb')
    #     else:
    #         raise FileDoesNotEexistError('文件不存在')
    #
    # @classmethod
    # def get_file_path(cls, **kwargs) -> str | list:
    #     """传入文件名称，返回文件对象,参数：file_name"""
    #     file_name = kwargs.get('data')
    #     project_id = kwargs.get('project_id')
    #     HttpClient().download_file(project_id, file_name)
    #     file_path = os.path.join(GetPath.get_upload_files(), file_name)
    #     if os.path.exists(file_path):
    #         return file_path
    #     else:
    #         raise FileDoesNotEexistError('文件不存在')


if __name__ == '__main__':
    print(RandomFileData.get_file_path(**{'data': '文档库搜索112.pdf'}))
