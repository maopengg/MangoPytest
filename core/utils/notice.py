# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import json
from datetime import datetime
from pathlib import Path

from mangotools.models import EmailNoticeModel, FeiShuNoticeModel, TestReportModel, WeChatNoticeModel
from mangotools.notice import EmailSend, FeiShuSend, WeChatSend

from core.settings.settings import SEND_USER, EMAIL_HOST, STAMP_KEY
from core.utils import project_dir


class NoticeMain:
    """测试报告通知（邮件 / 企微 / 飞书），渠道由项目 __init__.py 控制"""

    def __init__(self, project_name: str, project_display_name: str,
                 test_environment: str, proj):
        self.project_name = project_name
        self.project_display_name = project_display_name
        self.test_environment = test_environment
        self.proj = proj

    def notice_main(self):
        report = self._get_case_count()
        if report is None:
            return
        if report.fail == 0 and report.warning == 0:
            return

        channel = getattr(self.proj, "NOTICE_CHANNEL", "")

        if channel == "email":
            self._send_email(report)
        elif channel == "wechat":
            self._send_wechat(report)
        elif channel == "feishu":
            self._send_feishu(report)

    # ---- 渠道发送 ----

    def _send_email(self, report: TestReportModel):
        send_list = getattr(self.proj, "NOTICE_EMAIL_SEND_LIST", [])
        if not send_list:
            return
        EmailSend(
            EmailNoticeModel(
                send_user=SEND_USER,
                email_host=EMAIL_HOST,
                stamp_key=STAMP_KEY,
                send_list=send_list,
            ),
            test_report=report,
        ).send_main()

    def _send_wechat(self, report: TestReportModel):
        webhook = getattr(self.proj, "NOTICE_WECHAT_WEBHOOK", "")
        if not webhook:
            return
        WeChatSend(
            WeChatNoticeModel(webhook=webhook),
            test_report=report,
        ).send_wechat_notification()

    def _send_feishu(self, report: TestReportModel):
        webhook = getattr(self.proj, "NOTICE_FEISHU_WEBHOOK", "")
        if not webhook:
            return
        FeiShuSend(
            FeiShuNoticeModel(webhook=webhook),
            test_report=report,
        ).send_feishu_notification()

    # ---- 报告统计 ----

    def _get_case_count(self) -> TestReportModel | None:
        summary_path = (
            Path(project_dir.root_path()) / "report" / "html" / "widgets" / "summary.json"
        )
        if not summary_path.exists():
            return None

        with summary_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        statistic = data.get("statistic", {})
        time_info = data.get("time", {})
        total = statistic.get("total", 0)
        passed = statistic.get("passed", 0)
        failed = statistic.get("failed", 0)
        broken = statistic.get("broken", 0)
        skipped = statistic.get("skipped", 0)
        duration_seconds = round(time_info.get("duration", 0) / 1000, 2)

        return TestReportModel(
            project_name=self.project_display_name,
            test_environment=self.test_environment,
            case_sum=total,
            success=passed,
            success_rate=round((passed + skipped) / total * 100, 2) if total > 0 else 0.0,
            warning=broken,
            fail=failed,
            execution_duration=f"{duration_seconds}s",
            test_time=self._format_time(time_info.get("start"))
            if time_info.get("start") else "",
        )

    @staticmethod
    def _format_time(timestamp_ms: int) -> str:
        return datetime.fromtimestamp(timestamp_ms / 1000).strftime('%Y-%m-%d %H:%M:%S')
