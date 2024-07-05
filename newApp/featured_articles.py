from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime,time
import pytz
import json
import time as time_module
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


def fetch_crucial_news():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).replace(tzinfo=None)
    today_start = datetime.combine(now.date(), time.min).replace(tzinfo=None)
    today_end = datetime.combine(now.date(), time.max).replace(tzinfo=None)

    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id', 'title')
    if not news_data:
        print("No news articles found for today's date.")
        return [], 0
    
    jsonl_filename = os.path.join(current_path, 'batchinput.jsonl')

    with open(jsonl_filename, 'w', encoding='utf-8') as file:
        json_entry = {
            "custom_id": f"news-0",
            "method": "POST", 
            "url": "/v1/chat/completions",
            "body" :{
                "model": "gpt-4o",
                "messages": [
                    {"role": "system", "content": system_prompt1},
                    {"role": "user", "content": "\n".join([f"{news_id}: {title}" for news_id, title in news_data])}
                ],
                "temperature": 0.7
                }
            }
        file.write(json.dumps(json_entry, ensure_ascii=False) + '\n')

def make_output():
    fetch_crucial_news()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    batch_input_file = client.files.create(
        file=open("newApp/batchinput.jsonl", "rb"),
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
        time_module.sleep(180)
    
    result_file_id = batch_job.output_file_id
    result = client.files.content(result_file_id).content
    print(result)

    result_file_name = "./test_result.jsonl"

    with open(result_file_name, 'wb') as file:
        file.write(result)
    # Loading data from saved file
    results = []
    with open(result_file_name, 'r') as file:
        for line in file:
            # Parsing the JSON string into a dict and appending to the list of results
            json_object = json.loads(line.strip())
            results.append(json_object)

    # Reading only the first results
    res = results[0]
    res_body = res['response']['body']
    res_content = res_body['choices'][0]['message']['content']
    input_tokens = res_body['usage']['prompt_tokens']
    output_tokens = res_body['usage']['completion_tokens']
    total_tokens = res_body['usage']['total_tokens']
    
    return res_content, input_tokens, output_tokens, total_tokens

def calculate_cost(model, input_tokens, output_tokens):
    if model == "gpt-4o":
        input_cost_per_token = 5 / 1_000_000
        output_cost_per_token = 15 / 1_000_000
        cost = (input_cost_per_token * input_tokens) + (output_cost_per_token * output_tokens)
        return cost
    else:
        raise ValueError("Unsupported model")
    
def update_crucial_articles():

    selected_news_ids_str, fe_input_tokens, fe_output_tokens, fe_total_tokens = make_output()

    try:
        selected_news_ids = [int(news_id.strip()) for news_id in selected_news_ids_str.split(',')]
    except ValueError as e:
        print(f"Error parsing selected news ids: {e}")
        print(f"Response content was not in the expected format: {selected_news_ids_str}")
        return [], fe_total_tokens

    # 비용 계산
    fe_cost = (calculate_cost("gpt-4o", fe_input_tokens, fe_output_tokens)) / 2
    cost_won = (fe_cost * 1300) / 2

    Gpt.objects.create(
        task="기사분류",
        input_tokens=fe_input_tokens,
        output_tokens=fe_output_tokens,
        total_tokens=fe_total_tokens,
        cost_dollar=fe_cost,
        cost_won=cost_won,
    )

    News.objects.filter(news_id__in=selected_news_ids).update(crucial=True)

    return selected_news_ids, fe_total_tokens

if __name__ == "__main__":
    update_crucial_articles()