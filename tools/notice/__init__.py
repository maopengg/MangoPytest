# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import json

from enums.tools_enum import StatusEnum, NoticeEnum
from models.tools_model import WeChatSendModel, EmailSendModel, EmailModel
from tools.allure_data.allure_report_data import AllureFileClean
from tools.database.sql_statement import sql_statement_1, sql_statement_2
from tools.database.sqlite_handler import SQLiteHandler
from tools.notice.send_mail import SendEmail
from tools.notice.wechat_send import WeChatSend


class SendNotice:

    def __init__(self, project_id: int, testing_environment: str):
        db_handler = SQLiteHandler()
        self.testing_environment = testing_environment
        self.project_list = db_handler.execute_sql(sql_statement_1, (project_id, StatusEnum.SUCCESS.value))
        if self.project_list:
            self.notice_list = db_handler.execute_sql(sql_statement_2, (project_id,))
        else:
            self.notice_list = []

    def notice_send(self):
        """
        发送通知
        @return:
        """
        allure_data = AllureFileClean().get_case_count()
        for notice in self.notice_list:
            if notice.get('type') == NoticeEnum.MAIL.value:
                email = EmailSendModel(
                    metrics=allure_data,
                    project=self.project_list[0].get('name'),
                    environment=self.testing_environment,
                    config=EmailModel(**json.loads(notice.get('config')))
                )
                SendEmail(email).send_main()
            elif notice.get('type') == NoticeEnum.WECOM.value:
                wechat = WeChatSendModel(
                    metrics=allure_data,
                    project=self.project_list[0].get('name'),
                    environment=self.testing_environment,
                    webhook=notice.get('config')
                )
                WeChatSend(wechat).send_wechat_notification()
