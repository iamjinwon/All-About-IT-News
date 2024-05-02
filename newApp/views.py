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
            # 날짜 부분만 추출 ('tech_recipe:20240430.json' -> '20240430')
            date_part = item.split(':')[1].split('.')[0]
            # 날짜 형식 변환 ('20240430' -> '2024년 4월 30일 기사모음')
            formatted_date = datetime.strptime(date_part, '%Y%m%d').strftime('%Y년 %-m월 %-d일 기사모음')
            formatted_articles.append(formatted_date)

    return render(request, "newApp/index2.html", {"articles": formatted_articles})

def about(request):
    return render(request, "newApp/about.html")

def contact(request):
    return render(request, "newApp/contact.html")

def post(request):
    json_file_path = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe/tech_recipe:20240417.json"
    with open(json_file_path, 'r') as file:
        article = json.load(file)
    return render(request, "newApp/post.html", {"articles": article})
