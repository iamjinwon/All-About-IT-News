import os
import sys
import urllib.request
import json
from datetime import datetime
import pytz

client_id = "BGOuVLWleJtZcnu4lGc3"
client_secret = "E5QYbEP2a8"

encText = urllib.parse.quote("인공지능") 

url = "https://openapi.naver.com/v1/search/news?query=" + encText # JSON 결과

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    response_json = json.loads(response_body.decode('utf-8'))

    seoul_tz = pytz.timezone('Asia/Seoul')
    today_date = datetime.now(tz = seoul_tz).strftime('%Y%m%d')
    today_news = [item for item in response_json['items'] if datetime.strptime(item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').strftime('%Y%m%d') == today_date]
    
    # 하나라도 오늘날짜와 다른 뉴스가 포함되있는지 확인
    # for news_item in today_news:
    #     if datetime.strptime(news_item['pubDate'], '%a, %d %b %Y %H:%M:%S +0900').strftime('%Y%m%d') != today_date:
    #         print(True)
    #         break
    # else:
    #     print(False)

    with open(f'media/news/naver/{today_date}.json', 'w') as f:
        json.dump(today_news, f, indent=4, ensure_ascii=False)
else:
    print("Error Code:" + rescode)

