from banana_project_news_web import chinatimes_list_crawler
from banana_project_news_web import chinatimes_content_crawler

if __name__ == '__main__':

    # return article list and judge need update or not result
    chinatimes_article_list, chinatimes_need_update = chinatimes_list_crawler.main()

    #
    if chinatimes_need_update:
        for i in range(len(chinatimes_article_list)):
            a_term = chinatimes_content_crawler.News()
            a_term.web_name = 'chinatimes'
            a_term.publish_time = chinatimes_article_list[i]['publish_time']
            a_term.web_class = chinatimes_article_list[i]['web_class']
            a_term.title = chinatimes_article_list[i]['title']
            a_term.url = chinatimes_article_list[i]['url']
            a_term.related = a_term.related_or_not()
            a_term.upload_to_db()
