# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import json
from datetime import datetime
from pathlib import Path

from mangotools.enums import NoticeEnum
from mangotools.models import EmailNoticeModel, WeChatNoticeModel, TestReportModel
from mangotools.notice import EmailSend, WeChatSend

from auto_tests.project_config import ProjectEnum
from core.enums.tools_enum import ClientNameEnum, EnvironmentEnum, AutoTestTypeEnum
from core.enums.tools_enum import StatusEnum
from core.models.tools_model import CaseRunModel
from core.settings.settings import SEND_USER, EMAIL_HOST, STAMP_KEY
from core.sources import SourcesData
from core.utils import project_dir


class NoticeMain:

    def __init__(self, case_run_model: list[CaseRunModel]):
        self.case_run_model = case_run_model
        self.result_dict = None
        self.test_environment = None

    def notice_main(self):
        for i in self.case_run_model:
            self.test_environment = EnvironmentEnum.get_value(i.test_environment.value)
            self.result_dict = SourcesData.get_test_object(project_name=i.project.value, type=i.test_environment.value)
            if self.result_dict:
                if self.result_dict.get('is_notice') == StatusEnum.SUCCESS.value:
                    notice_list = SourcesData.get_notice_config(
                        is_dict=False,
                        project_name=self.result_dict.get('project_name')
                    )
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
        """统计 Allure 报告用例数量"""

        summary_path = Path(project_dir.root_path()) / "report" / "html" / "widgets" / "summary.json"

        if not summary_path.exists():
            raise FileNotFoundError(
                "未检测到 Allure 报告，请确认是否执行：\n"
                "1. pytest --alluredir=allure-results\n"
                "2. allure generate allure-results -o report/html --clean"
            )

        with summary_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        statistic = data.get("statistic", {})
        time_info = data.get("time", {})

        total = statistic.get("total", 0)
        passed = statistic.get("passed", 0)
        failed = statistic.get("failed", 0)
        broken = statistic.get("broken", 0)
        skipped = statistic.get("skipped", 0)

        # 成功率
        if total > 0:
            pass_rate = round((passed + skipped) / total * 100, 2)
        else:
            pass_rate = 0.0

        # 执行时长（转换成字符串，符合模型要求）
        duration_seconds = round(time_info.get("duration", 0) / 1000, 2)
        execution_duration = f"{duration_seconds}s"

        # 测试时间
        start_time = time_info.get("start")
        test_time = (
            self.timestamp_to_datetime(start_time)
            if start_time
            else ""
        )
        project_name = self.result_dict.get("name") or "未知项目"
        return TestReportModel(
            project_name=project_name,
            test_environment=self.test_environment,
            case_sum=total,
            success=passed,
            success_rate=pass_rate,
            warning=broken,
            fail=failed,
            execution_duration=execution_duration,  # ← 字符串
            test_time=test_time,
        )


if __name__ == '__main__':
    test_project = [
        {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.UI},
        {'project': ProjectEnum.WanAndroid, 'test_environment': EnvironmentEnum.PRO, 'type': AutoTestTypeEnum.API}
    ]
    data1: list[CaseRunModel] = [CaseRunModel(**i) for i in test_project]
    NoticeMain(data1).email_alert('11')
