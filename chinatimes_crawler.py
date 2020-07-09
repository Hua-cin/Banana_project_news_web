'''
get banana news, chinatime
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
   '''

   :return: compare_result, article_list

   '''

   # check log file exist ornot
   func_check_file("log_file")

   # fetch db newest data
   db_neswest_data = fetch_db_newest()
   # print(db_neswest_data)

   # if news title contain exclude word, not to catch
   title_exclude_word = ['香蕉船', '香蕉哥哥', '香蕉新樂園', '香蕉伯', 'YOYO', 'yoyo', '正顎', '香蕉男', '香蕉」', '香蕉水', '旺仔', \
              '想當香蕉', '流血', '硬', '黑蕉', '兒童界', '香蕉機', '香蕉槍', '香蕉球', 'GG']

   # f news tag contain exclude word, not to catch
   tag_exclude_word = ['娛樂']

   url = "https://www.chinatimes.com/Search/%E9%A6%99%E8%95%89?chdtv"
   res = request_url(url)

   soup = BeautifulSoup(res.text, 'html.parser')
   total_pages = int(str(soup.select('a[class="page-link"]')[-1]).split('page=')[1].split('">')[0])

   # print("total pages : {:>3}".format(total_pages))

   article_compare_result = False
   update_or_not = False
   article_list = []

   for i in range(1, total_pages+1):

      url = 'https://www.chinatimes.com/Search/%E9%A6%99%E8%95%89?page={}&chdtv'.format(i)

      res = request_url(url)
      soup = BeautifulSoup(res.text, 'html.parser')
      all_text = soup.select('div[class="col"]')

      for j in all_text:

         if datetime.datetime.strptime(str(j.select('time')[0]).split('datetime="')[1].split('"><')[0], "%Y-%m-%d %H:%M") \
                 <= db_neswest_data['publish_time']:
            article_compare_result = True
            break

         update_or_not = True

         web_class = j.select('div [class="category"]')[0].text
         title = j.select('h3')[0].text
         publish_time = datetime.datetime.strptime(str(j.select('time')[0]).split('datetime="')[1].split('"><')[0], "%Y-%m-%d %H:%M")
         sub_url = j.select('h3 a')[0]['href']

         row = {}

         row['publish_time'] = publish_time
         row['web_class'] = web_class
         row['title'] = title
         row['url'] = sub_url

         if (not exclude_in(title, title_exclude_word) and (not exclude_in(web_class, tag_exclude_word))) and sub_url != "":
            article_list.append(row)
            # print(row)
      # print(article_list)

      if article_compare_result == True:
         break

   return article_list, update_or_not

def func_check_file(sub_keyword):
   resource_path = r'{}/'.format(os.getcwd()) + sub_keyword

   # 檢查目錄是否存在, 如已存在則強制刪除目錄並再次建立目錄
   if os.path.exists(resource_path):
      pass
   else:  # 目錄不存在, 則建立新目錄
      os.mkdir(resource_path)


def write_log(log):
   """ log function """
   now = datetime.datetime.now()
   today = datetime.date.today()
   print("{}, {}".format(now, log), file=open("{}/log_file/log_{}.txt".format(os.getcwd(),today), "a"))


def fetch_db_newest():
   '''
   fetch db the newest data for data confirm
   :return: db_neswest_data
   '''

   # fetch key_word
   key_word = pd.read_csv(r'{}/key_word.csv'.format(os.getcwd()))

   try:
      # connect database
      db = MySQLdb.connect(host = str(key_word.loc[0, 'host']),
                           user = str(key_word.loc[0, 'user']),
                           passwd = str(key_word.loc[0, "passwd"]),
                           db = str(key_word.loc[0, "db"]),
                           port = int(key_word.loc[0, "port"]),
                           charset=str(key_word.loc[0, "charset"]))

      sql_str = 'SELECT * FROM fruveg.Daniel_news_test ' \
                'where web_name = "chinatimes" and related = 1 ' \
                'order by publish_time DESC limit 1;'
      db_neswest_data_df = pd.read_sql(sql=sql_str, con=db)

   except Exception as err:
      msg = "01.Unable to fetch data from db. Program stop!! {}".format(err)
      write_log(msg)
      print(err)
      sys.exit(0)

   db.close()

   db_neswest_data = {}
   db_neswest_data['publish_time'] = datetime.datetime.strptime(str(db_neswest_data_df.loc[0,'publish_time']), "%Y-%m-%d %H:%M:%S")
   db_neswest_data['web_class'] = str(db_neswest_data_df.loc[0,'web_class'])
   db_neswest_data['title'] = str(db_neswest_data_df.loc[0,'title'])
   db_neswest_data['url'] = str(db_neswest_data_df.loc[0,'url'])

   return db_neswest_data # db_neswest_data (dict format)

def request_url(url):
   '''

   :return:
   '''

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

      t = 300
      time.sleep(t)

      if proxy != '':
         print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

      msg = "03.Request data normal, continue program."
      write_log("{}".format(msg))  # ~~~~~

   except:
      msg = "04.Unable to request data again, stop program.\n"
      write_log("{}".format(msg))  # ~~~~~
      sys.exit(0)

   return res


def exclude_in(string, exclude_list):
   for x in range(len(exclude_list)):
      if exclude_list[x] in string:
         return True
   return False

if __name__ == "__main__":

   main()
