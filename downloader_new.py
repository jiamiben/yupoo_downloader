import os, random
import pandas as pd
import requests
from retrying import retry
from bs4 import BeautifulSoup
import csv
import json
import re
import traceback
import sys
import threading
import logging
import datetime


class yupooDownloader:
    def __init__(self, main_url="https://boostmasterlin.x.yupoo.com/albums?tab=gallery"):
        self.main_url = main_url

    def create_csv_file(self, page):
        # 生成保存 CSV 文件的文件夹路径
        folder = os.path.join(os.getcwd(), f"page{page}")
        # 如果文件夹不存在，则创建它
        if not os.path.exists(folder):
            os.makedirs(folder)
        # 生成 CSV 文件的完整路径
        file_path = os.path.join(folder, "bf3_strona.csv")
        # 记录日志，指示正在下载页面上的相册链接
        Logger.ins().std_logger().info(f">>>[create_csv_file] Downloading photos from website: {self.main_url} (page={page})")

        try:
            # 构造 URL 并下载数据
            url = f"{self.main_url}?page={page}"
            response = requests.get(url)
            data = response.text
            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(data, features="lxml")
            links = []  # 存储相册链接的列表
            global title
            title = []  # 存储相册标题的列表
            count = 0
            # 找到所有 class 为 "album__main" 的 <a> 元素，并提取 href 和 title 属性
            for link in soup.find_all("a", class_="album__main"):
                count += 1
                q = link.get("href")
                t = link.get("title")
                links.append([q])  # 将链接添加到列表中
                title.append(t)   # 将标题添加到列表中
            # 记录日志，指示将要下载多少个相册
            Logger.ins().std_logger().info(f">>>[create_csv_file] {count} photo albums will be downloaded.")
            # 将链接写入 CSV 文件
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter=",", quoting=csv.QUOTE_MINIMAL)
                writer.writerow(["LINKS"])
                writer.writerows(links)
            # 记录日志，指示 CSV 文件保存在哪里
            Logger.ins().std_logger().info(f">>>[create_csv_file] The CSV file containing the link can be found at: {folder}")
            # 返回相册标题列表
            return title
        except requests.exceptions.RequestException as e:
            # 如果下载过程中出现异常，则记录错误信息并重新引发该异常
            Logger.ins().std_logger().error(f">>>[create_csv_file] Error downloading data (page={page}): {e}")
            raise e

    @retry(stop_max_attempt_number=5)
    def create_file_tests(self, number, page):
        try:
            # 生成保存 CSV 文件的文件夹路径
            folder = os.path.join(os.getcwd(), f"page{page}")
            # 生成 CSV 文件的完整路径
            file_path = os.path.join(folder, str(number) + "TESTY.csv")
            # 打开 CSV 文件并写入数据
            with open(file_path, "w", newline="") as file:
                writer = csv.writer(file, delimiter=",")
                # 读取相册链接列表
                df = pd.read_csv(os.path.join(folder, "bf3_strona.csv"), sep=" ")
                # 根据页面和相册编号构造 URL
                url = self._get_album_url(page, number, df)
                # 下载并解析 HTML
                soup = self._download_and_parse_html(url)
                # 查找横向图片
                search = soup.select(".image__landscape")
                writer.writerow([number])
                for x in search:
                    q = x["data-src"]
                    writer.writerow(["https:" + q])
                # 查找竖向图片
                search = soup.select(".image__portrait")
                for x in search:
                    q = x["data-src"]
                    writer.writerow(["https:" + q])
        except (requests.exceptions.RequestException, KeyError) as e:
            # 如果出现异常，则记录错误信息，而不是直接打印堆栈跟踪
            Logger.ins().std_logger().error(f">>>[create_file_tests] Error creating test file (page={page}, number={number}): {e}")
            traceback.print_exc()

    def _get_album_url(self, page, number, df):
        # 获取相册链接
        TEXT = df["LINKS"][number]
        # 构造 URL
        url = f"{self.main_url}&page={page}"
        head, sep, tail = url.partition("x.yupoo.com")
        album_url = head + "x.yupoo.com" + TEXT
        return album_url

    def _download_and_parse_html(self, url):
        # 下载并解析 HTML
        response = requests.get(url, timeout=None)
        data = response.content
        soup = BeautifulSoup(data, "lxml")
        return soup

    def download_photo(self, number, page, value):
        try:
            # 更改相册标题
            value = self._change_album_title(value)
            print(f">>>[download_photo] Changed title: {value}")
            
            # 创建文件夹
            folder = os.path.join("page%s" % page, value)
            self._create_directory(folder)
            print(f">>>[download_photo] Folder: {folder}")
        
            # 下载并保存图片
            df = pd.read_csv(os.path.join("page%s" % page, str(number) + "TESTY.csv"))
            count = 0
            for col in df.columns:
                for url in df[col].tolist():
                    if str(url).startswith("http"):
                        count += 1
                        self._download_and_save(url, count, folder, value)
                        print(f">>>[download_photo] Download {url} Done")
            
        except Exception as e:
            # 如果出现异常，则记录错误信息，而不是直接打印堆栈跟踪
            Logger.ins().std_logger().error(f">>>[download_photo] Error downloading photos (page={page}, number={number}): {e}")
            traceback.print_exc()
        
    def _change_album_title(self, title):
        try:
            # 将相册标题更改为指定格式
            add_money = random.randint(50, 100)
            origin_price = 40 #round(int(title.split()[0])/7)
            sale_price = origin_price + add_money
            title = title.replace(title.split()[0], str(origin_price))
            title = str(sale_price) + " " +title
            title = title.replace("男女鞋","").replace("耐克","").replace("“", " ").replace("”", " ").replace("‘", " ").replace("’", " ").replace("'", "")
            # title = self.translate(title) # 如果需要翻译成英文可以打开
            reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
            title = re.sub(reg, ' ', title)
            return title
        
        except Exception as e:
            # 如果出现异常，则记录错误信息，而不是直接打印堆栈跟踪
            Logger.ins().std_logger().error(f">>>[download_photo] Error changing album title: {e}")
            traceback.print_exc()

    def _create_directory(self, directory):
        try:
            # 创建文件夹
            if not os.path.exists(directory):
                os.makedirs(directory)
        except Exception as e:
            # 如果出现异常，则记录错误信息，而不是直接打印堆栈跟踪
            Logger.ins().std_logger().error(f">>>[download_photo] Error creating directory: {e}")
            traceback.print_exc()

    def _download_and_save(self, url, count, folder, title):
        try:
            # 下载并保存图片
            c = requests.Session()
            c.get("https://photo.yupoo.com/")
            c.headers.update({"referer": "https://photo.yupoo.com/"})
            res = c.get(url, timeout=None)
            if not os.path.exists(f"{folder}/{30-count}.jpg"):
                with open(f"{folder}/{30-count}.jpg", "wb") as f:
                    f.write(res.content)
                    f.close()
            with open(f"{folder}/title.txt", "w", encoding="utf-8") as f:
                f.write(title)
        except Exception as e:
            # 如果出现异常，则记录错误信息，而不是直接打印堆栈跟踪
            Logger.ins().std_logger().error(f">>>[download_photo] Error downloading and saving photo: {e}")
            traceback.print_exc()
            
    def translate(self, text):
        try:
            from DrissionPage import MixPage
            import time, re, traceback
            page = MixPage("d")
            # text = "107 40 Nk Max 270 网面半掌气垫跑步鞋 DC0957-001"
            # 107%2040%20Nk%20Max%20270%20网面半掌气垫跑步鞋%20DC0957-001
            url = "https://fanyi.baidu.com/"
            if page.ele("@id=baidu_translate_input", timeout=1) == None:
                page.get(url)
            page.ele("@id=baidu_translate_input", timeout=15).input(text)
            time.sleep(3)
            tra = page.ele("@class=trans-right").text.split("\n")[1]
            return tra
        except:
            print(traceback.format_exc())
        return text
        
