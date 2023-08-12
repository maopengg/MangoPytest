# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description:
# @Time   : 2023-03-07 8:24
# @Author : 毛鹏
import socket


def get_host_ip():
    """
    查询本机ip地址
    :return:
    """
    # 获取主机名
    hostname = socket.gethostname()
    # 获取主机的IP地址
    ip_address = socket.gethostbyname(hostname)
    return ip_address


if __name__ == '__main__':
    print(get_host_ip())
