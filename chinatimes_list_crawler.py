'''
get banana news, chinatimes list
input : N/A
output : article_list, update_or_not
'''

from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime
import os
import sys
import pandas as pd
import time
import random

def main():
   pass

def ltn_list():
   '''
   :return: compare_result, article_list
   '''

   # check log folder exist or not
   func_check_folder("log_folder")

   # call fetch_db_newest function, fetch db newest data
   db_neswest_data = fetch_db_newest()

   # if news title contain exclude word, not to fetch
   # title_exclude_word = ['香蕉船', '香蕉哥哥', '香蕉新樂園', '香蕉伯', 'YOYO', 'yoyo', '正顎', '香蕉男', '香蕉」', '香蕉水', '旺仔', \
   #            '想當香蕉', '流血', '硬', '黑蕉', '兒童界', '香蕉機', '香蕉槍', '香蕉球', 'GG', '罷韓']
   title_exclude_word_path = "{}/ref_data/title_exclude_word.txt".format(os.getcwd())
   title_exclude_word = load_file_to_list(title_exclude_word_path)

   # # if news tag contain exclude word, not to fetch
   # tag_exclude_word = ['娛樂']

   # search page
   url = "https://www.chinatimes.com/Search/%E9%A6%99%E8%95%89?chdtv"

   # call request url function
   res = request_url(url)

   # use beautifulsoup
   soup = BeautifulSoup(res.text, 'html.parser')

   # capture total pages
   total_pages = int(str(soup.select('a[class="page-link"]')[-1]).split('page=')[1].split('">')[0])
   # print("total pages : {:>3}".format(total_pages))

   # init article_compare_result, default False
   article_compare_result = False

   # init update_or_not, default False
   update_or_not = False

   # init article_list
   article_list = []

   # scan search page
   for i in range(1, total_pages+1):

      # search page
      url = 'https://www.chinatimes.com/Search/%E9%A6%99%E8%95%89?page={}&chdtv'.format(i)

      # call request url function
      res = request_url(url)

      # use beautifulsoup
      soup = BeautifulSoup(res.text, 'html.parser')

      # capture all text
      all_text = soup.select('div[class="col"]')

      # scan one page article
      for j in all_text:

         # compare web article publish time and db newest data publish time, data scan finish
         if datetime.datetime.strptime(str(j.select('time')[0]).split('datetime="')[1].split('"><')[0], "%Y-%m-%d %H:%M") \
                 <= db_neswest_data['publish_time']:
            article_compare_result = True
            break

         # web have new data, need to update news page
         update_or_not = True

         # capture article data
         web_class = j.select('div [class="category"]')[0].text
         title = j.select('h3')[0].text
         publish_time = datetime.datetime.strptime(str(j.select('time')[0]).split('datetime="')[1].split('"><')[0], "%Y-%m-%d %H:%M")
         sub_url = j.select('h3 a')[0]['href']

         # init row data (for one article)
         row = {}

         # store article data to row
         row['publish_time'] = publish_time
         row['web_class'] = web_class
         row['title'] = title
         row['url'] = sub_url

         # call excude_in function and if meet the conditions, store to article_list
         if (not exclude_in(title, title_exclude_word) and (not exclude_in(web_class, tag_exclude_word))) and sub_url != "":
            article_list.append(row)
      # data scan finish
      if article_compare_result == True:
         break

   # return article_list and need update or not
   return article_list, update_or_not

def func_check_folder(sub_keyword):
   '''
   confirm have log folder or not
   :param sub_keyword: log folder name
   '''

   resource_path = r'{}/'.format(os.getcwd()) + sub_keyword

   # confirm folder exist or not
   if os.path.exists(resource_path):
      pass
   else:  # if no exist, make a new filder
      os.mkdir(resource_path)

   today = datetime.date.today()

   # write a space to log file
   print(" ", file=open("{}/log_folder/log_{}.txt".format(os.getcwd(),today), "a"))

