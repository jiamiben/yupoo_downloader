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
        os.system("IF NOT EXIST page%s MD page%s" % (page, page))
        f = open("page%s/bf3_strona.csv" % page, "w", newline="", encoding="utf-8")
        os.system("attrib +h bf3_strona.csv")
        writer = csv.writer(f, delimiter=" ", quoting=csv.QUOTE_MINIMAL)
        writer.writerow(["LINKS"])
        # url = "https://boostmasterlin.x.yupoo.com/albums?tab=gallery&page=%s"%page
        url = self.main_url + "?page=%s" % page
        text = url
        head, sep, tail = text.partition("x.yupoo.com")
        Logger.ins().std_logger().info(">>>[create_csv_file] Download photos from websites:" + head + "x.yupoo.com")
        Logger.ins().std_logger().info(">>>[create_csv_file] Page=%s, URL:%s" % (page, url))  # https://yejibin.x.yupoo.com/albums?tab=gallery&page=1
        response = requests.get(url)
        data = response.text
        soup = BeautifulSoup(data, features="lxml")  # soup = BeautifulSoup(data, 'lxml')
        row1 = []
        global title
        title = []
        count = 0
        for link in soup.findAll("a", class_="album__main"):
            count = count + 1
            q = link.get("href")
            t = link.get("title")
            row1.append(q)
            title.append(t)
        page = page + 1
        Logger.ins().std_logger().info(">>>[create_csv_file] Will be downloaded " + str(count) + " Photo albuma.")

        for c in range(len(row1)):
            writer.writerow([row1[c]])
        print(">>>T[create_csv_file] The CSV file containing the link can be found at:" + os.getcwd())
        f.close()
        return title

    @retry(stop_max_attempt_number=5)
    def create_file_tests(self, number, page):
        try:
            with open((os.path.join("page%s" % page, str(number) + "TESTY.csv")), "w", newline="") as file:
                writer = csv.writer(file, delimiter=",")
                df = pd.read_csv(os.path.join("page%s" % page, "bf3_strona.csv"), sep=" ")
                TEXT = df["LINKS"][number]
                url = self.main_url + "&page=%s" % page
                text = url
                head, sep, tail = text.partition("x.yupoo.com")
                url = head + "x.yupoo.com" + TEXT

                response = requests.get(url, timeout=None)
                data = response.content
                soup = BeautifulSoup(data, "lxml")
                # print(soup)
                search = soup.select(".image__landscape")
                writer.writerow([number])
                for x in search:
                    q = x["data-src"]
                    writer.writerow(["https:" + q])
                search = soup.select(".image__portrait")
                for x in search:
                    q = x["data-src"]
                    writer.writerow(["https:" + q])
        except:
            print(traceback.format_exc())

    def download_photo(self, number, page, value):
        try:
            try:
                print(">>>[download_photo] source_title: %s" % value)
                add_money = random.randint(50, 100)
                origin_price = 40 #round(int(value.split()[0])/7)
                sale_price = origin_price + add_money
                value = value.replace(value.split()[0], str(origin_price))
                value = str(sale_price) + " " +value
                value = value.replace("男女鞋","").replace("耐克","").replace("“", " ").replace("”", " ").replace("‘", " ").replace("’", " ").replace("'", "")
                # value = self.translate(value) # 要翻译再打开
                reg = "[^0-9A-Za-z\u4e00-\u9fa5]"
                value=re.sub(reg, ' ', value)
                print(">>>[download_photo] changed_title: %s" % value)
            except:
                print(traceback.format_exc())

            def create_directory(directory):
                if not os.path.exists(directory):
                    os.makedirs(directory)
                print(">>>[download_photo] folder: %s" % directory)
                
            def download_save(url, count):
                try:
                    folder = value
                    
                    folder = os.path.join("page%s" % page, folder)
                    try:
                        create_directory(folder)
                    except:
                        pass
                    c = requests.Session()
                    c.get("https://photo.yupoo.com/")
                    c.headers.update({"referer": "https://photo.yupoo.com/"})
                    res = c.get(url, timeout=None)
                    if not os.path.exists(f'{folder}/{30-count}.jpg'):
                        with open(f'{folder}/{30-count}.jpg', "wb") as f:
                            f.write(res.content)
                            f.close()
                    with open(os.path.join(folder, "title.txt"), "w", encoding="utf-8") as f:
                        f.write(value)
                    
                except:
                    print(traceback.format_exc())

            dfzdj = pd.read_csv(os.path.join("page%s" % page, str(number) + "TESTY.csv"))
            count = 0
            try:
                for col in dfzdj.columns:

                    for url in dfzdj[col].tolist():
                        count += 1
                        if str(url).startswith("http"):
                            download_save(url, count)
                            count

                    print(">>>[download_photo] Download " + str(url) + " Done")
            except:
                print(traceback.format_exc())
            try:
                path = os.getcwd() + "\\" + "page%s" % page + "\\" + col
                """
                files = os.listdir(path)
                for index, file in enumerate(files):
                    if file != "title.txt":
                        os.rename(os.path.join(path, file), os.path.join(path, "".join([str(index), "big.jpg"])
                """
            except:
                print(traceback.format_exc())

        except:
            print(traceback.format_exc())
    
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
    a = yupooDownloader("https://mabimabihong123.x.yupoo.com/categories/3184733")
    for page in range(1,2):
        title_list = a.create_csv_file(page)
        for x, value in enumerate(title_list):
            a.create_file_tests(x, page)
            a.download_photo(x, page, value)
            os.remove(os.path.join("page%s" % page, (str(x) + "TESTY.csv")))
