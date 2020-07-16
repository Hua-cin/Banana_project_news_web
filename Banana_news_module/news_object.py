#!/usr/bin/python3
# -*- coding: utf-8 -*-

import requests
import MySQLdb
import datetime
import time
import re
from sklearn import cluster
import jieba
import jieba.analyse
import pandas as pd
import math
import json
import sys
import os


exec_file_path = '/home/lazyso/anaconda3/envs/AutoNewsenv/banana_project_news_web'
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
        self.output_class = ''
        self.content = ''

    def allocation(self, row_dict):
        """
        method for allocation recipe to object
        :param self:
        :param web: web name
        :param row_dict: article_item
        :return: N/A
        """

        self.web_name = row_dict['web_name']
        self.web_class = row_dict['web_class']
        self.publish_time = row_dict['publish_time']
        self.title = row_dict['title']
        self.url = row_dict['url']

    def kmeans_related(self, func_content):
        """
        method for confirm content related banana or not
        :param self:
        :param func_content: call cotent function, chinatimes_content, ltn_content ...
        :return: 1 = True, 0 = False
        """

        # call content_function to request content
        self.content, self.web_tag , article_time, content_exist = func_content(self.url)

        # update publish_time after content confirm
        if article_time != 0 :
            self.publish_time = article_time

        # fetch base data, list have dict
        base = pd.read_csv(r'{}/ref_data/base.csv'.format(exec_file_path))
        base_dict_list = base.to_dict('records')

        # call jieba function, and get wordcut dict
        sample_dict = func_jieba(self.content)

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
                # print("無相關")
                result = 0
            elif cluster_labels[1] == cluster_labels[2]:
                # print("無相關")
                result = 0
            else:
                # print("相關")
                result = 1
        else:
            # print("無相關")
            result = 0

        # trainset_tf, trainset_class, seg_corpus = load_news_data()
        # input_tf = get_article_vector(self.content, seg_corpus)
        # self.output_class = knn_classify(input_tf, trainset_tf, trainset_class, k=3)
        # print("class = {}".format(self.output_class))

        # print result and title
        print(self.title)
        print(self.url)
        print("|{}|\n".format(self.content))
        if result == 1:
            print("相關")
        else:
            print("無相關")
        print("-----------------")

        # return judgt result
        return result, content_exist


    def knn_class(self):
        trainset_tf, trainset_class, seg_corpus = load_news_data()
        input_tf = get_article_vector(self.content, seg_corpus)
        self.output_class = knn_classify(input_tf, trainset_tf, trainset_class, k=3)
        print("class = {}".format(self.output_class))
        print("------------------------------------------------------------------------------------------")


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
            sql_str = 'insert into Daniel_news (web_name, publish_time, web_class, title, url, related, output_class, web_tag, log_dt) ' \
                      'values(\'{}\', \'{}\', \'{}\', \'{}\', \'{}\',\'{}\', \'{}\', \'{}\', \'{}\');' \
                .format(self.web_name, self.publish_time, self.web_class, self.title, self.url, self.related, self.output_class, self.web_tag, now)

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


# for knn
# |
# Y
def df_to_json():

    path = '{}/ref_data/article_lib'.format(exec_file_path)
    file_list = os.listdir(path)

    columns = ["category", "title", "content"]
    news_total_data = []

    for i in file_list:

        c = i.split('_')[1].split('相關')[0]

        path_title = path + '/' + i
        file_title = os.listdir(path_title)

        for y in file_title:
            news_data = []
            t = y.split('_')[1].split('.')[0]
            new_content = path_title + '/' + y
            with open(new_content, 'r', encoding='utf-8') as f:
                a = f.read()

            news_data.append(c)
            news_data.append(t)
            news_data.append(a)
            news_total_data.append(news_data)

    new_df = pd.DataFrame(columns=columns)
    new_df = new_df.append(pd.DataFrame(news_total_data, columns=columns))

    new_df_json = new_df.to_json(orient="records", force_ascii=False)

    return (new_df_json)

