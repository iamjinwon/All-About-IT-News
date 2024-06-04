from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, timedelta

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News

# .env 파일 경로 명시
dotenv_path = os.path.join(project_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

def make_output(system_prompt, content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content.strip()
    total_tokens = response.usage.total_tokens  # 사용된 전체 토큰 수
    return result, total_tokens

def update_crucial_articles():
    system_prompt = """
    You're task is to select the 5 most useful articles from a collection of articles.

    [Rules]
    - Answers MUST always be in Korean.
    - The given text is the body of the article and news_id.
    - The primary audience for this article is people in IT-related industries.
    - You MUST answer only with the news_id.
    - Answers MUST not be duplicated.

    [Output Format]
    , , , , 
    """.strip()

    today_start = datetime.combine(datetime.now().date(), datetime.min.time())
    today_end = datetime.combine(datetime.now().date(), datetime.max.time())

    # News 테이블에서 오늘 날짜의 news_id와 description을 가져오기
    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id', 'description')

    # 디버깅: 가져온 데이터 출력
    print(f"News data: {news_data}")

    if not news_data:
        print("No news articles found for today's date.")
        return [], 0

    # 기사 요약을 만들기 위한 데이터 준비
    content = "\n".join([f"{news_id}: {description[:100]}" for news_id, description in news_data])

    # OpenAI API를 사용하여 주요 기사 5개를 선택
    selected_news_ids_str, total_tokens = make_output(system_prompt, content)

    # 응답 디버깅 출력
    print(f"Response: {selected_news_ids_str}")

    try:
        # 문자열에서 news_id 추출
        selected_news_ids = [int(news_id.strip()) for news_id in selected_news_ids_str.split(',')]
    except ValueError as e:
        print(f"Error parsing selected news ids: {e}")
        # 응답이 예상한 형식이 아닌 경우 디버깅을 위한 출력을 추가
        print(f"Response content was not in the expected format: {selected_news_ids_str}")
        return [], total_tokens

    # 선택된 기사들의 crucial 필드를 True로 업데이트
    News.objects.filter(news_id__in=selected_news_ids).update(crucial=True)

    return selected_news_ids, total_tokens

if __name__ == "__main__":
    selected_ids, total_tokens = update_crucial_articles()
    print(f"Selected News IDs: {selected_ids}")
    print(f"Total Tokens Used: {total_tokens}")
