class News:
    """ a news class """
    def __init__(self):
        self.web_name = ''
        self.publish_time = ''
        self.web_class = ''
        self.title= ''
        self.url = ''
        self.content = ''

    def related(self):
        print(self.content)
        return self.url


a= News()
a.content = 123
print(a.content)

b = News()
print(b.content)
