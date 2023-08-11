# -*- coding: utf-8 -*-
# @Project: auto_test
# @Description: 随机数据封装
# @Time   : 2022-11-04 22:05
# @Author : 毛鹏
import random
import time
from datetime import date, timedelta, datetime

from faker import Faker


class RandomTool:
    """随机数据类"""
    faker = Faker(locale='zh_CN')

    @classmethod
    def random_regular(cls, func: str) -> str:
        """ 不包含 """
        func = func.strip()
        func = func.replace("()", "")
        return getattr(cls, func)()

    @staticmethod
    def random_time_random() -> str:
        """获取基于当前时间戳的随机五位数"""
        s = int(time.time())
        s = str(s)
        return s[5:len(s)]

    @staticmethod
    def random_random_0_9() -> int:
        """0-9的随机数"""
        _data = random.randint(0, 9)
        return _data

    @staticmethod
    def random_10_99() -> int:
        """10-99的随机数"""
        _data = random.randint(10, 99)
        return _data

    @staticmethod
    def random_100_999() -> int:
        """100-999的随机数"""
        _data = random.randint(100, 999)
        return _data

    @staticmethod
    def random_0_5000() -> int:
        """0-5000的随机数"""
        _data = random.randint(0, 5000)
        return _data

    @staticmethod
    def random_int():
        """小数"""
        return random.random()

    @staticmethod
    def random_goods_name() -> str:
        """不带随机数的商品名称"""
        goods = ["清洁霜", "洗面奶", "浴剂", "洗发护发剂", "剃须膏", "面霜", "蜜", "化妆水", "面膜", "发乳", "发胶", "胭脂", "口红", "眼影", "清凉剂", "除臭剂",
                 "育毛剂", "除毛剂", "染毛剂", "驱虫剂", "橄榄精华", "洗面乳", "浴液", "洗发液", "化妆水", "香水", "洁肤水", "卸妆液", "精华液", "原液", "蜜类",
                 "护发乳", "精华乳", "润面霜", "粉底霜", "洗发膏", "遮瑕膏", "炯发膏", "精华霜", "妆前霜", "香粉", "爽身粉", "散粉", "洁肤粉", "蜜粉", "粉饼",
                 "化妆盒", "发蜡", "卸妆油", "润肤油", "润发油", "精华油", "香水", "古龙水", "面霜", "护手霜", "眼影", "防晒霜", "隔离霜", "腮红", "BB霜",
                 "沐浴露",
                 "洗发水", "洗面奶", "发胶", "剃须膏", "洁肤", "乳液", "面霜", "精华", "隔离", "防晒", "粉底", "遮瑕膏", "眉笔", "眉粉", "睫毛膏",
                 "眼线笔", "眼影", "腮红", "眼霜", "隔离液", "遮瑕膏", "防晒液", "粉底液（自然）", "粉条", "散粉", "粉饼", "打高光的粉", "眼影", "眼部亮粉", "腮红",
                 "润唇膏", "唇蜜", "唇膏", "唇笔", "唇彩", "眉笔", "眉粉", "眼线笔", "睫毛膏", "指甲油", "眼唇部卸妆油", "脸部卸妆油", "洗甲油"]
        return goods[random.randint(0, 104)]

    @staticmethod
    def random_goods_name_int() -> str:
        """带随机数的商品名称"""
        goods = ["清洁霜", "洗面奶", "浴剂", "润发油", "洗发护发剂", "剃须膏", "面霜", "蜜", "化妆水", "面膜", "发乳", "发胶", "胭脂", "口红", "眼影", "清凉剂",
                 "除臭剂",
                 "育毛剂", "除毛剂", "染毛剂", "驱虫剂", "橄榄精华", "洗面乳", "浴液", "洗发液", "化妆水", "香水", "洁肤水", "卸妆液", "精华液", "原液", "蜜类",
                 "护发乳", "精华乳", "润面霜", "粉底霜", "洗发膏", "遮瑕膏", "炯发膏", "精华霜", "妆前霜", "香粉", "爽身粉", "散粉", "洁肤粉", "蜜粉", "粉饼",
                 "化妆盒", "发蜡", "卸妆油", "润肤油", "精华油", "香水", "古龙水", "面霜", "护手霜", "眼影", "防晒霜", "隔离霜", "腮红", "BB霜",
                 "沐浴露",
                 "洗发水", "洗面奶", "发胶", "剃须膏", "洁肤", "乳液", "面霜", "精华", "隔离", "防晒", "粉底", "遮瑕膏", "眉笔", "眉粉", "睫毛膏",
                 "眼线笔", "眼影", "腮红", "眼霜", "隔离液", "遮瑕膏", "防晒液", "粉底液（自然）", "粉条", "散粉", "粉饼", "打高光的粉", "眼影", "眼部亮粉", "腮红",
                 "润唇膏", "唇蜜", "唇膏", "唇笔", "唇彩", "眉笔", "眉粉", "眼线笔", "睫毛膏", "指甲油", "眼唇部卸妆油", "脸部卸妆油", "洗甲油"]
        return goods[random.randint(0, 104)] + str(random.randint(0, 1000))

    @classmethod
    def random_get_phone(cls) -> int:
        """随机生成手机号码"""
        phone = cls.faker.phone_number()
        return phone

    @classmethod
    def random_get_id_number(cls) -> int:
        """随机生成身份证号码"""

        id_number = cls.faker.ssn()
        return id_number

    @classmethod
    def random_get_female_name(cls) -> str:
        """女生姓名"""
        female_name = cls.faker.name_female()
        return female_name

    @classmethod
    def random_get_male_name(cls) -> str:
        """男生姓名"""
        male_name = cls.faker.name_male()
        return male_name

    @classmethod
    def random_get_simple_profile(cls) -> str:
        """获取简单的人物信息"""
        res = cls.faker.simple_profile()
        return str(res)

    @classmethod
    def random_get_profile(cls) -> str:
        """获取带公司的人物信息"""
        res = cls.faker.profile()
        return str(res)

    @classmethod
    def random_get_email(cls) -> str:
        """生成邮箱"""
        email = cls.faker.email()
        return email

    @classmethod
    def random_get_bank_card(cls) -> str:
        """银行卡"""
        return cls.faker.credit_card_number()

    @classmethod
    def random_get_address(cls) -> str:
        """带邮政编码的地址"""
        return cls.faker.address()

    @classmethod
    def random_get_job(cls) -> str:
        """获取职称"""
        return cls.faker.job()

    @classmethod
    def random_get_company(cls) -> str:
        """获取公司名称"""
        return cls.faker.company()

    @classmethod
    def random_get_city(cls) -> str:
        """获取城市"""
        return cls.faker.city()

    @classmethod
    def random_get_country(cls) -> str:
        """获取国家"""
        return cls.faker.country()

    @classmethod
    def random_get_province(cls) -> str:
        """获取国家"""
        return cls.faker.province()

    @classmethod
    def random_get_pystr(cls) -> str:
        """生成英文的字符串"""
        return cls.faker.pystr()

    @classmethod
    def random_get_word(cls) -> str:
        """生成词语"""
        return cls.faker.word()

    @classmethod
    def random_get_text(cls) -> str:
        """生成一篇文章"""
        return cls.faker.text()

    @classmethod
    def random_get_year(cls) -> str:
        """获取年份"""
        return cls.faker.year()

    @classmethod
    def random_get_month(cls) -> str:
        """获取月份"""
        return cls.faker.month()

    @classmethod
    def random_get_date(cls) -> str:
        """获取日期"""
        return cls.faker.date()

    @classmethod
    def random_get_date_this_year(cls) -> str:
        """获取当前年份:年月日"""
        return cls.faker.date_this_year()

    @classmethod
    def random_get_date_time(cls) -> str:
        """获取：年月日时分秒"""
        return cls.faker.date_time()

    @classmethod
    def random_get_future_datetime(cls) -> str:
        """获取未来时间，年月日 时分秒"""
        return cls.faker.future_datetime()

    @classmethod
    def random_get_future_date(cls) -> str:
        """获取未来时间 年月日"""
        return cls.faker.future_date()

    @classmethod
    def random_get_deta_hms(cls) -> str:
        """获取时分秒"""
        now_time = datetime.now().strftime("%H%M%S")
        return now_time

    @classmethod
    def random_get_time(cls) -> str:
        """计算当前时间"""
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    @classmethod
    def random_today_date(cls) -> str:
        """获取今日0点整时间"""

        _today = date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def random_time_after_week(cls) -> str:
        """获取一周后12点整的时间"""

        _time_after_week = (date.today() + timedelta(days=+6)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week

    @classmethod
    def random_time_after_month(cls) -> str:
        """获取30天后的12点整时间"""

        _time_after_week = (date.today() + timedelta(days=+30)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week
