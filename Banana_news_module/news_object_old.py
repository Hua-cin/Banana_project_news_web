import requests
import MySQLdb
import datetime
import sys
import time
import re
import os
import jieba
import pandas as pd
from sklearn import cluster


exec_file_path = '/home/lazyso/Autonews'
exec_file_path = os.getcwd()

class News:
    """
    a new News object
    """

    def __init__(self):
        """
        init object
        """

        self.web_name = ''
        self.publish_time = ''
        self.web_class = ''
        self.title= ''
        self.url = ''
        self.web_tag = ''
        self.related = 99


    def allocation(self, web, row_dict):
        """
        method for allocation recipe to object
        :param self:
        :param web: web name
        :param row_dict: article_item
        :return: N/A
        """

        self.web_name = web
        self.web_class = row_dict['web_class']
        self.publish_time = row_dict['publish_time']
        self.title = row_dict['title']
        self.url = row_dict['url']

    def related_or_not(self, func_content):
        """
        method for confirm content related banana or not
        :param self:
        :param func_content: call cotent function, chinatimes_content, ltn_content ...
        :return: 1 = True, 0 = False
        """

        # call content_function to request content
        content, self.web_tag , article_time, content_exist = func_content(self.url)

        # update publish_time after content confirm
        if article_time != 0 :
            self.publish_time = article_time

        # fetch base data, list have dict
        base = pd.read_csv(r'{}/ref_data/base.csv'.format(exec_file_path))
        base_dict_list = base.to_dict('records')

        # call jieba function, and get wordcut dict
        sample_dict = func_jieba(content)

        # fetch how many '香蕉' times in sample
        if '香蕉' in sample_dict:
            banana_times = sample_dict['香蕉']
        else:
            banana_times = 0

        # remove '香蕉' item from sample dict
        if '香蕉' in sample_dict:
            del sample_dict['香蕉']

        # copy a work list
        work_list = base_dict_list
        work_list.append(sample_dict)

        # fetch work columns
        columns = []
        for i in range(2):
            # call combine key function to fetch columns
            columns = comb_key(columns, work_list[i])

        # create a work dataframe for K-means use
        work_df = pd.DataFrame(data=work_list, columns=columns)

        # work_df dataframe null to 0
        work_df = work_df.fillna(0)

        # modify factor
        for z in work_df:
            if work_df.loc[1, z] < 0:
                work_df.loc[2, z] = work_df.loc[2, z] * (-1)

        # KMeans 演算法
        kmeans_fit = cluster.KMeans(n_clusters=2).fit(work_df)

        # fetch cluster result
        cluster_labels = kmeans_fit.labels_

        # judge the latest result
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
        # print result and title
        print(self.title)
        print(self.url)
        print("**")
        print("|{}|".format(content))
        print("-----------------")

        # return judgt result
        return result, content_exist

    def upload_to_db(self):
        """
        uplode data after judgement
        :return: N/A
        """

        # create a db connect
        db = connect_db()
        cursor = db.cursor()  # create cursor

        try:
            # setup autocommit false
            db.autocommit(False)
            now = datetime.datetime.now()
            sql_str = 'insert into Daniel_news_test (web_name, publish_time, web_class, title, url, related, web_tag, log_dt) ' \
                      'values(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\',\'{}\', \'{}\', \'{}\');' \
                .format(self.web_name, self.publish_time, self.web_class, self.title, self.url, self.related, self.web_tag, now)

            # execute insert data
            cursor.execute(sql_str)

            # setup autocommit True
            db.autocommit(True)

            # close db connect
            db.close()

        except Exception as err:
            # close db connect
            db.close()
            now = datetime.datetime.now()
            print("{}, {}, {}".format(now, "11.upload to db abnormal. STOP!", err))
            sys.exit(0)

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
         # print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

   except Exception as err:
      now = datetime.datetime.now()
      print("{}, {}, {}".format(now, "12.Unable to request data from web.", err))

      # if first requset error, delay 180 second
      t = 180
      time.sleep(t)

      if proxy != '':
         # print("proxy = True")
         res = requests.get(url, headers=headers, proxies=proxies)
      else:
         res = requests.get(url, headers=headers)

      now = datetime.datetime.now()
      print("{}, {}".format(now, "13.Request data normal, continue program."))

   except:
      # if request second error, program stop
      now = datetime.datetime.now()
      print("{}, {}".format(now, "14.Unable to request data again. STOP!"))
      sys.exit(0)

   # if request normal, return request
   return res

def connect_db():
    """connect database"""

    # fetch key_word
    key_word = pd.read_csv(r'{}/ref_data/key_word.csv'.format(exec_file_path))

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

    # fetch stop word list
    stopword_path = r'{}/ref_data/stopword.txt'.format(exec_file_path)
    stopword_list = []
    with open(stopword_path, 'r', encoding='utf-8') as f_stop:
        for temp in f_stop.readlines():
            stopword_list.append(temp.replace('\n', ''))

    # fetch mydict list
    jieba.load_userdict(r'{}/ref_data/mydict.txt'.format(exec_file_path))
    s = jieba.cut(text)
    jieba_word_count = {}
    for i in s:
        if i in jieba_word_count:
            jieba_word_count[i] += 1
        else:
            jieba_word_count[i] = 1
    # filter jieba wordcut list by user define
    jieba_word = [(k, jieba_word_count[k]) for k in jieba_word_count if (len(k) > 1) and (k not in stopword_list) and not re.match(r'[0-9a-zA-Z]+',k)]

    # sort jieba wordcut list
    jieba_word.sort(key=lambda item: item[1], reverse=True)

    # init jieba wordcut dict
    jieba_dict = {}

    # insert data to jieba wordcut dict
    for i in jieba_word:
        jieba_dict[i[0]] =i [1]

    # return word cut result by dict
    return jieba_dict

def comb_key(list, dict_list):
    """
    to get distinct key for muti dict
    :param list: before list
    :param dict_list: article dict
    :return: after modify list
    """

    for j in dict_list:
        if j in list:
            pass
        else:
            list.append(j)
    # return distinct key list
    return list

if __name__ == "__main__":
    """
    main function
    """
    main()