def load_news_data():
    """
    新聞資料當作測試資料，產生訓練集向量與訓練集分類。
    :return: 訓練集的向量及訓練集分類
    """

    training_set_tf = {}
    training_set_class = {}
    keywords = []

    news_data = json.loads(df_to_json())

    for news in news_data:
        training_set_class[news['title']] = news['category']
        # 保存每篇文章詞彙出現次數
        jieba.analyse.set_stop_words('{}/ref_data/stopword.txt'.format(exec_file_path))
        seg_list = jieba.analyse.extract_tags(news['content'], topK=100)

        seg_content = {}
        for seg in seg_list:
            if seg in seg_content:
                seg_content[seg] += 1
            else:
                seg_content[seg] = 1
        # 保存文章詞彙頻率
        training_set_tf[news['title']] = seg_content
        # 獲取關鍵詞
        keywords.extend(jieba.analyse.extract_tags(news['content'], topK=100))
    # 文章斷詞轉成向量表示
    seg_corpus = list(set(keywords))
    for title in training_set_tf:
        tf_list = list()
        for word in seg_corpus:
            if word in training_set_tf[title]:
                tf_list.append(training_set_tf[title][word])
            else:
                tf_list.append(0)
        training_set_tf[title] = tf_list

    return (training_set_tf, training_set_class, seg_corpus)

def get_article_vector(content, seg_corpus):
    """
    計算要測試的文章向量。
    :param content: 文章內容
    :param seg_corpus: 新聞關鍵詞彙語料庫
    :return: 文章的詞頻向量
    """

    seg_content = {}
    jieba.analyse.set_stop_words('{}/ref_data/stopword.txt'.format(exec_file_path))
    seg_list = jieba.analyse.extract_tags(content, topK = 100)
    for seg in seg_list:
        if seg in seg_content:
            seg_content[seg] += 1
        else:
            seg_content[seg] = 1
    #產生vector
    tf_list = []
    for word in seg_corpus:
        if word in seg_content:
            tf_list.append(seg_content[word])
        else:
            tf_list.append(0)
    return tf_list

def cosine_similarity(v1, v2):
    """
    計算兩個向量的cosine similarity。數值越高表示距離越近，也代表越相似，範圍為0.0~1.0。
    :param v1: 輸入向量1
    :param v2: 輸入向量2
    :return: 2個向量的正弦相似度
    """
    #compute cosine similarity of v1 to v2: (v1 dot v2)/{||v1||*||v2||)
    sum_xx, sum_xy, sum_yy = 0.0, 0.0, 0.0
    for i in range(0, len(v1)):
        x, y = v1[i], v2[i]
        sum_xx += math.pow(x, 2)
        sum_yy += math.pow(y, 2)
        sum_xy += x * y
    try:
        return sum_xy / math.sqrt(sum_xx * sum_yy)
    except ZeroDivisionError:
        return 0

def knn_classify(input_tf, trainset_tf, trainset_class, k):
    """
    kNN分類演算法。
    :param input_tf: 輸入向量
    :param trainset_tf: 訓練集的向量
    :param trainset_class: 訓練集的分類
    :param k: 決定最近鄰居取k個
    :return:
    """
    tf_distance = {}
    # 計算每個訓練集合特徵關鍵字頻率向量和輸入向量的距離
    # print('1.計算向量距離')
    for position in trainset_tf.keys():
        tf_distance[position] = cosine_similarity(trainset_tf.get(position), input_tf)
        '''
        print('\tDistance(%s) = %f' % (
        position.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding), tf_distance.get(position)))
        '''
    # 取出k個最近距離的分類
    class_count = {}
    # print('2.K個最近鄰居的分類, k = %d' % k)
    for i, position in enumerate(sorted(tf_distance, key=tf_distance.get, reverse=True)):
        current_class = trainset_class.get(position)
        '''
        print('\t(%s) = %f, class = %s' % (
        position.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding), tf_distance.get(position),
        current_class))
        '''
        # 將最接近的鄰居之分類做加權
        if i == 0:
            class_count[current_class] = class_count.get(current_class, 0) + 2
        else:
            class_count[current_class] = class_count.get(current_class, 0) + 1
        if (i + 1) >= k:
            break

    # print('3.依K個最近鄰居中出現最高頻率的作分類')
    input_class = ''
    l=[]

    for i, c in enumerate(sorted(class_count, key=class_count.get, reverse=True)):
        if i == 0:
            input_class = c
        print('\t%s, %d' % (c, class_count.get(c)))
        l.append(c)
    # print('4.分類結果 = %s' % input_class)

    y = ''
    for x in l:
        y += x + " "
    # print(y.strip())

    return y

if __name__ == "__main__":
    """
    main function
    """
    main()