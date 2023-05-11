# -*- encoding: utf-8 -*-

import sys

from save_natgeo_data import *
from get_all_specific_natgeo import *


def download_all(url, username, password, database, data_table):
    """
    Func: 下载全部节目
    """
    # 获取所有节目的基本信息
    natgeo_sniffer = Sniffer(url)
    all_basic_info = natgeo_sniffer.get_all_episode_info()

    # 将所有节目的基本信息保存到数据库中
    natgeo_processor = DataProcess(username, password)

    # 如果存在同名的数据库，则删除重建；如果不存在，则直接创建
    natgeo_processor.delete_database(database)
    natgeo_processor.create_database(database)

    # 在数据库中创建数据表
    natgeo_processor.delete_data_table(database, data_table)
    natgeo_processor.create_data_table(database, data_table, create_database_sqls)

    # 保存基本信息到数据库指定的表中
    natgeo_sqls = insert_sqls(data_table, all_basic_info)
    natgeo_processor.modify_data(database, data_table, natgeo_sqls)

    # 下载所有节目
    get_files(all_basic_info)


def update_download(url, username, password, database, data_table):
    """
    Func: 只下载与之前相比还没有下载过的最新更新的节目
    """
    # 获取所有节目的基本信息
    natgeo_sniffer = Sniffer(url)
    all_basic_info = natgeo_sniffer.get_all_episode_info()

    # 将所有节目的基本信息保存到数据库中
    natgeo_processor = DataProcess(username, password)

    # 更新的节目信息
    new_basic_info = natgeo_processor.check_latest_issue(database, data_table, all_basic_info)

    if new_basic_info is None or len(new_basic_info) < 1:
        logger.warning('没有节目更新，无需处理！')
        return

    # 更新数据库，写入最新的节目信息
    new_natgeo_sqls = insert_sqls(data_table, new_basic_info)
    natgeo_processor.modify_data(database, data_table, new_natgeo_sqls)

    # 下载更新的节目
    get_files(new_basic_info)


def insert_sqls(table, data):
    """
    Func: 构造插入数据的SQL语句
    :param table: 保存数据的数据表
    :param data: 字典，保存需要插入的数据
    :return: 列表，保存构造好的sql语句
    """
    # NOTE:
    #  必须使用 pymysql.convener中的escape_str() 方法对字符串进行转换，否则字符串写入数据库时会报语法错误
    #  escape_string() 方法无效。escape_str() 在 escape_string()的基础上，再次嵌套了 一层引号，
    #  使其在与其他字符串合并时，仍能保持为独立的字符串

    # NOTE:
    #  def escape_str(value, mapping=None):
    #     return "'%s'" % escape_string(str(value), mapping)

    if not check_instance(table=table, data=data):
        return

    sqls = []
    for title, url in data.items():
        title = escape_str(title)
        url = escape_str(url)
        # NOTE: 通过MySQL中的 NOW() 函数获取当前的日期时间
        sql = f"INSERT INTO {table} (TITLE, URL, UPDATED_TIME) VALUES ({title}, {url}, NOW())"
        sqls.append(sql)

    return sqls


if __name__ == '__main__':
    logger = log_setting('Overheard_download', '../Logs')
    if logger is None:
        sys.exit()

    # Overheard 主页网址
    natgeo_homepage = "https://www.nationalgeographic.com/podcasts/overheard/"

    # 数据库基本信息
    database_info = {
        "user": "root",
        "password": "root",
        "host": "localhost",
        "port": 3306,
        "charset": "utf8mb4",
        "database": "overheard_db_20230508",
        'data_table': 'overheard_basic_data',
    }

    natgeo_user = database_info["user"]
    natgeo_passwd = database_info["password"]
    natgeo_db = database_info["database"]
    natgeo_dt = database_info["data_table"]

    # 创建数据表的SQL语句
    create_database_sqls = [f"DROP TABLE IF EXISTS `{database_info['data_table']}`;",
                            f"CREATE TABLE `{database_info['data_table']}` ( "
                            "`NUM` int NOT NULL AUTO_INCREMENT COMMENT '序号', "
                            "`TITLE` varchar(255) NOT NULL COMMENT '标题', "
                            "`URL` varchar(255) DEFAULT NULL COMMENT '链接', "
                            "`DOWNLOAD_STATUS` varchar(255) NOT NULL DEFAULT 'NO' COMMENT '下载状态',"
                            "`UPDATED_TIME` datetime DEFAULT NULL COMMENT '更新时间', "
                            "PRIMARY KEY ( `NUM`) "
                            ") "
                            "ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='所有节目的标题和链接';"
                            ]
    # 全量下载
    # download_all(natgeo_homepage, natgeo_user, natgeo_passwd, natgeo_db, natgeo_dt)

    # 增量下载
    update_download(natgeo_homepage, natgeo_user, natgeo_passwd, natgeo_db, natgeo_dt)
