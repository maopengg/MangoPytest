# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 
# @Time   : 2023-08-12 17:40
# @Author : 毛鹏
from enums.tools_enum import NotificationType, ProjectEnum
from models.tools_model import MysqlDBModel, WeChatSendModel, EmailSendModel
from tools.mysql_tool.mysql_control import MySQLHelper
from tools.notify.send_mail import SendEmail
from tools.notify.wechat_send import WeChatSend
from tools.other_tools.allure_data.allure_report_data import AllureFileClean

TEST_PROJECT_MYSQL: MySQLHelper = MySQLHelper(
    MysqlDBModel(host='61.183.9.60', port=23306, user='root', password='zALL_mysql1', database='aigc_AutoTestPlatform'))


def notify_send(data: list[dict]):
    """
    是否发送通知
    @param data:
    @return:
    """
    for project_obj in data:
        project = project_obj.get('project')
        environment = project_obj.get('testing_environment')
        sql = f'SELECT is_notify,notify_type_list FROM aigc_AutoTestPlatform.project_config WHERE project_name="{project}" AND project_te = "{environment}";'
        if project == ProjectEnum.AIGC.value:
            query = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            if query.get('is_notify') == 0:
                send(project, environment, query.get('notify_type_list'))
        elif project == ProjectEnum.CDXP.value:
            query = TEST_PROJECT_MYSQL.execute_query(sql)[0]
            if query.get('is_notify') == 0:
                send(project, environment, query.get('notify_type_list'))
    TEST_PROJECT_MYSQL.close()


def send(project_name, project_te, notify_type_list):
    """
    实际发送通知
    @param project_name:
    @param project_te:
    @param notify_type_list:
    @return:
    """
    allure_data = AllureFileClean().get_case_count()
    sql = f'SELECT * FROM aigc_AutoTestPlatform.notify_config WHERE project_name="{project_name}";'
    query: list[dict] = TEST_PROJECT_MYSQL.execute_query(sql)
    email = EmailSendModel(metrics=allure_data,
                           project=project_name,
                           environment=project_te,
                           config=[i for i in query if i.get('type') == 0][0].get('config'))
    wechat = WeChatSendModel(metrics=allure_data,
                             project=project_name,
                             environment=project_te,
                             webhook=[i for i in query if i.get('type') == 1][0].get('config'),
                             tester_name='毛鹏')
    notification_mapping = {
        NotificationType.WECHAT.value: WeChatSend(wechat).send_wechat_notification,
        NotificationType.EMAIL.value: SendEmail(email).send_main}
    for i in notify_type_list:
        notification_mapping.get(i)()
    # if test_environment.excel_report:
    #     ErrorCaseExcel().write_case()
