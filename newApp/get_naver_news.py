import os
import sys
import urllib.request

client_id = "BGOuVLWleJtZcnu4lGc3"
client_secret = "E5QYbEP2a8"

encText = urllib.parse.quote("인공지능") # quote가 뒤에 부분을 UTF-8로 인코딩해줌

url = "https://openapi.naver.com/v1/search/news?query=" + encText # JSON 결과

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)
response = urllib.request.urlopen(request)
rescode = response.getcode()
if(rescode==200):
    response_body = response.read()
    print(response_body.decode('utf-8'))
else:
    print("Error Code:" + rescode)

