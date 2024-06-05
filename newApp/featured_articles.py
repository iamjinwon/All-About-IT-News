from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime
from newApp.models import News

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

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
    total_tokens = response.usage.total_tokens
    return result, total_tokens

def update_crucial_articles():
    system_prompt = """
    Your task is to find interesting articles by looking at the title of the article and focusing on IT-related information, the latest technology, social issues, etc.

    [Rules]
    - Answers MUST always be in Korean.
    - You MUST pick 5 articles and answer them by article number.
    - The given texts are 3-line summaries of the articles.
    - The primary audience for this article is people in IT-related industries.
    - You MUST answer only with the article number.
    - Answers MUST not be duplicated.
    """.strip()

    today_start = datetime.combine(datetime.now().date(), datetime.min.time())
    today_end = datetime.combine(datetime.now().date(), datetime.max.time())

    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id','title')

    if not news_data:
        print("No news articles found for today's date.")
        return [], 0

    content = "\n".join([f"{news_id}: {title}" for news_id, title in news_data])

    selected_news_ids_str, total_tokens = make_output(system_prompt, content)

    try:
        # 문자열에서 news_id 추출
        selected_news_ids = [int(news_id.strip()) for news_id in selected_news_ids_str.split(',')]
    except ValueError as e:
        print(f"Error parsing selected news ids: {e}")
        # 응답이 예상한 형식이 아닌 경우 디버깅을 위한 출력을 추가
        print(f"Response content was not in the expected format: {selected_news_ids_str}")
        return [], total_tokens

    News.objects.filter(news_id__in=selected_news_ids).update(crucial=True)

    return selected_news_ids, total_tokens

if __name__ == "__main__":
    selected_ids, total_tokens = update_crucial_articles()
