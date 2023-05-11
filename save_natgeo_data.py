# -*- encoding: utf-8 -*-

import re

import pymysql
from pymysql.converters import escape_str

from log_overheard import log_setting


def check_instance(database='1', table='1', sqls=False, data=False):
    """
    Func: 用来检查用户传入的参数是否合法
    :param database: 数据库的名称
    :param table: 数据表的名称
    :param sqls: 列表，包含用户提供的sql语句
    :param data: 字典，包含节目信息
    :return: 当提供的某个参数不合法时，返回False；提供的参数全部合法时，返回True; 没提供某个参数，则返回结果和该参数无关
    """
    if data is False:
        data = {1: True}
    if sqls is False:
        sqls = [1]

    status = []

    if database is None:
        pass
    elif not isinstance(database, str) or len(database) < 1:
        logger.critical(f"输入的数据库名称【{database}】不是非空字符串，请检查！")
        status.append(False)
    elif re.match(r'[:/\\*?<>\]\[|]', database):
        logger.critical(f"输入的数据库名称【{database}】中含有非法字符，请检查！")
        status.append(False)

    if not isinstance(table, str) or len(table) < 1:
        logger.critical(f"输入的数据表名称【{table}】不是非空字符串，请检查！")
        status.append(False)
    elif re.match(r'[:/\\*?<>\]\[|]', table):
        logger.critical(f"输入的数据库名称【{table}】中含有非法字符，请检查！")
        status.append(False)

    if not isinstance(sqls, list) or len(sqls) < 1:
        logger.error(f'提供的SQL语句不是非空列表的形式，请检查！')
        status.append(False)

    if not isinstance(data, dict) or len(data) < 1:
        logger.critical(f"提供的待检测的数据不是非空字典形式，请检查！")
        status.append(False)

    if False in status:
        return False
    else:
        return True


