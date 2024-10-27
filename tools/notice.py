# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import json
from datetime import datetime

from mangokit import EmailSend, WeChatSend, EmailNoticeModel, WeChatNoticeModel, TestReportModel
from mangokit.tools.other.native_ip import get_host_ip

from auto_test.project_enum import ProjectEnum
from enums.tools_enum import ClientNameEnum, NoticeEnum, EnvironmentEnum, AutoTestTypeEnum
from enums.tools_enum import StatusEnum
from models.tools_model import CaseRunModel
from settings.settings import SEND_USER, EMAIL_HOST, STAMP_KEY
from sources import SourcesData
from tools import InitPath


class NoticeMain:

    def __init__(self, case_run_model: list[CaseRunModel]):
        self.case_run_model = case_run_model
        self.result_list = None
        self.test_environment = None

    def notice_main(self):
        for i in self.case_run_model:
            self.test_environment = EnvironmentEnum.get_value(i.test_environment.value)

            self.result_list = SourcesData \
                .project[SourcesData.project['name'] == i.project.value] \
                .to_dict(orient='records')
            if self.result_list:
                if self.result_list[0].get('is_notice') == StatusEnum.SUCCESS.value:
                    notice_list = SourcesData \
                        .project[SourcesData.notice_config['project_id'] == self.result_list[0].get('id')] \
                        .to_dict(orient='records')
                    for notice in notice_list:
                        if notice.get('type') == NoticeEnum.MAIL.value:
                            try:
                                self.__wend_mail_send(eval(notice.get('config')), )
                            except SyntaxError:
                                raise SyntaxError("邮件发送人输入的不是一个list")
                        elif notice.get('type') == NoticeEnum.WECOM.value:
                            self.__we_chat_send(notice.get('config'), )

    @classmethod
    def email_alert(cls, content: str) -> None:
        """
        发送邮件
        """
        user_list = ['729164035@qq.com', ]
        email = EmailSend(EmailNoticeModel(
            send_user=SEND_USER,
            email_host=EMAIL_HOST,
            stamp_key=STAMP_KEY,
            send_list=user_list,
        ))
        email.send_mail(user_list, f'【{ClientNameEnum.PLATFORM_CHINESE.value}服务运行通知】', content)

    def __we_chat_send(self, webhook: str):
        wechat = WeChatSend(WeChatNoticeModel(webhook=webhook), self.get_case_count())
        wechat.send_wechat_notification()

    def __wend_mail_send(self, send_list: list):
        email = EmailSend(EmailNoticeModel(
            send_user=SEND_USER,
            email_host=EMAIL_HOST,
            stamp_key=STAMP_KEY,
            send_list=send_list,
        ), self.get_case_count())
        email.send_main()

    @classmethod
    def timestamp_to_datetime(cls, timestamp_ms):
        timestamp_s = timestamp_ms / 1000.0
        dt_object = datetime.fromtimestamp(timestamp_s)
        return dt_object.strftime('%Y-%m-%d %H:%M:%S')

    def get_case_count(self) -> TestReportModel:
        """ 统计用例数量 """
        try:
            file_name = fr"{InitPath.project_root_directory}\report\html\widgets\summary.json"
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
                statistic = data['statistic']
                _time = data['time']
                # 判断运行用例总数大于0
                if statistic["total"] > 0:
                    # 计算用例成功率
                    pass_rate = round(
                        (statistic["passed"] + statistic["skipped"]) / statistic["total"] * 100, 2
                    )
                else:
                    # 如果未运行用例，则成功率为 0.0
                    pass_rate = 0.0
                # 收集用例运行时长
                time = _time if statistic['total'] == 0 else round(_time['duration'] / 1000, 2)
                try:
                    return TestReportModel(project_id=self.result_list[0].get('id'),
                                           project_name=self.result_list[0].get('name'),
                                           test_environment=self.test_environment,
                                           ip=get_host_ip(),
                                           case_sum=statistic['total'],
                                           success=statistic['passed'],
                                           success_rate=pass_rate,
                                           warning=statistic['broken'],
                                           fail=statistic['failed'],
                                           execution_duration=time,
                                           test_time=self.timestamp_to_datetime(_time['start']))
                except KeyError:
                    raise KeyError('结果为空不发送邮件，请检查用例执行过程错误原因！')
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "程序中检查到您未生成allure报告，"
                "通常可能导致的原因是allure环境未配置正确，"
            ) from exc


if __name__ == '__main__':
    test_project = [
        {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
        {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API}
    ]
    data1: list[CaseRunModel] = [CaseRunModel(**i) for i in test_project]
    NoticeMain(data1).email_alert('11')
