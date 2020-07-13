from banana_project_news_web import chinatimes_list_crawler
from banana_project_news_web import ltn_list_crawler
from banana_project_news_web import ltn_list_crawler_for_tag
from banana_project_news_web import news_object_add_knn
from banana_project_news_web import content_crawler

if __name__ == '__main__':

    # update chinatimes news-------------------------------------------------------------------------------------------
    # return article list and judge need update or not result
    chinatimes_article_list, chinatimes_need_update = chinatimes_list_crawler.ltn_list()

    # if need, update chinatimes
    if chinatimes_need_update:
        for i in range(len(chinatimes_article_list)):
            reg_news = news_object_add_knn.News()
            reg_news.allocation('chinatimes', chinatimes_article_list[i])
            reg_news.related, content_exist = reg_news.related_or_not(content_crawler.chinatimes_content)
            if content_exist:
                # reg_news.class_function()
                reg_news.upload_to_db()

        print("chinatimes update finish!!")
    else:
        print("chinatimes no need update!!")

    # # update ltn news-------------------------------------------------------------------------------------------------
    ltn_for_tag = False

    # return article list and judge need update or not result
    # choice which type webpage for ltn web
    if ltn_for_tag: # for have tag web
        ltn_article_list, ltn_need_update = ltn_list_crawler_for_tag.ltn_list()
    else:
        ltn_article_list, ltn_need_update = ltn_list_crawler.ltn_list()

    # if need, update chinatimes
    if ltn_need_update:
        for i in range(len(ltn_article_list)):
            reg_news = news_object_add_knn.News()
            reg_news.allocation('ltn', ltn_article_list[i])
            reg_news.related, content_exist = reg_news.related_or_not(content_crawler.ltn_content)
            if content_exist:
                # reg_news.class_function()
                reg_news.upload_to_db()

        print("ltn update finish!!")
    else:
        print("ltn no need update!!")

