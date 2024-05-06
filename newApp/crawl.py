import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import pytz

def crawl_techrecipe():
    def parse_time(time_str):
        if '분' in time_str:
            return 0
        elif '시간' in time_str:
            return int(time_str.split(' ')[0])
        else:
            return 24

    news_data = []
    max_retries = 2

    page = 1
    while True:
        attempt = 0
        while attempt < max_retries:
            try:
                url = f"https://techrecipe.co.kr/category/news/page/{page}"
                res = requests.get(url)
                res.raise_for_status()
                soup = BeautifulSoup(res.text, "lxml")

                newsbox = soup.find_all('h2', attrs={"class": "entry-title h3"})
                newslink = [item.find('a')['href'] for item in newsbox]
                newsbox_date = soup.find_all('span', attrs={"class": "updated"})
                images = soup.find_all('img', attrs={"class": "attachment-gridlove-a4-orig size-gridlove-a4-orig wp-post-image"})

                times = [parse_time(date.text.strip()) for date in newsbox_date]
                page_end = False

                for index, (news, time, date, link) in enumerate(zip(newsbox, times, newsbox_date, newslink)):
                    if time >= 12:
                        page_end = True
                        break
                    url2 = f"{link}"
                    res2 = requests.get(url2)
                    res2.raise_for_status()
                    soup2 = BeautifulSoup(res2.text, "lxml")

                    description_div = soup2.find('div', class_ = 'entry-content')
                    paragraph_texts = [p.text for p in description_div.find_all('p')]
                    paragraph_texts_convert = " ".join(paragraph_texts)

                    image_src = images[index]['src']
                    seoul_tz = pytz.timezone('Asia/Seoul')
                    today_date = datetime.now(tz = seoul_tz).strftime('%H%M%S')
                    news_data.append({"title": news.text.strip(), "date": today_date, "image": image_src, "link": link, "description" : paragraph_texts_convert})

                if page_end:
                    break

                page += 1
                break 

            except requests.exceptions.RequestException as e:
                attempt += 1
                time.sleep(60)  # 1분 대기
                if attempt == max_retries:
                    raise Exception(f"Failed to fetch data after {max_retries} attempts for page {page}") from e

        if page_end or attempt == max_retries:
            break

    seoul_tz = pytz.timezone('Asia/Seoul')
    today_date = datetime.now(tz = seoul_tz).strftime('%Y%m%d')

    with open(f'media/news/TechRecipe/tech_recipe:{today_date}.json', 'w', encoding='utf-8') as file:
        json.dump(news_data, file, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    crawl_techrecipe()
