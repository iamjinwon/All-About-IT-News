import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import time
import django
import os
import sys

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News
SEOUL_TZ = pytz.timezone('Asia/Seoul')
MAX_RETRIES = 2
PAGE_LIMIT_HOURS = 12

def parse_time(time_str):
    now = datetime.now(tz=SEOUL_TZ)
    if '분' in time_str:
        minutes = int(time_str.split(' ')[0])
        return now - timedelta(minutes=minutes)
    elif '시간' in time_str:
        hours = int(time_str.split(' ')[0])
        return now - timedelta(hours=hours)
    else:
        return now - timedelta(days=1)

def fetch_page(url):
    attempt = 0
    while attempt < MAX_RETRIES:
        try:
            res = requests.get(url)
            res.raise_for_status()
            return BeautifulSoup(res.text, "lxml")
        except requests.exceptions.RequestException as e:
            attempt += 1
            time.sleep(60)  # 1분 대기
            if attempt == MAX_RETRIES:
                raise Exception(f"Failed to fetch data after {MAX_RETRIES} attempts for URL: {url}") from e

def is_page_end(time):
    return (datetime.now(tz=SEOUL_TZ) - time).total_seconds() >= PAGE_LIMIT_HOURS * 3600

def crawling():
    page = 1

    while True:
        url = f"https://techrecipe.co.kr/category/news/page/{page}"
        soup = fetch_page(url)

        newsbox = soup.find_all('h2', attrs={"class": "entry-title h3"})
        newslink = [item.find('a')['href'] for item in newsbox]
        newsbox_date = soup.find_all('span', attrs={"class": "updated"})
        images = soup.find_all('img', attrs={"class": "attachment-gridlove-a4-orig size-gridlove-a4-orig wp-post-image"})

        times = [parse_time(date.text.strip()) for date in newsbox_date]
        page_end = False

        for index, (news, time, link) in enumerate(zip(newsbox, times, newslink)):
            if is_page_end(time):
                page_end = True
                break
            if "위클리" in news.text:
                continue 
            
            soup2 = fetch_page(link)

            description_div = soup2.find('div', class_ = 'entry-content')
            paragraph_texts = [p.text for p in description_div.find_all('p')]
            paragraph_texts_convert = " ".join(paragraph_texts)

            image_src = images[index]['src']

            # 데이터베이스에 저장
            News.objects.create(
                title=news.text.strip(),
                date=time,
                image=image_src,
                link=link,
                description=paragraph_texts_convert
            )

        if page_end:
            break
        
        page += 1

# 실행 예제
if __name__ == "__main__":
    crawling()
