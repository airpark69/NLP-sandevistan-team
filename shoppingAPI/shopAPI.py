import os
import sys
import urllib.request
from urllib.error import URLError, HTTPError 
import json
import time
from functools import wraps

# 장시간 연결로 인한 에러 발생시 자동 재시도 코드
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry




client_id = "NAVER_client_id"
client_secret = "NAVER_client_secret"

# https://developers.naver.com/main/ 에서 발급 받은 id, secret




@retry((TimeoutError,URLError,HTTPError), tries=4, delay=15, backoff=2)
def search_shopping(query,start=1,display=100,word_list=[]):
    encText = urllib.parse.quote(query)
    url = "https://openapi.naver.com/v1/search/shop.json?query=" + encText\
        + "&display=" + str(display)\
        + "&start=" + str(start)  # JSON 결과
    # url = "https://openapi.naver.com/v1/search/shop.xml?query=" + encText # XML 결과
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id",client_id)
    request.add_header("X-Naver-Client-Secret",client_secret)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if(rescode==200):
        response_body = response.read()
        response_dict = json.loads(response_body.decode('utf-8'))
        for item in response_dict.get('items'):
            title = item.get('title')
            category2 = item.get('category2')
            category3 = item.get('category3')
            category4 = item.get('category4')
            data = "__label__" + category2 + "\t"\
                   "__label__" + category3 + "\t"\
                   "__label__" + category4 + "\t" + title + "\n"
            word_list.append(data)

        return word_list
    else:
        print("Error Code:" + rescode)

input_text = input("검색 값:")

word_list = []

for i in range(1, 31):
    search_shopping(input_text, start=i, word_list=word_list) ## 2번째 인자는 index 페이지, 100까지 for문 돌리면 10000개 나옴
text_dir = input_text + ".txt"

with open(text_dir, 'w', encoding='utf-8') as f:
            f.writelines(word_list)
            print(text_dir, "완료")