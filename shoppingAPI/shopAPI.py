import pandas as pd
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



#########################
client_id = "" 
client_secret = ""
# https://developers.naver.com/main/ 에서 발급 받은 id, secret



@retry((TimeoutError,URLError,HTTPError), tries=4, delay=15, backoff=2)
def search_shopping(query,start=1,display=100,word_df=pd.DataFrame()):
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
            row = []
            title = item.get('title')
            category2 = item.get('category2')
            category3 = item.get('category3')
            category4 = item.get('category4')
            row.append(title)
            row.append(category2)
            row.append(category3)
            row.append(category4)
            data = "__label__" + category2 + "\t"\
                   "__label__" + category3 + "\t"
            if category4 != '':
                data = data + "__label__" + category4 + "\t" + title + "\n"
            else:
                data = data + title + "\n"
            row.append(data)

            word_df.loc[word_df.shape[0]] = row

        return word_df
    else:
        print("Error Code:" + rescode)

#input_text = input("검색 값:")
input_list = ["김치", "반찬", "젓갈", "장류", "김", "튀각", "부각",\
              "과일", "견과류", "채소", "쌀", "잡곡","혼합곡", "건과류",\
              "쇠고기", "닭고기", "돼지고기","알류","축산가공식품","육류","양고기","오리고기",\
              "한방재료", "건강분말", "건강즙","과일즙", "꿀", "인삼", "홍삼", "건강환/정", "영양제", "비타민제", "환자식","영양보충식",\
              "통조림", "황도", "참치","연어", "골뱅이","번데기", "햄", "피클","올리브", "옥수수","콩", "꽁치","고등어",\
              "차류", "주스","과즙음료", "전통차","차음료", "건강음료","기능성음료", "우유","요구르트", "커피", "탄산음료", "코코아", "파우더","스무디", "두유","탄산수","제로음료",\
              "장아찌", "반찬류", "절임류", "조림류", "볶음류", "장조림",\
              "초콜릿", "떡", "스낵", "한과", "과자","쿠키","아이스크림","빙수", "가공안주류", "빵", "강정", "팝콘","강냉이류", "시리얼", "젤리", "전병", "엿", "푸딩", "사탕", "화과자", "베이커리","껌",\
              "건어물", "김","해초", "해산물","어패류", "생선", "수산가공식품", "젓갈","장류","조개류","게","갑각류","오징어","연체류","날치알","해삼","멍게",\
              "고추장", "양념장", "된장", "청국장", "쌈장", "간장", "장류", "매주",\
              "냉동식품","간편조리식품", "즉석국","즉석탕", "만두", "어묵", "튀김류", "누룽지", "즉석밥", "샐러드", "스프", "죽", "카레","짜장", "채식푸드", "떡볶이", "피자", "핫도그", "딤섬", "도시락", "햄버거",\
              "조미료", "고춧가루", "소금", "고추냉이", "식초", "물엿","올리고당", "겨자", "액젓", "설탕", "후추", "천연감미료",\
              "분말가루", "콩가루", "오트밀", "찹쌀가루", "쌀가루", "밀가루", "부침가루", "빵가루", "튀김가루",\
              "소스","드레싱","잼","시럽",\
              "치즈", "마가린", "버터", "생크림", "휘핑크림", "연유",\
              "콜라겐", "단백질보충제", "헬스보충제", "다이어트보조제", "곤약", "히알루론산", "식이섬유", "다이어트차", "다이어트식품",\
              "라면", "면류", "간식", "디저트", "구이", "밥","죽", "볶음", "튀김", "조림", "찜", "찌개", "국",\
              "샐러드", "닭가슴살", "만두", "딤섬", "햄버거", "맛살", "게살", "함박", "미트볼", "채식푸드",\
              "식용유", "오일","가루","분말류","향신료","제과재료","제빵재료",\
              "전통주"]
word_df = pd.DataFrame(columns=['title', 'cate1', 'cate2', 'cate3', 'text'])

for input in input_list:
    for i in range(1, 21):
        search_shopping(input, start=i, word_df=word_df) ## 2번째 인자는 index 페이지, 100까지 for문 돌리면 10000개 나옴
    print(input, "완료")

text_dir = "Naver_dataset.csv"

word_df.to_csv(text_dir, index=False)

# with open(text_dir, 'w', encoding='utf-8') as f:
#             f.writelines(word_list)
#             print(text_dir, "최종 완료")