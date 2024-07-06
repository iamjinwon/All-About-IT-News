from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz
import json
import time as time_module
from system_prompt import system_prompt2

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News, SummarizeNews, Gpt

dotenv_path = os.path.join(project_path, '.env')
load_dotenv(dotenv_path=dotenv_path)

def fetch_crucial_news():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).replace(tzinfo=None)
    today_start = datetime.combine(now.date(), time.min).replace(tzinfo=None)
    today_end = datetime.combine(now.date(), time.max).replace(tzinfo=None)

    news_data = News.objects.filter(created_dt__range=(today_start, today_end), crucial=True)

    if not news_data.exists():
        print("No news articles found for today's date.")
        return None, 0

    jsonl_filename = os.path.join(current_path, 'batchinput.jsonl')
    
    with open(jsonl_filename, 'w', encoding='utf-8') as file:
        for i, news in enumerate(news_data):
            description = news.description
            json_entry = {
                "custom_id": f"news-{i}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o",
                    "messages": [
                        {"role": "system", "content": system_prompt2},
                        {"role": "user", "content": f"{description}"}
                    ],
                    "temperature": 0.7
                }
            }
            file.write(json.dumps(json_entry, ensure_ascii=False) + "\n")

    return news_data, len(news_data)

def make_output():
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    batch_input_file_path = os.path.join(current_path, 'batchinput.jsonl')
    batch_input_file = client.files.create(
        file=open(batch_input_file_path, "rb"),
        purpose="batch"
    )
    batch_input_file_id = batch_input_file.id

    batch_job = client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h"
    )

    while True:
        batch_job = client.batches.retrieve(batch_job.id)
        if batch_job.status == "completed":
            break
        time_module.sleep(600)  # 10분 대기

    result_file_id = batch_job.output_file_id
    result = client.files.content(result_file_id).content
    print(result)

    result_file_name = os.path.join(current_path, 'test_result.jsonl')

    with open(result_file_name, 'wb') as file:
        file.write(result)

    # 저장된 파일에서 데이터 로드
    results = []
    with open(result_file_name, 'r') as file:
        for line in file:
            json_object = json.loads(line.strip())
            results.append(json_object)

    return results

def calculate_cost(model, input_tokens, output_tokens):
    if model == "gpt-4o":
        input_cost_per_token = 5 / 1_000_000
        output_cost_per_token = 15 / 1_000_000
        cost = (input_cost_per_token * input_tokens) + (output_cost_per_token * output_tokens)
        return cost
    else:
        raise ValueError("Unsupported model")

def summarize_articles():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).replace(tzinfo=None)
    today_start = datetime.combine(now.date(), time.min).replace(tzinfo=None)
    today_end = datetime.combine(now.date(), time.max).replace(tzinfo=None)

    news_data, news_count = fetch_crucial_news()

    if not news_data:
        print("No news articles found for today's date.")
        return

    results = make_output()

    for i, news in enumerate(news_data):
        description = news.description
        news_id = news.news_id
        res = results[i]
        res_body = res['response']['body']
        res_content = res_body['choices'][0]['message']['content']
        input_tokens = res_body['usage']['prompt_tokens']
        output_tokens = res_body['usage']['completion_tokens']
        total_tokens = res_body['usage']['total_tokens']

        cost = calculate_cost("gpt-4o", input_tokens, output_tokens) / 2
        cost_won = (cost * 1300)

        if res_content:
            summary_lines = res_content.strip().split('\n')
            if len(summary_lines) >= 3:
                summary_dict = {
                    "news_id": news_id,
                    "first_sentence": summary_lines[0].strip().lstrip('(1) '),
                    "second_sentence": summary_lines[1].strip().lstrip('(2) '),
                    "third_sentence": summary_lines[2].strip().lstrip('(3) '),
                    "created_dt": now
                }

                _, created = SummarizeNews.objects.update_or_create(
                    news_id=news_id,
                    defaults=summary_dict
                )
                if created:
                    print(f"Created new summary for news_id {news_id}")
                else:
                    print(f"Updated existing summary for news_id {news_id}")

                Gpt.objects.create(
                    task="기사요약",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    cost_dollar=cost,
                    cost_won=cost_won,
                )
            else:
                print(f"Summarization did not return enough sentences for news_id {news_id}")

if __name__ == "__main__":
    summarize_articles()
