import pymysql
from pymysql import Error

# 数据库连接配置
config = {
    'host': 'rm-2zegst7f44n183i51ho.mysql.rds.aliyuncs.com',
    'port': 3306,
    'user': 'u_integration_test_writer',
    'password': '6JJFkKw45*Q5o^ejKgxX40OhQsvG!',
    'database': 'u_integration_test',
    'charset': 'utf8'
}


def get_all_tables():
    """查询数据库中的所有表"""
    connection = None
    try:
        # 建立数据库连接
        connection = pymysql.connect(**config)
        print("成功连接到数据库！")

        with connection.cursor() as cursor:
            # 查询所有表名
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()

            if not tables:
                print("数据库中暂无任何表。")
                return []

            print(f"\n共找到 {len(tables)} 个表：")
            print("-" * 50)
            for i, table in enumerate(tables, 1):
                print(f"{i}. {table[0]}")

            return [table[0] for table in tables]

    except Error as e:
        print(f"数据库连接或查询失败：{e}")
        return []
    finally:
        if connection:
            connection.close()
            print("\n数据库连接已关闭。")


def query_table_data(table_name, limit=5):
    """查询指定表的前几条数据（可选功能）"""
    connection = None
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit};")
            data = cursor.fetchall()

            # 获取列名
            cursor.execute(f"DESCRIBE `{table_name}`;")
            columns = [col[0] for col in cursor.fetchall()]

            return columns, data
    except Error as e:
        print(f"查询表 {table_name} 数据失败：{e}")
        return [], []
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    # 查询所有表
    tables = get_all_tables()

    # 可选：打印每个表的前几条数据示例
    if tables:
        print("\n是否查看表的详细数据？(y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            for table in tables:
                print(f"\n{'=' * 50}")
                print(f"表名：{table}")
                print('=' * 50)
                columns, data = query_table_data(table, limit=3)
                if columns:
                    print("列名：", ", ".join(columns))
                    if data:
                        print("数据示例（前3行）：")
                        for row in data:
                            print(row)
                    else:
                        print("该表无数据。")
                print()