from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz
from system_prompt import system_prompt1

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News, Gpt

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
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens
    return result, input_tokens, output_tokens, total_tokens

def calculate_cost(model, input_tokens, output_tokens):
    if model == "gpt-4o":
        input_cost_per_token = 5 / 1_000_000
        output_cost_per_token = 15 / 1_000_000
        cost = (input_cost_per_token * input_tokens) + (output_cost_per_token * output_tokens)
        return cost
    else:
        raise ValueError("Unsupported model")

def update_crucial_articles():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).replace(tzinfo=None) 
    today_start = datetime.combine(now.date(), time.min).replace(tzinfo=None)
    today_end = datetime.combine(now.date(), time.max).replace(tzinfo=None) 

    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id', 'title')

    if not news_data:
        print("No news articles found for today's date.")
        return [], 0

    content = "\n".join([f"{news_id}: {title}" for news_id, title in news_data])

    selected_news_ids_str, fe_input_tokens, fe_output_tokens, fe_total_tokens = make_output(system_prompt1, content)

    try:
        selected_news_ids = [int(news_id.strip()) for news_id in selected_news_ids_str.split(',')]
    except ValueError as e:
        print(f"Error parsing selected news ids: {e}")
        print(f"Response content was not in the expected format: {selected_news_ids_str}")
        return [], fe_total_tokens

    # 비용 계산
    fe_cost = calculate_cost("gpt-4o", fe_input_tokens, fe_output_tokens)
    cost_won = fe_cost * 1300

    # GPT 테이블에 데이터 삽입
    Gpt.objects.create(
        task="기사분류",
        input_tokens=fe_input_tokens,
        output_tokens=fe_output_tokens,
        total_tokens=fe_total_tokens,
        cost_dollar=fe_cost,
        cost_won=cost_won,
    )

    # News 테이블의 crucial 컬럼 업데이트
    News.objects.filter(news_id__in=selected_news_ids).update(crucial=True)

    return selected_news_ids, fe_total_tokens

if __name__ == "__main__":
    selected_ids, total_tokens = update_crucial_articles()
    print(f"Selected news IDs: {selected_ids}, Total tokens used: {total_tokens}")
