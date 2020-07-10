from bs4 import BeautifulSoup
import requests
import sys
import time
import random

def main():
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

    # capture tag
    tag = sub_soup.select('span[class="hash-tag"]')
    web_tag = tag[0].text.replace('#','')
    for y in range(1, len(tag)):
        web_tag += (';'+tag[y].text.replace('#',''))

    # return chinatimes url content
    return content, web_tag

def ltn_content(url):
    """

    :param url:
    :return:
    """
    res = request_url(url)
    sub_soup = BeautifulSoup(res.text, 'html.parser')

    all_text = sub_soup.select('div[class ="text"] p')
    drop_text = sub_soup.select('div[class ="text"] p[class]')

    content = ""
    for z in range(len(all_text)):
        if all_text[z] not in drop_text:
            content += (all_text[z].text+"\n")

    web_tag = ' '
    # return ltn url content
    return content, web_tag


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
   # print("\rrequest finish ")

if __name__ == "__main__":
    main()