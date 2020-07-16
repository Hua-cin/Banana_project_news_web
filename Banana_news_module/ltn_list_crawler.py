#!/usr/bin/python3
# -*- coding: utf-8 -*-

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
import re

exec_file_path = '/home/lazyso/anaconda3/envs/AutoNewsenv/banana_project_news_web'
exec_file_path = os.getcwd()

def main():
   pass

def ltn_list():
   '''
   :return: compare_result, article_list
   '''

   # check log folder exist or not
   # func_check_folder("log_folder")

   # call fetch_db_newest function, fetch db newest data
   db_neswest_data = fetch_db_newest()

   # if news title contain exclude word, not to fetch
   title_exclude_word_path = "{}/ref_data/title_exclude_word.txt".format(exec_file_path)
   title_exclude_word = load_file_to_list(title_exclude_word_path)

   # # if news tag contain exclude word, not to fetch
   # tag_exclude_word = ['娛樂']

   # search page
   url = "https://news.ltn.com.tw/search?keyword=%E9%A6%99%E8%95%89"
   url = "https://news.ltn.com.tw/search?keyword=%E9%A6%99%E8%95%89&conditions=and&start_time=2020-04-09&end_time=2020-07-09&page=1"

   # call request url function
   res = request_url(url)

   # use beautifulsoup
   soup = BeautifulSoup(res.text, 'html.parser')

   # print(soup)

   # capture total pages
   total_pages = int(str(soup.select('div [class="p_last"]')).split('page=')[1].split('">》')[0])
   # print("total pages : {:>3}".format(total_pages))

   # init article_compare_result, default False
   article_compare_result = False

   # init article_list
   article_list = []

   # scan search page
   for i in range(1, total_pages+1):

      # search page
      url = 'https://news.ltn.com.tw/search?keyword=%E9%A6%99%E8%95%89&page={}'.format(i)
      url = "https://news.ltn.com.tw/search?keyword=%E9%A6%99%E8%95%89&conditions=and&start_time=2020-04-09&end_time=2020-07-09&page={}".format(i)

      # call request url function
      res = request_url(url)

      # use beautifulsoup
      soup = BeautifulSoup(res.text, 'html.parser')

      # capture all text
      all_text = soup.select('li')

      # scan one page article
      for j in all_text:

         if j.select('span') != []:
            if len(j.select('span')[0].text.split(' ')) == 1:
              publish_time = datetime.datetime.strptime(j.select('span')[0].text, "%Y-%m-%d")
            else:
              publish_time = datetime.datetime.strptime(j.select('span')[0].text, "%Y-%m-%d %H:%M")

            # compare web article publish time and db newest data publish time, data scan finish
            if publish_time <= db_neswest_data['publish_time']:
              article_compare_result = True
              break

            # capture article data
            web_class = ' '
            title = j.select('a[class="tit"]')[0].text
            sub_url = j.select('a[class="tit"]')[0]['href']


            # init row data (for one article)
            row = {}

            # store article data to row
            row['publish_time'] = publish_time
            row['title'] = title
            if re.search('com.tw/m/', sub_url) != None:
               sub_url = sub_url.replace
            row['url'] = sub_url
            row['web_class'] = web_class

            # call excude_in function and if meet the conditions, store to article_list
            if not exclude_in(title, title_exclude_word) and sub_url != "" :
              article_list.append(row)

      # data scan finish
      if article_compare_result == True:
         break

   # return article_list and need update or not
   return article_list

def fetch_db_newest():
   '''
   fetch db the newest data for data confirm
   :return: db_neswest_data
   '''

   # fetch key_word
   key_word = pd.read_csv(r'{}/ref_data/key_word.csv'.format(exec_file_path))

   try:
      # connect database
      db = MySQLdb.connect(host = str(key_word.loc[0, 'host']),
                           user = str(key_word.loc[0, 'user']),
                           passwd = str(key_word.loc[0, "passwd"]),
                           db = str(key_word.loc[0, "db"]),
                           port = int(key_word.loc[0, "port"]),
                           charset=str(key_word.loc[0, "charset"]))

      sql_str = 'SELECT * FROM fruveg.Daniel_news ' \
                'where web_name = "自由時報"  ' \
                'order by publish_time DESC limit 1;'
      db_neswest_data_df = pd.read_sql(sql=sql_str, con=db)

   except Exception as err:
      now = datetime.datetime.now()
      print("{}, {}, {}".format(now, "31.Unable to fetch data from db. STOP!", err))
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
      now = datetime.datetime.now()
      print("{}, {}, {}".format(now, "32.Unable to request data from web. STOP!", err))
      sys.exit(0)

      # if first requset error, delay 180 second
      t = 180
      time.sleep(t)

      if proxy != '':
         # print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

      now = datetime.datetime.now()
      print("{}, {}".format(now, "33.Request data normal, continue program."))

   except:
      now = datetime.datetime.now()
      print("{}, {}".format(now, "34.Unable to request data again. STOP!"))
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

if __name__ == "__main__":
   '''
   main function
   '''
   main()
