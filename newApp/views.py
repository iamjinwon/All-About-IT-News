from django.shortcuts import render, redirect, HttpResponse
from django.conf import settings
from datetime import datetime
import json
import os
import re

def index(request):
    directory_path = os.path.join(settings.BASE_DIR, 'newApp', 'media', 'news', 'tech_recipe')
    items = os.listdir(directory_path)
    formatted_articles = []

    for item in items:
        if os.path.isfile(os.path.join(directory_path, item)) and re.match(r'^\d{8}\.json$', item):
            formatted_date = datetime.strptime(item.split('.')[0], '%Y%m%d')
            formatted_articles.append(formatted_date)

    formatted_articles.sort(reverse=True)

    articles_with_display = [(date.strftime('%Y%m%d'), date.strftime('%Y년 %-m월 %-d일')) for date in formatted_articles]

    return render(request, "newApp/index.html", {"articles": articles_with_display})

def about(request):
    return render(request, "newApp/about.html")

def contact(request):
    return render(request, "newApp/contact.html")

def post(request, date_str):
    try:
        # Format the date to YYYY년 MM월 DD일
        date = datetime.strptime(date_str, '%Y%m%d')
        display_date = date.strftime('%Y년 %-m월 %-d일')

        # Construct file paths
        directory_path = os.path.join(settings.BASE_DIR, 'newApp', 'media', 'news', 'tech_recipe')
        original_json_path = os.path.join(directory_path, f"{date_str}.json")
        summarized_json_path = os.path.join(directory_path, f"summarize_{date_str}.json")
        
        # Load original articles data
        with open(original_json_path, 'r') as file:
            original_articles = json.load(file)
        
        # Load summarized articles data
        with open(summarized_json_path, 'r') as file:
            summarized_articles = json.load(file)
        
        # Combine original and summarized data
        for i, article in enumerate(original_articles):
            article['summary'] = summarized_articles[i]
            article['crawled_date'] = display_date  # Use the display date format

        # Render the template with articles
        return render(request, "newApp/post.html", {"articles": original_articles})
    
    except ValueError:
        # Handle exceptions for date parsing
        return HttpResponse("Invalid date format. Please use the correct format: YYYY년 MM월 DD일", status=400)
    except FileNotFoundError:
        # Handle exceptions for missing files
        return HttpResponse("The requested page does not exist.", status=404)

def redirect_to_today_post(request):
    today_date_str = datetime.now().strftime('%Y%m%d')
    return redirect('post', date_str=today_date_str)
