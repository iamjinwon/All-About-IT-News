from django.shortcuts import render, HttpResponse
from datetime import datetime
import json
import os

def index(request):
    directory_path = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe"
    items = os.listdir(directory_path)
    formatted_articles = []

    for item in items:
        if os.path.isfile(os.path.join(directory_path, item)) and item.endswith('.json'):
            date_part = item.split(':')[1].split('.')[0]
            formatted_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y년 %-m월 %-d일 기사모음')
            formatted_articles.append(formatted_date)

    return render(request, "newApp/index2.html", {"articles": formatted_articles})

def about(request):
    return render(request, "newApp/about.html")

def contact(request):
    return render(request, "newApp/contact.html")

def post(request):
    # 원본 기사 파일 경로
    original_json_path = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe/tech_recipe:20240417.json"
    # 요약 기사 파일 경로
    summarized_json_path = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe/summarize_tech_recipe:20240417.json"
    
    # 원본 기사 데이터 로드
    with open(original_json_path, 'r') as file:
        original_articles = json.load(file)
    
    # 요약 기사 데이터 로드
    with open(summarized_json_path, 'r') as file:
        summarized_articles = json.load(file)
    
    # 원본과 요약 데이터 결합
    for i, article in enumerate(original_articles):
        # Access the summary directly from the dictionary without string operations
        article['summary'] = summarized_articles[i]  # Updated to directly use the summary dict

    # 템플릿 렌더링
    return render(request, "newApp/post.html", {"articles": original_articles})

