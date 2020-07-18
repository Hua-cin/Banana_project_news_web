#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import datetime

start_time = datetime.datetime.now()
from Banana_news_module import chinatimes_list_crawler
from Banana_news_module import ettoday_list_crawler
from Banana_news_module import tvbs_list_crawler
from Banana_news_module import ltn_list_crawler
from Banana_news_module import news_object_corj
from Banana_news_module import content_crawler


def list_to_result(article_list):
    # if need, update chinatimes

    for i in range(len(article_list)):
        reg_news = news_object.News()
        reg_news.corj = "ckip"
        reg_news.allocation(article_list[len(article_list) - 1 - i])

        if article_list[0]['web_name'] == "ETtoday新聞雲":
            reg_news.related, content_exist = reg_news.kmeans_related(content_crawler.ettoday_content)

        elif article_list[0]['web_name'] == "TVBS新聞網":
            reg_news.related, content_exist = reg_news.kmeans_related(content_crawler.tvbs_content)

        elif article_list[0]['web_name'] == "中時電子報":
            reg_news.related, content_exist = reg_news.kmeans_related(content_crawler.chinatimes_content)

        elif article_list[0]['web_name'] == "自由時報":
            reg_news.related, content_exist = reg_news.kmeans_related(content_crawler.ltn_content)

        reg_news.knn_class()

        if content_exist:
            reg_news.upload_to_db()

    now = datetime.datetime.now()
    print("{}, 012.{} update finish.".format(now, article_list[0]['web_name']))


if __name__ == '__main__':

    now = datetime.datetime.now()
    print("\n{}, {}".format(now, "001.program start."))

    try:
        pass

        now = datetime.datetime.now()
        print("{}, 002.{} start confirm..".format(now, '中時電子報'))

        chinatimes_article_list = chinatimes_list_crawler.article_list()
        if len(chinatimes_article_list)>0:
            list_to_result(chinatimes_article_list)
        else:
            now = datetime.datetime.now()
            print("{}, 003.{} no need update..".format(now, '中時電子報'))

        # print('\n')

        now = datetime.datetime.now()
        print("{}, 004.{} start confirm..".format(now, '自由時報'))

        ltn_article_list = ltn_list_crawler.article_list()
        if len(ltn_article_list)>0:
            list_to_result(ltn_article_list)
        else:
            now = datetime.datetime.now()
            print("{}, 005.{} no need update..".format(now, '自由時報'))

        # print('\n')

        now = datetime.datetime.now()
        print("{}, 006.{} start confirm..".format(now, 'TVBS新聞網'))

        tvbs_article_list = tvbs_list_crawler.article_list()
        if len(tvbs_article_list)>0:
            list_to_result(tvbs_article_list)
        else:
            now = datetime.datetime.now()
            print("{}, 007.{} no need update..".format(now, 'TVBS新聞網'))

        # print('\n')

        now = datetime.datetime.now()
        print("{}, 008.{} start confirm..".format(now, 'ETtoday新聞雲'))

        ettoday_article_list = ettoday_list_crawler.article_list()
        if len(ettoday_article_list)>0:
            list_to_result(ettoday_article_list)
        else:
            now = datetime.datetime.now()
            print("{}, 009.{} no need update..".format(now, 'ETtoday新聞雲'))

        now = datetime.datetime.now()
        print("\n{}, {}".format(now, "001.program end."))

    except Exception as err:
        now = datetime.datetime.now()
        print("{}, {}, {}".format(now, "010.prgoram abnormal. STOP!", err))
        sys.exit(0)

    end_time = datetime.datetime.now()
    print("spend time = {}".format(end_time-start_time))