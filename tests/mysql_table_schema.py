#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL 数据库表结构查询工具
用于查询数据库中所有表及其建表语句
"""

import pymysql
import os
from typing import List, Tuple, Optional
from dataclasses import dataclass
from contextlib import contextmanager


@dataclass
class DBConfig:
    """数据库配置类"""
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = ""
    charset: str = "utf8mb4"


class MySQLSchemaExtractor:
    """MySQL 表结构提取器"""

    def __init__(self, config: DBConfig):
        self.config = config
        self.connection = None

    @contextmanager
    def _get_cursor(self):
        """获取数据库游标的上下文管理器"""
        try:
            self.connection = pymysql.connect(
                host=self.config.host,
                port=self.config.port,
                user=self.config.user,
                password=self.config.password,
                database=self.config.database,
                charset=self.config.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            cursor = self.connection.cursor()
            yield cursor
        except pymysql.Error as e:
            print(f"数据库连接错误: {e}")
            raise
        finally:
            if self.connection:
                self.connection.close()
                self.connection = None

    def get_all_tables(self) -> List[str]:
        """
        获取数据库中所有表名
        
        Returns:
            表名列表
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME
            """, (self.config.database,))
            return [row['TABLE_NAME'] for row in cursor.fetchall()]

    def get_create_table_sql(self, table_name: str) -> str:
        """
        获取指定表的建表语句
        
        Args:
            table_name: 表名
            
        Returns:
            建表 SQL 语句
        """
        with self._get_cursor() as cursor:
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            result = cursor.fetchone()
            return result['Create Table'] if result else ""

    def get_table_columns(self, table_name: str) -> List[dict]:
        """
        获取表的列信息
        
        Args:
            table_name: 表名
            
        Returns:
            列信息列表
        """
        with self._get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COLUMN_NAME,
                    DATA_TYPE,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION,
                    NUMERIC_SCALE,
                    IS_NULLABLE,
                    COLUMN_DEFAULT,
                    COLUMN_COMMENT,
                    EXTRA
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (self.config.database, table_name))
            return cursor.fetchall()

    def get_table_indexes(self, table_name: str) -> List[dict]:
        """
        获取表的索引信息
        
        Args:
            table_name: 表名
            
        Returns:
            索引信息列表
        """
        with self._get_cursor() as cursor:
            cursor.execute(f"SHOW INDEX FROM `{table_name}`")
            return cursor.fetchall()

    def export_all_schemas(self, output_file: Optional[str] = None) -> str:
        """
        导出所有表的建表语句
        
        Args:
            output_file: 输出文件路径，为 None 则返回字符串
            
        Returns:
            所有建表语句的字符串
        """
        tables = self.get_all_tables()
        
        lines = []
        lines.append("=" * 80)
        lines.append(f"数据库: {self.config.database}")
        lines.append(f"表数量: {len(tables)}")
        lines.append("=" * 80)
        lines.append("")

        for table_name in tables:
            lines.append("-" * 80)
            lines.append(f"表名: {table_name}")
            lines.append("-" * 80)
            lines.append("")
            
            # 建表语句
            create_sql = self.get_create_table_sql(table_name)
            lines.append(create_sql)
            lines.append(";")
            lines.append("")
            
            # 列信息
            columns = self.get_table_columns(table_name)
            lines.append("-- 列信息:")
            for col in columns:
                col_type = col['DATA_TYPE']
                if col['CHARACTER_MAXIMUM_LENGTH']:
                    col_type += f"({col['CHARACTER_MAXIMUM_LENGTH']})"
                elif col['NUMERIC_PRECISION']:
                    if col['NUMERIC_SCALE']:
                        col_type += f"({col['NUMERIC_PRECISION']},{col['NUMERIC_SCALE']})"
                    else:
                        col_type += f"({col['NUMERIC_PRECISION']})"
                
                nullable = "NULL" if col['IS_NULLABLE'] == 'YES' else "NOT NULL"
                default = f"DEFAULT {col['COLUMN_DEFAULT']}" if col['COLUMN_DEFAULT'] is not None else ""
                comment = f"COMMENT '{col['COLUMN_COMMENT']}'" if col['COLUMN_COMMENT'] else ""
                extra = col['EXTRA'] if col['EXTRA'] else ""
                
                lines.append(f"--   {col['COLUMN_NAME']:30} {col_type:20} {nullable:10} {default:20} {extra:20} {comment}")
            
            lines.append("")
            lines.append("")

        result = "\n".join(lines)

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(result)
            print(f"已导出到文件: {output_file}")

        return result


def main():
    """主函数示例"""
    # 配置数据库连接信息（请根据实际情况修改）
    config = DBConfig(
        host="mysql389bd1693b39.rds.ivolces.com",  # 数据库主机地址
        port=3306,                                   # 数据库端口
        user="test",                                 # 用户名
        password="84q9Q85uzXFtd5b",                  # 密码
        database="clm_test"                          # 数据库名
    )

    # 也可以从环境变量读取配置
    config.host = os.getenv("DB_HOST", config.host)
    config.port = int(os.getenv("DB_PORT", config.port))
    config.user = os.getenv("DB_USER", config.user)
    config.password = os.getenv("DB_PASSWORD", config.password)
    config.database = os.getenv("DB_NAME", config.database)

    try:
        extractor = MySQLSchemaExtractor(config)
        
        # 获取所有表
        print(f"正在查询数据库 '{config.database}' 中的所有表...")
        tables = extractor.get_all_tables()
        print(f"找到 {len(tables)} 个表:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table}")
        print()

        # 导出所有建表语句
        output_file = f"{config.database}_schema.sql"
        extractor.export_all_schemas(output_file)
        
        # 也可以只查看单个表的建表语句
        # if tables:
        #     print(f"\n表 '{tables[0]}' 的建表语句:")
        #     print(extractor.get_create_table_sql(tables[0]))

    except Exception as e:
        print(f"执行出错: {e}")


if __name__ == "__main__":
    main()
