#!/usr/bin/python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import sys
import time
import random
import datetime
import re

def main():
    # content, web_tag, article_time, content_exist = ltn_content("https://news.ltn.com.tw/news/sports/breakingnews/3221247")
    # tvbs_content("https://news.tvbs.com.tw/news/search_check/news/1340105")
    pass

def chinatimes_content(url):
    '''

    :param url: want requent url
    :return: chinatimes url content
    '''

    # call request url function
    res = request_url(url)
    sub_soup = BeautifulSoup(res.text, 'html.parser')

    # capture content
    all_text = sub_soup.select('div[class ="col-xl-11"] p')
    content = ""

    for j in range(len(all_text)):
        content += all_text[j].text
        if all_text[j].text != '':
            content += "\n"

    article_date = sub_soup.select('span[class="date"]')[0].text.replace("/","-")
    article_hour = sub_soup.select('span[class="hour"]')[0].text

    article_time = article_date + ' ' + article_hour

    # capture tag
    tag = sub_soup.select('span[class="hash-tag"]')
    web_tag = tag[0].text.replace('#','')
    for y in range(1, len(tag)):
        web_tag += (';'+tag[y].text.replace('#',''))

    # print(content)

    if content == '':
        content_exist = False
    else:
        content_exist = True

    # return chinatimes url content
    return content, web_tag, article_time, content_exist

def ltn_content(url):
    """

    :param url:
    :return:
    """
    article_time = 0
    content = ""

    res = request_url(url)
    sub_soup = BeautifulSoup(res.text, 'html.parser')

    # type 1
    if content == "":
        try:
            all_text = sub_soup.select('div[class ="text"] p')
            drop_text = sub_soup.select('div[class ="text"] p[class]')

            for z in range(len(all_text)):
                if all_text[z] not in drop_text:
                    content += (all_text[z].text+"\n")
            content = content.strip()

            if content != "":
                article_time = sub_soup.select('span[class ="time"]')[0].text.strip()
        except:
            pass

    # type 2
    if content == "":
        try:
            all_text = sub_soup.select('div[class ="text boxTitle boxText"] p')
            drop_text = sub_soup.select('div[class ="text boxTitle boxText"] p[class]')

            for z in range(len(all_text)):
                if all_text[z] not in drop_text:
                    content += (all_text[z].text+"\n")
            content = content.strip()

            if content != "":
                article_time = sub_soup.select('span[class="time"]')[0].text.strip()
        except:
            pass

    # type 3
    if content == "":
        try:
            all_text = sub_soup.select('div[class="cont"] p')
            drop_text = sub_soup.select('div[class="cont"] p[class]')

            for z in range(len(all_text)):
                if all_text[z] not in drop_text:
                    content += (all_text[z].text+"\n")
            content = content.strip()

            if content != "":
                article_time = sub_soup.select('div[class="writer_date"]')[0].text.strip()
        except:
            pass

    # type 4
    if content == "":
        try:
            all_text = sub_soup.select('div[class="news_content"] p')
            drop_text = sub_soup.select('div[class="news_content"] p[class]')

            for z in range(len(all_text)):
                if all_text[z] not in drop_text:
                    content += (all_text[z].text+"\n")
            content = content.strip()

            if content != "":
                article_time = sub_soup.select('div[class="c_time"]')[0].text.strip()
        except:
            pass

    web_tag = ' '

    # print(content)
    if content == '':
        content_exist = False
    else:
        content_exist = True

    # return ltn url content article_time
    return content, web_tag, article_time, content_exist

def tvbs_content(url):
    '''

    :param url: want requent url
    :return: chinatimes url content
    '''

    # call request url function
    res = request_url(url)
    sub_soup = BeautifulSoup(res.text, 'html.parser')
    all_text = sub_soup.text

    # capture content
    content = re.sub(r'\n+\s+', "\n", str(all_text.split("小\n中\n大\n")[1].split("更新時間")[0])).strip()

    article_time = sub_soup.select('div[class ="icon_time time leftBox2"]')[0].text.replace("/","-")

    # capture tag
    reg_tag = sub_soup.select('div[class="adWords"] a')
    web_tag = sub_soup.select('div[class="adWords"] a')[0].text
    for i in range(1, len(reg_tag)):
        web_tag += (';'+reg_tag[i].text)

    if content == '':
        content_exist = False
    else:
        content_exist = True

    # return chinatimes url content
    return content, web_tag, article_time, content_exist


def request_url(url):
   '''
   use url to request request
   :param url: url
   :return: request
   '''

   # call delay function, random 1 ~ 5 second
   delay(10)

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
      print("{}, {}, {}".format(now, "21.Unable to request data from web.", err))

      # if first requset error, delay 180 second
      t = 180
      time.sleep(t)

      if proxy != '':
         # print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

   except:
      # if request second error, program stop
      now = datetime.datetime.now()
      print("{}, {}".format(now, "22.Unable to request data again. STOP!"))
      sys.exit(0)

   # if request normal, return request
   return res

def delay(x=1):
   '''
   set system delay
   :param x: delay how many second
   :return: N/A
   '''

   # randon 1 ~ x second
   t = random.randint(1, x)

   # for delay loop
   for y in range(1, t+1):
      if y < t:
         # print("\rdelay {:>2d} 秒".format(t - y), end="")
         time.sleep(1)

if __name__ == "__main__":
    main()
