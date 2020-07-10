from banana_project_news_web import chinatimes_list_crawler
from banana_project_news_web import news_object
from banana_project_news_web import content_crawler

if __name__ == '__main__':

    # return article list and judge need update or not result
    chinatimes_article_list, chinatimes_need_update = chinatimes_list_crawler.main()

    #
    if chinatimes_need_update:
        for i in range(len(chinatimes_article_list)):
            reg_news = news_object.News()
            reg_news.allocation('chinatimes', chinatimes_article_list[i])
            reg_news.related = reg_news.related_or_not(content_crawler.chinatimes_content)
            reg_news.upload_to_db()