def write_log(log):
   '''
   write log to log file
   :param log: log message
   '''

   now = datetime.datetime.now()
   today = datetime.date.today()

   # Standard output to log file
   print("{}, {}".format(now, log), file=open("{}/log_folder/log_{}.txt".format(os.getcwd(),today), "a"))

def fetch_db_newest():
   '''
   fetch db the newest data for data confirm
   :return: db_neswest_data
   '''

   # fetch key_word
   key_word = pd.read_csv(r'{}/ref_data/key_word.csv'.format(os.getcwd()))

   try:
      # connect database
      db = MySQLdb.connect(host = str(key_word.loc[0, 'host']),
                           user = str(key_word.loc[0, 'user']),
                           passwd = str(key_word.loc[0, "passwd"]),
                           db = str(key_word.loc[0, "db"]),
                           port = int(key_word.loc[0, "port"]),
                           charset=str(key_word.loc[0, "charset"]))

      sql_str = 'SELECT * FROM fruveg.Daniel_news_test ' \
                'where web_name = "chinatimes"  ' \
                'order by publish_time DESC limit 1;'
      db_neswest_data_df = pd.read_sql(sql=sql_str, con=db)

   except Exception as err:
      msg = "01.Unable to fetch data from db. Program stop!! {}".format(err)
      write_log(msg)
      print(err)
      sys.exit(0)

   db.close()

   # init db_neswest_data dict
   db_neswest_data = {}
   # store db newest data to dict
   db_neswest_data['publish_time'] = datetime.datetime.strptime(str(db_neswest_data_df.loc[0,'publish_time']),
                                                                "%Y-%m-%d %H:%M:%S")
   db_neswest_data['web_class'] = str(db_neswest_data_df.loc[0,'web_class'])
   db_neswest_data['title'] = str(db_neswest_data_df.loc[0,'title'])
   db_neswest_data['url'] = str(db_neswest_data_df.loc[0,'url'])

   # return db_neswest_data (dict format)
   return db_neswest_data

def request_url(url):
   '''
   use url to request request
   :param url: url
   :return: request
   '''

   # call delay function, random 1 ~ 5 second
   delay(5)

   # proxy setting
   proxy = ''
   proxies = {
      'http': 'http://' + proxy,
      'https': 'http://' + proxy
   }
   # headers
   headers = {
      'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36'
   }

   # request a request
   try:
      if proxy != '':
         print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

   except Exception as err:
      msg = "02.Unable to request data from web. {}".format(err)
      write_log(msg)
      print(err)

      # if first requset error, delay 180 second
      t = 180
      time.sleep(t)

      if proxy != '':
         print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

      msg = "03.Request data normal, continue program."
      write_log("{}".format(msg))  # ~~~~~

   except:
      # if request second error, program stop
      msg = "04.Unable to request data again, stop program.\n"
      write_log("{}".format(msg))  # ~~~~~
      sys.exit(0)

   # if request normal, return request
   return res

def exclude_in(string, exclude_list):
   '''

   :param string:
   :param exclude_list: eclude word list
   :return: True or False
   '''

   for x in range(len(exclude_list)):
      if exclude_list[x] in string:
         # if exist, return True
         return True
   # if not exist, return False
   return False

def delay(x=1):
   '''
   set system delay
   :param x: delay how many second
   :return:
   '''

   # randon 1 ~ x second
   t = random.randint(1, x)

   # for delay loop
   for y in range(1, t+1):
      if y < t:
         # print("\rdelay {:>2d} 秒".format(t - y), end="")
         time.sleep(1)
   # print("\rrequest finish ")

def load_file_to_list(path):
   '''
   load file for list item
   :param path: file path
   :return: data list
   '''

   with open(path, 'r', encoding='utf-8') as f:
      temp = f.read()

   text = temp.split('\n')
   title_exclude_word = []

   for i in text:
      title_exclude_word.append(i)

   return title_exclude_word

if __name__ == "__main__":
   '''
   main function
   '''
   main()