class Logger(object):
    instance = None
    curr_log_name = ""
    __fh = None
    __ch = None
    mutex = threading.Lock()

    def __get_fh(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.__fh = logging.FileHandler("./trace_log/%s" % self.curr_log_name)
        self.__fh.setFormatter(formatter)

    def __get_ch(self):
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.__ch = logging.StreamHandler()
        self.__ch.setFormatter(formatter)

    def __init__(self):
        if not os.path.exists("./trace_log/"):
            os.mkdir("./trace_log/")

        self.fileLogger = logging.getLogger("FileLogger")
        self.fileLogger.setLevel(logging.DEBUG)

        self.stdLogger = logging.getLogger("StdLogger")
        self.stdLogger.setLevel(logging.DEBUG)

        self.curr_log_name = "AutoTest_%s.log" % datetime.datetime.now().strftime("%Y-%m-%d")
        self.__get_fh()
        self.__get_ch()

        self.fileLogger.addHandler(self.__fh)
        self.stdLogger.addHandler(self.__ch)
        self.stdLogger.addHandler(self.__fh)
        # log.removeHandler(fileTimeHandler)

    @staticmethod
    def ins():
        if Logger.instance == None:
            Logger.mutex.acquire()
            Logger.instance = Logger()
            Logger.mutex.release()
        return Logger.instance

    def file_logger(self):
        if self.curr_log_name != "AutoTest_%s.log" % datetime.datetime.now().strftime("%Y-%m-%d"):
            self.curr_log_name = "AutoTest_%s.log" % datetime.datetime.now().strftime("%Y-%m-%d")
            self.fileLogger.removeHandler(self.__fh)
            self.__get_fh()
            self.fileLogger.addHandler(self.__fh)

        return self.fileLogger

    def std_logger(self):
        if self.curr_log_name != "AutoTest_%s.log" % datetime.datetime.now().strftime("%Y-%m-%d"):
            self.curr_log_name = "AutoTest_%s.log" % datetime.datetime.now().strftime("%Y-%m-%d")
            self.stdLogger.removeHandler(self.__fh)
            self.__get_fh()
            self.stdLogger.addHandler(self.__fh)
        return self.stdLogger

if __name__ == "__main__":    
    # 初始化下载器
    downloader = yupooDownloader("https://mabimabihong123.x.yupoo.com/categories/2931141") # 下载的url
    
    for page in range(1, 2): # 页数 只下载第一页
        # 获取相册标题列表
        title_list = downloader.create_csv_file(page)
        
        for x, value in enumerate(title_list):
            # 创建测试文件
            downloader.create_file_tests(x, page)
            
            # 下载照片
            downloader.download_photo(x, page, value)
            
            # 删除测试文件
            os.remove(os.path.join("page%s" % page, (str(x) + "TESTY.csv")))