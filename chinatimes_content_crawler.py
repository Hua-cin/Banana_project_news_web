from bs4 import BeautifulSoup
import requests
import MySQLdb
import datetime
import sys
import time
import random
import re
import os
import jieba
import pandas as pd
from sklearn import cluster
from banana_project_news_web import chinatimes_request_content

class News:
    """ a news class """
    def __init__(self):
        self.web_name = ''
        self.publish_time = ''
        self.web_class = ''
        self.title= ''
        self.url = ''
        self.related = 99

    def allocation(self, web, article_dict):
        self.web_name = web
        self.publish_time = article_dict['publish_time']
        self.web_class = rticle_dict['web_class']
        self.title = rticle_dict['title']
        self.url = rticle_dict['url']


    def related_or_not(self):
        '''

        :return:
        '''

        content = chinatimes_request_content.chinatimes_content(self.url)
        # res = request_url(self.url)
        #
        # sub_soup = BeautifulSoup(res.text, 'html.parser')
        # all_text = sub_soup.select('div[class ="col-xl-11"] p')
        # content = ""
        # for j in range(len(all_text)):
        #     content += all_text[j].text
        #     if all_text[j].text != '':
        #         content += "\n"

        base = pd.read_csv(r'{}/01_ref_data/base.csv'.format(os.getcwd()))
        base_dict_list = base.to_dict('records')
        print(base_dict_list)

        reg_dict = func_jieba(content)
        print(reg_dict)

        if '香蕉' in reg_dict:
            banana_times = reg_dict['香蕉']
        else:
            banana_times =0

        if '香蕉' in reg_dict:
            del reg_dict['香蕉']

        base_dict_list.append(reg_dict)

        columns = []
        for i in range(2):
            columns = comb_key(columns, base_dict_list[i])

        late = pd.DataFrame(data=base_dict_list, columns=columns)

        # late dataframe 空值補0
        late = late.fillna(0)

        for z in late:
            if late.loc[1, z] < 0:
                late.loc[2, z] = late.loc[2, z] * (-1)

        print(late)
        # KMeans 演算法
        kmeans_fit = cluster.KMeans(n_clusters=2).fit(late)

        # 印出分群結果
        cluster_labels = kmeans_fit.labels_

        print("\n----------------")
        print("{}\n分群結果：\n{}".format(2, cluster_labels))

        # 判定結果
        if banana_times > 1:
            if cluster_labels[0] == cluster_labels[1]:
                print("無相關")
                result = 0
            elif cluster_labels[1] == cluster_labels[2]:
                print("無相關")
                result = 0
            else:
                print("相關")
                result = 1
        else:
            print("無相關")
            result = 0
        return result

    def upload_to_db(self):
        """insert data"""

        db = connect_db()
        cursor = db.cursor()  # create cursor

        try:
            db.autocommit(False)  # setup autocommit false

            now = datetime.datetime.now()
            sql_str = 'insert into Daniel_news_test (web_name, publish_time, web_class, title, url, related, log_dt) ' \
                      'values(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\',\'{}\', \'{}\');' \
                .format(self.web_name, self.publish_time, self.web_class, self.title, self.url, self.related, now)
            cursor.execute(sql_str)  # start insert data
            db.autocommit(True)  # setup autocommit true
            db.close()

        except Exception as err:
            db.close()
            print(err)
def main():
    pass

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

# def delay(x=1):
#    '''
#    set system delay
#    :param x: delay how many second
#    :return:
#    '''
#
#    # randon 1 ~ x second
#    t = random.randint(1, x)
#
#    # for delay loop
#    for y in range(1, t+1):
#       if y < t:
#          # print("\rdelay {:>2d} 秒".format(t - y), end="")
#          time.sleep(1)
#    # print("\rrequest finish ")

def connect_db():
    """connect database"""

    # fetch key_word
    key_word = pd.read_csv(r'{}/01_ref_data/key_word.csv'.format(os.getcwd()))

    db = MySQLdb.connect(host=str(key_word.loc[0, 'host']),
                         user=str(key_word.loc[0, 'user']),
                         passwd=str(key_word.loc[0, "passwd"]),
                         db=str(key_word.loc[0, "db"]),
                         port=int(key_word.loc[0, "port"]),
                         charset=str(key_word.loc[0, "charset"]))
    return db  # return db name

def func_jieba(text):
    '''
    :param text:
    :return: word count dict
    '''

    # insert stopword list
    stopword_path = r'./01_ref_data/stopword.txt'
    stopword_list = []
    with open(stopword_path, 'r', encoding='utf-8') as f_stop:
        for temp in f_stop.readlines():
            stopword_list.append(temp.replace('\n', ''))
    # print(stopword_list)

    jieba.load_userdict(r'./01_ref_data/mydict.txt')
    s = jieba.cut(text)
    jieba_word_count = {}
    for i in s:
        if i in jieba_word_count:
            jieba_word_count[i] += 1
        else:
            jieba_word_count[i] = 1

    jieba_word = [(k, jieba_word_count[k]) for k in jieba_word_count if (len(k) > 1) and (k not in stopword_list) and not re.match(r'[0-9a-zA-Z]+',k)]
    jieba_word.sort(key=lambda item: item[1], reverse=True)

    jieba_dict = {}

    for i in jieba_word:
        jieba_dict[i[0]] =i [1]
    # del jieba_dict['香蕉']

    return jieba_dict

def comb_key(list, dict_list):
    """
    :param list: before list
    :param dict_list: article dict
    :return: after modify list
    """
    for j in dict_list:
        if j in list:
            pass
        else:
            list.append(j)
    return list

if __name__ == "__main__":
    main()