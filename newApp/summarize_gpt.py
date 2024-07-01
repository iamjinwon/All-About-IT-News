from openai import OpenAI
from dotenv import load_dotenv
import os
import django
import sys
from datetime import datetime, time
import pytz
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

def summarize_gpt(system_prompt, news_content):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": news_content},
        ],
        temperature=0.2
    )

    result = response.choices[0].message.content
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

def summarize_articles():
    seoul_tz = pytz.timezone('Asia/Seoul')
    now = datetime.now(seoul_tz).replace(tzinfo=None)
    today_start = datetime.combine(now.date(), time.min).replace(tzinfo=None)
    today_end = datetime.combine(now.date(), time.max).replace(tzinfo=None)

    news_data = News.objects.filter(created_dt__range=(today_start, today_end), crucial=True)

    if not news_data.exists():
        print("No news articles found for today's date.")
        return

    for news in news_data:
        description = news.description
        news_id = news.news_id

        summarize, input_tokens, output_tokens, total_tokens = summarize_gpt(system_prompt2, description)
        cost = calculate_cost("gpt-4o", input_tokens, output_tokens)
        cost_won = cost * 1300

        if summarize:
            summary_lines = summarize.strip().split('\n')
            
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
