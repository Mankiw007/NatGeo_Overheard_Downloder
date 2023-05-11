# -*- encoding: utf-8 -*-

import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from get_all_basic_natgeo import *
from log_overheard import log_setting


class Downloader:
    def __init__(self, title, url, save_path=None):
        title = re.sub(r'[:/\\*?<>\]\[|]', "_", title)      # 使用 _ 替换掉标题中的 特殊字符
        self.title = title
        self.url = url
        self.save_path = save_path
        self.__publish_date = None
        self.__raw_html = f'../HTMLs/{title}.html'
        self.__text = title + '.txt'
        self.__picture = title + '.jpg'
        self.__picture_info = title + '_picture_info.txt'
        self.__audio = title + '.mp3'
        self.__audio_info = title + '_audio_info.txt'

    def __request_url(self):
        """
        Func: 获取网址的html文件；最多尝试访问两次
        Return: html文件的路径；如果获取失败，则默认返回 None
        """
        for i in range(2):
            try:
                logger.info(f'开始请求网址 {self.url} ... ')
                result = requests.get(self.url)

                if result.status_code == 200:
                    with open(self.__raw_html, 'w', encoding='utf-8') as f:
                        f.write(result.text)

                    logger.info(f'网页的html文件【{self.__raw_html}】保存完成。\n')
                    return self.__raw_html
                else:
                    logger.error(f'网址请求异常，返回码为【{result.status_code}】，请检查！\n')
            except Exception as e:
                logger.error(f'网址请求出现错误，请检查：{e}\n')

    def __get_publish_date(self):
        """
        Func: 获取节目的发布日期。如果获取出现异常，则使用当前日期作为发布日期
        """
        try:
            logger.info('开始获取节目的发布日期 ... ')
            html = etree.parse(self.__raw_html, etree.HTMLParser())
            publish_info = html.xpath('//div[@class="Byline__Meta Byline__Meta--publishDate"]//text()')
            date_info = publish_info[0].replace('Published ', '')

            # 将英文格式(March 20, 2023)的日期 修改为 数字格式(2023-03-20)，方便后续使用该信息
            time_format = datetime.datetime.strptime(date_info, '%B %d, %Y')
            self.__publish_date = datetime.datetime.strftime(time_format, '%Y-%m-%d')
            logger.info(f'节目的发布日期为【{self.__publish_date}】\n ')
        except Exception as e:
            logger.error(f'获取发布日期出现异常，请检查：{e}\n')
            self.__publish_date = datetime.date.today().strftime('%Y-%m-%d')
            logger.warning(f'使用当前日期【{self.__publish_date}】作为发布日期！')

    def __get_save_path(self):
        """
        Func:
        如果用户指定了路径，则使用指定的的路径；
        如果没有提供，则根据发布日期构造保存路径；
        如果构造失败，则使用当前路径。
        """
        if not self.save_path:
            logger.info('开始获取保存文件的各级目录 ... ')
            basic_path = r'D:\National Geographic\Overheard'

            try:
                date_list = self.__publish_date.split('-')
                first_dir = date_list[0]
                second_dir = date_list[1]
                self.save_path = '\\'.join([basic_path, first_dir, second_dir])

                # 判断路径是否存在，不存在 则依次创建
                if not os.path.exists(self.save_path):
                    os.makedirs(self.save_path)

                logger.info(f'保存文件的目录为【{self.save_path}】\n')
            except Exception as e:
                logger.error(f'获取文件保存路径出现异常，请检查：{e}')
                self.save_path = os.getcwd()
                logger.warning(f'使用当前目录【{self.save_path}】保存文件。\n')
        else:
            if os.path.exists(self.save_path):
                logger.info(f'使用提供的路径【{self.save_path}】保存文件。\n')
            else:
                self.save_path = os.getcwd()
                logger.warning(f'提供的路径不存【{self.save_path}】不存在。\n')
                logger.warning(f'使用当前目录【{self.save_path}】保存文件。\n')

    def __get_text(self):
        """
        Func: 获取指定网页上的文本。不对外开放，如果用户需要下载某一期的文本，请调用 get_only_text()
        """
        try:
            logger.info('开始获取标题描述和文章简介 ... ')
            html = etree.parse(self.__raw_html, etree.HTMLParser())
            title_desc = html.xpath('//p[@class="Article__Headline__Desc"]//text()')
            preface = html.xpath('//section[@class="Article__Content"]/div[1]/p[1]//text()')

            logger.info('开始保存标题描述和文章简介 ... ')
            # 依次写入 链接、标题、作者、标题描述、文章简介
            with open('\\'.join([self.save_path, self.__text]), 'w', encoding='utf-8') as f:
                f.write(self.url + '\n\n')
                f.write(self.title + '\n\n')
                f.write('Nat Geo' + '\n\n')
                f.write('【标题描述】' + '\n')
                for item in title_desc:
                    f.write(item.replace("’", "'").replace('“', '"').replace('”', '"'))
                f.write('\n\n')

                f.write('【文章简介】')
                for item in preface:
                    f.write(item.replace("’", "'").replace('“', '"').replace('”', '"'))
                f.write('\n\n')

            logger.info('开始获取正文 ... ')
            # 从第2个<p>开始算是正文
            body_text = html.xpath('//section[@class="Article__Content"]//div[1]//p')[2:]

            keyword1 = 'SHOW NOTES'
            keyword2 = 'SHOWNOTES'
            keyword3 = 'Show Notes'
            keyword4 = 'Want more'

            logger.info('开始保存正文 ... ')
            with open('\\'.join([self.save_path, self.__text]), 'a', encoding='utf-8') as f:
                f.write('【TRANSCRIPT】')
                for item in body_text:
                    # item.xpath('string(.)') 获取每个节点的文本，并将其转换为字符串
                    text = str(item.xpath('string(.)')).replace("’", "'").replace('“', '"').replace('”', '"')

                    # 如果碰到以上述元素开头的文本，则表示正文结束，停止写入
                    if text.startswith((keyword1, keyword2, keyword3, keyword4)):
                        break

                    # 如果某个元素的前4个字母大写（认为是人名），表示该元素需另起一段开始写入
                    # 该判断方式不能涵盖所有情况
                    if text[:4].isupper():
                        f.write('\n\n' + text.replace(': ', ':\n'))
                    else:
                        f.write(text.replace(': ', ':\n'))

                logger.info(f'文本【{self.__text}】保存完成。\n')
        except Exception as e:
            logger.error(f'保存文本出现错误，请检查：{e}\n')

    def get_only_text(self):
        """
        Func: 调用该方法，只用来下载某一期的文本
        """
        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()
            self.__get_text()

    def __get_picture_url(self):
        """
        Func: 获取指定网页上的图片的链接。不对外开放，如果用户需要获取图片链接，请调用 get_only_picture_url()
        """
        try:
            logger.info('开始获取封面图片的链接 ... ')
            html = etree.parse(self.__raw_html, etree.HTMLParser())
            picture_url = html.xpath('//div[contains(@class,"Image__Wrapper")]//source[last()]/@srcset')[0].split(' ')[1]

            with open('\\'.join([self.save_path, self.__picture_info]), 'a', encoding='utf-8') as f:
                f.writelines(picture_url + '\n\n')

            logger.info(f'封面图片的链接为：{picture_url}\n')

            return picture_url
        except Exception as e:
            logger.error(f'获取封面图片的链接出现错误，请检查：{e}\n')
            return False

    def __get_picture_info(self):
        """
        Func: 获取指定网页上的图片的信息。不对外开放，如果用户需要获取图片链接，请调用 get_only_picture_info()
        """
        try:
            logger.info('开始获取图片的信息(图片说明和拍摄者)并保存 ... ')
            html = etree.parse(self.__raw_html, etree.HTMLParser())
            picture_text = html.xpath('//span[@class="RichText"]//text()')

            # 如果 picture_text 为 [], 即网页上没有（有的节目没有封面图片的说明，只有作者；有的节目连图片的作者也没有）
            if not picture_text:
                picture_text = ['None']

            picture_auth = html.xpath('//span[contains(@class,"Caption__Credit")]//text()')
            if not picture_auth:
                picture_auth = ['None']

            with open('\\'.join([self.save_path, self.__picture_info]), 'a', encoding='utf-8') as f:
                f.writelines([item + '\n\n' for item in ('【图片简介】', picture_text[0], picture_auth[0])])

            logger.info(f'图片的信息【{self.__picture_info}】保存完成。\n')
        except Exception as e:
            logger.error(f'保存图片的信息出现错误，请检查：{e}\n')

    def __get_picture_file(self, url=None):
        """
        Func: 获取指定网页上的图片。不对外开放，如果用户需要获取图片，请调用 get_only_picture_file()
        url: 图片文件的链接
        """
        # 如果没有指定链接，则自动去网页上获取图片的链接
        if url is None:
            url = self.__get_picture_url()
            if not url:
                return

        # 如果提供了图片链接，则先判断提供的值是否为URL形式的字符串，然后直接使用提供的链接进行下载
        if isinstance(url, str) and url.startswith('http'):
            try:
                logger.info('开始请求图片数据 ... ')
                picture_data = requests.get(url)
            except Exception as e:
                logger.error(f'图片链接请求出现错误，请检查：{e}\n')
                return False

            logger.info('开始保存图片 ... ')
            try:
                with open('\\'.join([self.save_path, self.__picture]), 'wb') as f:
                    for chunk in picture_data.iter_content():
                        if chunk:
                            f.write(chunk)

                logger.info(f'图片【{self.__picture}】保存完成。\n')
            except Exception as e:
                logger.error(f'保存图片出现错误，请检查：{e}\n')
        else:
            logger.error(f'指定的图片链接【{url}】格式错误， 请检查！')

    def get_only_picture_url(self):
        """
        Func: 调用该方法，只用来下载某一期的图片的链接
        """
        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()

            return self.__get_picture_url()

    def get_only_picture_info(self):
        """
        Func: 调用该方法，只用来下载某一期的图片的信息
        """
        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()

            return self.__get_picture_info()

    def get_only_picture_file(self):
        """
        Func: 调用该方法，只用来下载某一期的图片
        """
        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()
            self.__get_picture_file()

    def get_picture_all(self):
        """
        Func: 调用该方法，获取某一期节目中所有图片相关的资源
        """
        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()
            self.__get_picture_info()
            self.__get_picture_file()

    def get_only_audio_url(self):
        """
        Func: 获取音频的链接
        """
        # headless mode
        option = webdriver.ChromeOptions()
        option.add_argument('--headless')
        option.add_argument('--disable-gpu')
        option.add_argument('start-maximized')
        option.add_experimental_option('excludeSwitches', ['enable-automation'])
        option.add_experimental_option('detach', True)
        option.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=option)
        driver.implicitly_wait(20)

        try:
            logger.info('再次请求网址获取音频链接 ... ')
            driver.get(self.url)
        except Exception as e:
            logger.error(f'再次请求网址出现错误，请检查：{e}\n')
            driver.close()
            return False

        try:
            # 切换 frame - 音频相关的内容嵌套在名为第一个 iframe 中
            logger.info('开始切换到包含音频的iframe ... ')

            iframe = driver.find_elements(By.TAG_NAME, "iframe")[0]

            # KEEP: 如下几种切换 frame的方式
            # driver.switch_to.frame('iheartembed')
            # driver.switch_to.frame(0)
            # driver.switch_to.frame(driver.find_elements(By.TAG_NAME, "iframe")[0])
            # driver.switch_to.frame(iframe)
            WebDriverWait(driver, 10).until(ec.frame_to_be_available_and_switch_to_it(iframe))

            logger.info('开始获取【播放】按钮 ... ')
            # audio_play_button = driver.find_element(By.TAG_NAME, 'button')
            audio_play_button = WebDriverWait(driver, 20).until(ec.element_to_be_clickable((By.TAG_NAME, 'button')))

            logger.info('开始点击【播放】按钮 ... ')
            webdriver.ActionChains(driver).move_to_element(audio_play_button).perform()
            time.sleep(2)
            webdriver.ActionChains(driver).click(audio_play_button).perform()

            logger.info('开始获取音频链接 ... ')
            audio_element = WebDriverWait(driver, 20).until(ec.presence_of_element_located((By.TAG_NAME, 'video')))
            audio_url = audio_element.get_attribute('src')
            logger.info(f'音频链接为：{audio_url}')

            with open('\\'.join([self.save_path, self.__audio_info]), 'w', encoding='utf-8') as f:
                f.write(audio_url)
            logger.info(f'音频链接【{self.__audio_info}】保存完成。\n')

            return audio_url
        except Exception as e:
            logger.error(f'获取音频链接出现错误，请检查：{e}\n')
            return False
        finally:
            driver.close()

    def __get_audio_file(self, url):
        """
        Func: 保存音频文件
        url: 音频文件的链接
       """
        logger.info('开始请求音频数据 ... ')
        try:
            audio_data = requests.get(url)
            logger.info('音频数据获取完成。')
        except Exception as e:
            logger.error(f'音频链接请求出现错误，请检查：{e}\n')
            return False

        logger.info('开始保存音频文件 ... ')
        try:
            with open('\\'.join([self.save_path, self.__audio]), 'wb') as f:
                f.write(audio_data.content)
                f.flush()

            logger.info(f'音频文件【{self.__audio}】保存完成。')
        except Exception as e:
            logger.error(f'音频文件保存出现错误，请检查：{e}')

    def get_audio_file(self, url=None):
        """
        Func: 获取音频文件
        Param: url: 音频文件的链接
       """
        if url is None:
            # 如果没有提供音频链接，则需要从网页中获取
            url = self.get_only_audio_url()
            if not url:
                return
            self.__get_audio_file(url)
        # 如果提供了音频链接，则先判断提供的值是否为URL形式的字符串，然后直接使用提供的链接进行下载
        elif isinstance(url, str) and url.startswith('http'):
            with open('\\'.join([self.save_path, self.__audio_info]), 'w', encoding='utf-8') as f:
                f.write(url)
            logger.info(f'用户提供的音频链接【{url}】保存完成。\n')
            logger.info(f'使用用户提供的音频链接进行下载。')
            self.__get_audio_file(url)
        else:
            logger.error(f'输入的音频URL {url} 不是字符串, 请检查！')

    def get_file(self):
        """
        Func: 获取Overheard的某一期相关资源，包括文本，图片，音频文件
        """
        # logger.info('===============【START】===============')
        logger.info(f'开始处理【{self.title}】... ')

        if not self.__request_url():
            logger.info('网页的HTML文件错误或不存在，停止获取发布日期，请检查！\n')
            return
        else:
            self.__get_publish_date()
            self.__get_save_path()
            self.__get_text()
            self.__get_picture_file()
            self.__get_picture_info()
            self.get_audio_file()
        # logger.info('===============【END】===============\n')


