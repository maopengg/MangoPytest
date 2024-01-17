# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2024-01-17 10:50
# @Author : 毛鹏
# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-08-12 17:40
# @Author : 毛鹏
import json

from auto_test.project_enum import ProjectEnum
from config.config import AUTO_TEST_MYSQL_DB
from enums.tools_enum import NotificationType
from models.tools_model import WeChatSendModel, EmailSendModel, EmailModel, ProjectRunModel
from tools.allure_data.allure_report_data import AllureFileClean
from tools.database.mysql_control import MySQLHelper
from tools.notice.send_mail import SendEmail
from tools.notice.wechat_send import WeChatSend

TEST_PROJECT_MYSQL: MySQLHelper = MySQLHelper(AUTO_TEST_MYSQL_DB)


def notify_send(data: ProjectRunModel):
    """
    是否发送通知
    @param data: 执行测试用例的项目
    @return:
    """
    for project_obj in data.list_run:
        project = project_obj.project
        environment = project_obj.testing_environment
        sql = f'SELECT is_notify,notify_type_list FROM aigc_AutoTestPlatform.project_config WHERE project_name="{project}" AND project_te = "{environment}";'
        if project == ProjectEnum.AIGC.value:
            query = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            if query.get('is_notify') == 0:
                send(project, environment, eval(query.get('notify_type_list')))
        elif project == ProjectEnum.CDP.value:
            query = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            if query.get('is_notify') == 0:
                send(project, environment, eval(query.get('notify_type_list')))
    TEST_PROJECT_MYSQL.close()


def send(project_name, project_te, notify_type_list):
    """
    实际发送通知
    @param project_name: 项目名称
    @param project_te:测试环境
    @param notify_type_list: 发送的list
    @return:
    """
    allure_data = AllureFileClean().get_case_count()
    sql = f'SELECT * FROM aigc_AutoTestPlatform.notify_config WHERE project_name="{project_name}";'
    query: list[dict] = TEST_PROJECT_MYSQL.execute_query(sql)
    email_config = json.loads([i for i in query if i.get('type') == 0][0].get('config'))
    email = EmailSendModel(metrics=allure_data,
                           project=project_name,
                           environment=project_te,
                           config=EmailModel(**email_config)
                           )
    wechat = WeChatSendModel(metrics=allure_data,
                             project=project_name,
                             environment=project_te,
                             webhook=json.loads([i for i in query if i.get('type') == 1][0]['config'])['webhook'],
                             tester_name='毛鹏'
                             )
    notification_mapping = {
        NotificationType.WECHAT.value: WeChatSend(wechat).send_wechat_notification,
        NotificationType.EMAIL.value: SendEmail(email).send_main}
    for i in notify_type_list:
        notification_mapping.get(i)()
    # if test_environment.excel_report:
    #     ErrorCaseExcel().write_case()
