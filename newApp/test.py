from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz
import json
from system_prompt import system_prompt1


current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newProject.settings')
django.setup()

from newApp.models import News

dotenv_path = os.path.join(project_path, '.env')
load_dotenv(dotenv_path=dotenv_path)


def fetch_crucial_news():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz)
    today_start = datetime.combine(now.date(), time.min).astimezone(seoul_tz)
    today_end = datetime.combine(now.date(), time.max).astimezone(seoul_tz)

    news_data = News.objects.filter(created_dt__range=(today_start, today_end)).values_list('news_id', 'title')

    jsonl_filename = os.path.join(current_path, 'batchinput.jsonl')
    with open(jsonl_filename, 'w', encoding='utf-8') as file:
        json_entry = {
            "custom_id": f"news-0",
            "method": "POST", 
            "url": "/v1/chat/completions",
            "body" :{
                # "model": "gpt-4o",
                "model": "gpt-3.5-turbo",
                "messages": [
                    {"role": "system", "content": system_prompt1},
                    {"role": "user", "content": "\n".join([f"{news_id}: {title}" for news_id, title in news_data])}
                ],
                "max_tokens": 500
                }
            }
        file.write(json.dumps(json_entry, ensure_ascii=False) + '\n')

if __name__ == "__main__":
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
        print(batch_job)
        if batch_job.status == "completed":
            break
    
    result_file_id = batch_job.output_file_id
    result = client.files.content(result_file_id).content

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
    res = res['response']['body']['choices'][0]['message']['content'].split(',')
    print(res)