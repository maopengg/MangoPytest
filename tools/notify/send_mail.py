# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import smtplib
from email.mime.text import MIMEText

from models.tools_model import EmailSendModel
from tools.other_tools.allure_data.allure_report_data import AllureFileClean
from tools.read_files_tools.get_local_ip import get_host_ip


class SendEmail:
    """ 发送邮箱 """

    def __init__(self, email: EmailSendModel):
        self.email_data = email
        self.allure_data = AllureFileClean()
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    def send_mail(self, user_list: list, sub, content: str) -> None:
        """

        @param user_list: 发件人邮箱
        @param sub:
        @param content: 发送内容
        @return:
        """
        user = f"APIAutoTest <{self.email_data.config.send_user}>"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')  # 设置发送的内容
        message['Subject'] = sub  # 邮件的主题
        message['From'] = user  # 设置发送人
        message['To'] = ";".join(user_list)  # 设置收件人
        server = smtplib.SMTP()
        server.connect(self.email_data.config.email_host)
        server.login(self.email_data.config.send_user, self.email_data.config.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        执行异常邮件通知,调用之后发送邮寄
        @param error_message: 报错信息
        @return:
        """
        user_list = self.email_data.config.send_list

        sub = self.email_data.environment + "接口自动化执行异常通知"
        content = f"自动化测试执行完毕，程序中发现异常，请悉知。报错信息如下：\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self) -> None:
        """
        发送邮件
        :return:
        """
        user_list = self.email_data.config.send_list

        sub = f"<{self.email_data.project}项目{self.email_data.environment}环境>接口自动化报告"
        content = f"""
        各位同事, 大家好:
            自动化用例执行完成，执行结果如下:
            用例运行总数: {self.email_data.metrics.total} 个
            通过用例个数: {self.email_data.metrics.passed} 个
            失败用例个数: {self.email_data.metrics.failed} 个
            异常用例个数: {self.email_data.metrics.broken} 个
            跳过用例个数: {self.email_data.metrics.skipped} 个
            成  功   率: {self.email_data.metrics.pass_rate} %

        {self.allure_data.get_failed_cases_detail()}

        **********************************
        jenkins地址：http://61.183.9.60:808/login
        结果查看地址：http://{get_host_ip()}:9999/
        详细情况可登录jenkins平台查看，非相关负责人员可忽略此消息。谢谢。
        """
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_main()
