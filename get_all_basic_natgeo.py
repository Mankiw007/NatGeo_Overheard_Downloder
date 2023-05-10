# -*- encoding: utf-8 -*-

import os
import re

import requests
from lxml import etree

from log_overheard import log_setting


class Sniffer:
    def __init__(self, url):
        self.url = url
        self.raw_html = '../HTMLs/overheard.html'

    def __get_html(self):
        """
        Func: 获取Overheard主页信息，并将其保存为HTML格式
        Return: boolean - 获取成功则返回True，获取失败返回False
        """
        try:
            logger.info('开始请求Overheard主页，并将其内容保存到HTML文件中 ... ')
            r = requests.get(self.url)
            with open(self.raw_html, 'w', encoding='utf-8') as f:
                f.write(r.text)
            logger.info(f'Overheard主页的HTML文件【{self.raw_html}】保存完成。\n')
            return True
        except Exception as e:
            logger.error(f'Overheard主页请求失败，请检查：{e}。\n')
            return False

    def get_all_episode_info(self):
        """
        Func: 获取Overheard主页上所有节目的信息
        Return: 一个保存每期节目标题和对应网址的字典
        """
        # 判断 Overheard主页的HTML文件是否存在
        if self.__get_html():
            if not os.path.exists(self.raw_html):
                logger.error(f'Overheard主页的HTML文件【{self.raw_html}】不存在，请检查。\n')
                return False
        else:
            return False

        # 开始处理HTML文件
        try:
            logger.info('开始获取 Overheard主页上所有节目的信息 ... ')
            html = etree.parse(self.raw_html, etree.HTMLParser())

            # 最新一期的标题和链接
            latest_title = html.xpath('//a[@class="AnchorLink PromoTile__Link"]//text()')
            latest_url = html.xpath('//a[@class="AnchorLink PromoTile__Link"]//@href')

            # 往期的标题和链接
            titles = html.xpath('//a[@class="AnchorLink RegularStandardPrismTile__ContentLink"]//text()')
            urls = html.xpath('//a[@class="AnchorLink RegularStandardPrismTile__ContentLink"]//@href')

            # 使用 '_' 来替换掉标题中的特殊字符（[\/:*?<>|]），否则会干扰文件命名
            fine_titles = []
            special_str = r'[:/\\*?<>|]'
            for item in latest_title + titles:
                fine_titles.append(re.sub(special_str, "_", item))

            # 将所有标题和对应的链接合并到一个字典内
            issue_info = dict(zip(fine_titles, latest_url + urls))
            logger.info('获取所有节目信息完成。\n')

            return issue_info
        except Exception as e:
            logger.error(f'获取 Overheard主页上的节目信息出现错误，请检查：{e}\n')
            return False


logger = log_setting('Overheard_get_basic', '../Logs')


if __name__ == '__main__':
    pass
    website = "https://www.nationalgeographic.com/podcasts/overheard/"
    sniffer = Sniffer(website)
    sniffer.get_all_episode_info()
