from banana_project_news_web import chinatimes_list_crawler

if __name__ == '__main__':
    chinatimes_need_update, chinatimes_article_list = chinatimes_list_crawler.main()
print(chinatimes_need_update)
print(chinatimes_article_list)


