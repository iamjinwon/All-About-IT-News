from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News, SummarizeNews

# .env 파일 경로 명시
dotenv_path = os.path.join(project_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

def summarize_gpt(system_prompt, news_content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": news_content},
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
    return result

def summarize_articles():
    system_prompt = """
        You're a great news summarization bot: summarize a given news story in 3 sentences.

        [Rules]
        - Answers MUST always be in Korean.
        - You must THINK about the summarization process STEP BY STEP.
        - You MUST only answer in 3 sentences.
        - Answers MUST not be duplicated.
        - Your answers MUST follow the [Output Format].

        [Output Format]
        (1)
        (2)
        (3)
        """.strip()

    seoul_tz = pytz.timezone('Asia/Seoul')
    today_start = datetime.combine(datetime.now(seoul_tz).date(), time.min).astimezone(seoul_tz)
    today_end = datetime.combine(datetime.now(seoul_tz).date(), time.max).astimezone(seoul_tz)

    # News 테이블에서 오늘 날짜의 news_id와 description을 가져오기
    news_data = News.objects.filter(created_dt__range=(today_start, today_end))

    if not news_data.exists():
        print("No news articles found for today's date.")
        return

    for news in news_data:
        description = news.description
        news_id = news.news_id

        summarize = summarize_gpt(system_prompt, description)
        summary_lines = summarize.strip().split('\n')
        
        summary_dict = {
            "news_id": news_id,
            "first_sentence": summary_lines[0].strip().lstrip('(1) '),
            "second_sentence": summary_lines[1].strip().lstrip('(2) '),
            "third_sentence": summary_lines[2].strip().lstrip('(3) '),
            "created_dt": datetime.now(seoul_tz)  # 현재 로컬 시간 저장
        }

        # SummarizeNews 테이블에 news_id가 이미 있는지 확인하고, 업데이트 또는 생성
        summarize_news_obj, created = SummarizeNews.objects.update_or_create(
            news_id=news_id,
            defaults=summary_dict
        )
        if created:
            print(f"Created new summary for news_id {news_id}")
        else:
            print(f"Updated existing summary for news_id {news_id}")

if __name__ == "__main__":
    summarize_articles()
