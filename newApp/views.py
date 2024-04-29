from django.shortcuts import render, HttpResponse
import json

def index(request):
    filepath = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe/tech_recipe:20240417.json"
    with open(filepath, 'r') as file:
        data = json.load(file)
    return render(request, "newApp/main.html", {"articles": data})

def main(request):
    filepath = "/Users/jinwon/Desktop/git_Study/newApp/media/news/TechRecipe/tech_recipe:20240417.json"
    with open(filepath, 'r') as file:
        data = json.load(file)
    return render(request, "newApp/index.html", {"articles": data})


