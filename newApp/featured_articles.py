from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz

# 경로 설정
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News, Gpt  # Gpt 모델 추가

# 환경 변수 로드
dotenv_path = os.path.join(project_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

def make_output(system_prompt, content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
        temperature=0.7
    )

    result = response.choices[0].message.content.strip()
    input_tokens = response.usage.prompt_tokens  # 수정된 부분
    output_tokens = response.usage.completion_tokens  # 수정된 부분
    total_tokens = response.usage.total_tokens  # 수정된 부분
    return result, input_tokens, output_tokens, total_tokens

def calculate_cost(model, input_tokens, output_tokens):
    if model == "gpt-4o":
        input_cost_per_token = 5 / 1_000_000  # 1백만 토큰당 $5
        output_cost_per_token = 15 / 1_000_000  # 1백만 토큰당 $15
        cost = (input_cost_per_token * input_tokens) + (output_cost_per_token * output_tokens)
        return cost
    else:
        raise ValueError("Unsupported model")

def update_crucial_articles():
    system_prompt = """
Your task is to find interesting articles by looking at the title of the article and focusing on IT-related information, the latest technology, social issues, etc.

[Rules]
- You MUST pick 5 articles and answer them by news_id.
- The given texts are the titles of the articles
- The primary audience for this article is people in IT-related industries.
- Answers MUST not be duplicated.
- You MUST draw 5 articles, or all of them if you have fewer.
- You only need to call the news_id.
- The response MUST follow the output format

[Output format]
1, 2, 3, 4, 5
""".strip()

    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    today_start = datetime.combine(now.date(), time.min).astimezone(seoul_tz)
    today_end = datetime.combine(now.date(), time.max).astimezone(seoul_tz)

    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id', 'title')

    if not news_data:
        print("No news articles found for today's date.")
        return [], 0

    content = "\n".join([f"{news_id}: {title}" for news_id, title in news_data])

    selected_news_ids_str, fe_input_tokens, fe_output_tokens, fe_total_tokens = make_output(system_prompt, content)

    try:
        selected_news_ids = [int(news_id.strip()) for news_id in selected_news_ids_str.split(',')]
    except ValueError as e:
        print(f"Error parsing selected news ids: {e}")
        print(f"Response content was not in the expected format: {selected_news_ids_str}")
        return [], fe_total_tokens

    # 비용 계산
    fe_cost = calculate_cost("gpt-4o", fe_input_tokens, fe_output_tokens)

    # GPT 테이블에 데이터 삽입
    for news_id in selected_news_ids:
        Gpt.objects.update_or_create(
            news_id=news_id,
            defaults={
                'fe_input_tokens': fe_input_tokens,
                'fe_output_tokens': fe_output_tokens,
                'fe_total_tokens': fe_total_tokens,
                'fe_cost': fe_cost,
            }
        )

    # News 테이블의 crucial 컬럼 업데이트
    News.objects.filter(news_id__in=selected_news_ids).update(crucial=True)

    return selected_news_ids, fe_total_tokens

if __name__ == "__main__":
    selected_ids, total_tokens = update_crucial_articles()
    print(f"Selected news IDs: {selected_ids}, Total tokens used: {total_tokens}")