def get_files(info):
    """
    Func: 获取一期或者几期节目资源
    Param: info: 字典格式，保存节目的标题和对应的网址
    """
    if not isinstance(info, dict):
        logger.error(f'输入的信息 {info} 不是字典类型，请检查！')
        return False

    if len(info) < 1:
        logger.warning(f'输入的信息 {info} 为空字典，无须下载！')
        return False

    num = 1
    for episode_title, episode_url in info.items():
        logger.info(f'===============【Episode{num}: START】===============')
        downloader = Downloader(episode_title, episode_url)
        downloader.get_file()
        logger.info(f'===============【Episode{num}: END】===============\n\n')
        num += 1


def get_all_files(url):
    """
    Func: 获取Overheard的全部节目资源
    """
    # 开始处理Overhead主页
    sniffer = Sniffer(url)
    episode_info = sniffer.get_all_episode_info()

    if len(episode_info) < 1:
        logger.warning(f'输入的信息 {episode_info} 为空字典，无须下载！')
        return False

    # 开始依次获取每一期节目的资源
    if episode_info:
        num = 1
        for episode_title, episode_url in episode_info.items():
            logger.info(f'===============【Episode{num}: START】===============')
            downloader = Downloader(episode_title, episode_url)
            downloader.get_file()
            logger.info(f'===============【Episode{num}: END】===============\n\n')
            num += 1


logger = log_setting('Overheard_get_all', '../Logs')


if __name__ == '__main__':
    pass
    # title = "Farming for the planet"
    # url = 'https://www.nationalgeographic.com/podcasts/article/episode-15-farming-for-the-planet'
    # episodes = {title: url}
    # get_files(episodes)

    # downloader = Downloader(title, url)
    # downloader.get_only_picture_info()

    # website = "https://www.nationalgeographic.com/podcasts/overheard/"
    # get_all_files(website)
