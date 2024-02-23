import pymysql


class MysqlConnect:

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()

    def connect(self):
        self.connection = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database)

    def execute_query(self, sql):
        with self.connection.cursor() as cursor:
            cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
            result = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return result

    def close(self):
        if self.connection:
            self.connection.close()


# 使用示例
mysql = MysqlConnect("localhost", "username", "password", "database_name")
result1 = mysql.execute_query("SELECT * FROM your_table")
print(result1)
mysql.close()