class DataProcess(object):
    def __init__(self, username, password, host='localhost', port=3306, charset='utf8mb4'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.charset = charset

    def __create_conn(self, database=None):
        """
        Func：创建数据库的连接
        :param database: 要连接的数据库，默认为None，即不指定具体的数据库名称
        :return: 数据库连接
        """
        if not check_instance(database=database):
            return

        try:
            conn = pymysql.connect(user=self.username, password=self.password, host=self.host, port=self.port,
                                   database=database, autocommit=True)
            return conn
        except Exception as e:
            logger.critical(f'连接数据库服务出现异常，请检查！')
            logger.error(e)

    def is_database_exist(self, database):
        """
        Func: 检查某个数据库是否存在
        :param database: 需要检查的数据量名称
        :return: 如果存在，则返回Ture；不存在，则返回False；其余情况，返回None
        """
        if not check_instance(database=database):
            return

        conn = self.__create_conn()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'select * from information_schema.SCHEMATA where SCHEMA_NAME = {escape_str(database)};')
                if cursor.fetchall():
                    logger.info(f'数据库【{database}】存在。')
                    return True
                else:
                    logger.warning(f'数据库【{database}】不存在。')
                    return False
            except Exception as e:
                logger.critical(f'检查数据库【{database}】出现异常！')
                logger.error(e)
            finally:
                cursor.close()
                conn.close()

    def is_data_table_exist(self, database, table):
        """
        Func: 检查某张数据表是否存在于某个数据库中
        :param database: 要查找的数据库名称
        :param table: 要查找的数据表名称
        :return: 如果存在，则返回Ture；不存在，则返回False；其余情况，返回None
        """
        if not check_instance(database=database, table=table):
            return

        conn = self.__create_conn()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    f'select * from information_schema.TABLES '
                    f'where TABLE_SCHEMA = {escape_str(database)} and TABLE_NAME = {escape_str(table)};')
                if cursor.fetchall():
                    logger.info(f'数据表【{table}】存在。')
                    return True
                else:
                    logger.warning(f'数据表【{table}】不存在。')
                    return False
            except Exception as e:
                logger.critical(f'检查数据表【{table}】出现异常！')
                logger.error(e)
            finally:
                cursor.close()
                conn.close()

    def create_database(self, database):
        """
        Func: 创建数据库
        :param database: 指定的数据库名称
        :return: 创建成功，则返回Ture；创建失败，则返回False；其余情况，返回None
        """
        if not check_instance(database=database):
            return

        if self.is_database_exist(database):
            return

        conn = self.__create_conn()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(f'CREATE DATABASE {database};')
                logger.info(f'数据库【{database}】创建完成。\n')
                return True
            except Exception as e:
                logger.critical(f'数据库创建出现异常，请检查！\n')
                logger.error(e)
                return False
            finally:
                cursor.close()
                conn.close()

    def delete_database(self, database):
        """
        Func: 删除指定的数据库
        :param database: 指定的数据库名称
        :return: 删除成功，则返回Ture；删除失败，则返回False；其余情况，返回None
        """
        if not check_instance(database=database):
            return

        if not self.is_database_exist(database):
            return

        conn = self.__create_conn()
        if conn:
            cursor = conn.cursor()
            try:
                logger.info(f'开始删除数据库【{database}】 ... ')
                cursor.execute(f'DROP DATABASE IF EXISTS {database};')
                logger.info(f'数据库【{database}】删除完成。\n')
                return True
            except Exception as e:
                logger.critical(f'数据库删除出现异常，请检查！\n')
                logger.error(e)
                return False
            finally:
                cursor.close()
                conn.close()

    def create_data_table(self, database, table, sqls):
        """
        Func: 在指定的数据库中创建数据表
        :param database: 指定的数据库
        :param table: 指定的数据表
        :param sqls: 一个列表，保存用来创建数据表的sql语句
        :return: 创建成功，则返回Ture；创建失败，则返回False；其余情况，返回None
        """
        if not check_instance(database=database, table=table, sqls=sqls):
            return

        if self.is_data_table_exist(database, table):
            return

        conn = self.__create_conn(database)
        if conn:
            cursor = conn.cursor()
            try:
                logger.info(f"开始在数据库【{database}】创建数据表【{table}】... ")
                for sql in sqls:
                    cursor.execute(sql)
                logger.info(f"数据表【{table}】创建完成。\n")
                return True
            except Exception as e:
                logger.critical(f"数据表【{table}】创建失败，请检查！\n")
                logger.error(e)
                logger.info(f'开始回滚数据库【{database}】... ')
                conn.rollback()
                logger.info(f'回滚数据库【{database}】完成。\n')
                return False
            finally:
                cursor.close()
                conn.close()

    def delete_data_table(self, database, table):
        """
        Func: 删除数据库中的数据表
        :param database: 指定的数据库
        :param table: 指定的数据表
        :return: 删除成功，则返回Ture；删除失败，则返回False；其余情况，返回None
        """
        if not check_instance(database=database, table=table):
            return

        if not self.is_data_table_exist(database, table):
            return

        conn = self.__create_conn(database)
        if conn:
            cursor = conn.cursor()
            try:
                logger.info(f'开始删除数据表【{table}】 ... ')
                cursor.execute(f'drop table {table};')
                logger.info(f'数据表【{table}】删除完成。\n')
                return True
            except Exception as e:
                logger.critical(f'数据表删除出现异常，请检查！\n')
                logger.error(e)
                return False
            finally:
                cursor.close()
                conn.close()

    def modify_data(self, database, table, sqls):
        """
        Func: 修改指定数据库中指定数据表中的数据
        :param database: 指定的数据库
        :param table: 指定的数据表
        :param sqls: 列表，保存用的sql语句
        :return: 修改成功，则返回Ture；修改失败，则返回False；其余情况，返回None
        """
        if not check_instance(database=database, table=table, sqls=sqls):
            return

        if not self.is_database_exist(database):
            return

        if not self.is_data_table_exist(database, table):
            return

        conn = self.__create_conn(database)
        if conn:
            cursor = conn.cursor()
            try:
                logger.info(f'开始写入节目的基本信息 ... ')
                for sql in sqls:
                    cursor.execute(sql)
                # conn.commit()  # 数据库连接设置已经设置为自动提交
                logger.info(f'节目的基本信息已经全部写入数据表【{table}】中。\n')
                return True
            except Exception as e:
                logger.critical(f'写入基本信息时出现异常，请检查！\n')
                logger.error(e)
                logger.warning(f'开始回滚数据库【{database}】... ')
                conn.rollback()
                logger.warning(f'回滚数据库【{database}】完成。\n')
                return False
            finally:
                cursor.close()
                conn.close()

    def check_latest_issue(self, database, table, data):
        """
        Func: 检查用户提供的最新的节目信息中，哪些没有保存到指定的数据表中
        :param database: 指定的数据库
        :param table: 指定的数据表
        :param data: 字典，保存最新的全部节目的基本信息，key 是节目标题，value 是节目的网址
        :return: 字典，保存那些还未保存到数据库中的节目信息
        """
        if not check_instance(database=database, table=table, data=data):
            return

        if not self.is_database_exist(database):
            return

        if not self.is_data_table_exist(database, table):
            return

        conn = self.__create_conn(database)
        if conn:
            cursor = conn.cursor()
            try:
                logger.info(f'开始对比提供的节目信息和数据库中已有的节目信息 ... ')
                # 用来保存数据库中没有的节目信息
                latest_issue = {}

                # 查询每条信息是否已经在数据库的表中
                for title, url in data.items():
                    # title = escape_str(title)
                    cursor.execute(f"select 1 from {table} where title = {escape_str(title)} limit 1; ")
                    num = cursor.fetchall()     # 返回值为一个元组
                    if len(num) == 0:
                        logger.warning(f"节目【{title}】在数据库中没有保存。\n")
                        latest_issue[title] = url

                return latest_issue
            except Exception as e:
                logger.error('对比信息时出现异常，请检查！\n')
                logger.error(e)
            finally:
                cursor.close()
                conn.close()


logger = log_setting('Overheard_database', '../Logs')


if __name__ == "__main__":
    # 保存数据的数据库基本参数
    config = {
        "user": "root",
        "password": "root",
        "host": "localhost",
        "port": 3306,
        "database": "overheard_db",
        "data_table": "overheard_basic_data",
        "charset": "utf8mb4",
    }

    # 使用的数据库名称
    overheard_database = config['database']

    # 保存数据的数据表名称
    overheard_basic_data_table = config['data_table']

    # 实例化一个数据处理器
    processor = DataProcess(username=config['user'], password=config['password'])
    processor.is_database_exist(overheard_database)
