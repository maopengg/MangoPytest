# -*- coding: utf-8 -*-
# @Project: MangoServer
# @Description: 企微通知封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏

from enums.tools_enum import ClientNameEnum
from exceptions.api_exception import SendMessageError
from exceptions.error_msg import ERROR_MSG_0018, ERROR_MSG_0020, ERROR_MSG_0013, ERROR_MSG_0014, ERROR_MSG_0019
from exceptions.tools_exception import ValueTypeError
from models.tools_model import WeChatNoticeModel, TestReportModel
from tools.base_request.request_tool import RequestTool
from tools.logging_tool import logger


class WeChatSend:
    """
    企业微信消息通知
    """

    def __init__(self, notice_config: WeChatNoticeModel, test_report: TestReportModel):
        self.notice_config = notice_config
        self.test_report = test_report

        self.headers = {"Content-Type": "application/json"}

    def send_wechat_notification(self):
        """
        发送企业微信通知
        :return:
        """

        text = f"""【{ClientNameEnum.PLATFORM_CHINESE.value}通知】
                    >测试项目：<font color=\"info\">{self.test_report.project_name}</font>
                    >测试环境：{self.test_report.test_environment}
                    >
                    > **执行结果**
                    ><font color=\"info\">成  功  率  : {self.test_report.success_rate}%</font>
                    >执行用例数：<font color=\"info\">{self.test_report.case_sum}</font>                                    
                    >成功用例数：<font color=\"info\">{self.test_report.success}</font>
                    >失败用例数：`{self.test_report.fail}个`
                    >异常用例数：`0 个`
                    >跳过用例数：<font color=\"warning\">0</font>
                    >用例执行时长：<font color=\"warning\">{self.test_report.execution_duration} s</font>
                    >测试时间：<font color=\"comment\">{self.test_report.test_time}</font>
                    >
                    >非相关负责人员可忽略此消息。
                    >测试报告，点击查看>>[测试报告入口](http://{self.test_report.ip}:8002/#/login)
               """
        self.send_markdown(text)

    def send_markdown(self, content):
        """
        发送 MarkDown 类型消息
        :param content: 消息内容，markdown形式
        :return:
        """
        _data = {"msgtype": "markdown", "markdown": {"content": content}}
        res = RequestTool.internal_http(url=self.notice_config.webhook, method='POST', json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            logger.error(res.text)
            raise SendMessageError(*ERROR_MSG_0018)

    def send_file_msg(self, file):
        """
        发送文件类型的消息
        @return:
        """

        _data = {"msgtype": "file", "file": {"media_id": self.__upload_file(file)}}
        res = RequestTool.internal_http(url=self.notice_config.webhook, method='POST', json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            logger.error(res.json())
            raise SendMessageError(*ERROR_MSG_0020)

    def __upload_file(self, file):
        """
        先将文件上传到临时媒体库
        :param file:
        :return:
        """
        data = {"file": open(file, "rb")}
        res = RequestTool.internal_http(url=self.notice_config.webhook, method='POST', file=data,
                                        headers=self.headers).json()
        return res['media_id']

    def send_text(self, content, mentioned_mobile_list=None):
        """
        发送文本类型通知
        :param content: 文本内容，最长不超过2048个字节，必须是utf8编码
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        :return:
        """
        _data = {"msgtype": "text", "text": {"content": content, "mentioned_list": None,
                                             "mentioned_mobile_list": mentioned_mobile_list}}

        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            # 判断手机号码列表中得数据类型，如果为int类型，发送得消息会乱码
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = RequestTool.internal_http(url=self.notice_config.webhook, method='POST', json=_data,
                                                        headers=self.headers)
                        if res.json()['errcode'] != 0:
                            logger.error(res.json())
                            raise SendMessageError(*ERROR_MSG_0019)

                    else:
                        raise ValueTypeError(*ERROR_MSG_0013)
        else:
            raise ValueTypeError(*ERROR_MSG_0014)


if __name__ == '__main__':
    # WeChatSend('zshop').send_wechat_notification()
    pass
