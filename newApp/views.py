from django.shortcuts import render, redirect, HttpResponse
from datetime import datetime
from newApp.models import News, SummarizeNews
from .forms import UserForm

def index(request):
    # 데이터베이스에서 뉴스 날짜 목록을 가져오기
    news_dates = News.objects.dates('created_dt', 'day', order='DESC')

    formatted_articles = []
    for date in news_dates:
        formatted_date = date.strftime('%Y%m%d')
        formatted_articles.append(formatted_date)

    articles_with_display = [(date, datetime.strptime(date, '%Y%m%d').strftime('%Y년 %-m월 %-d일')) for date in formatted_articles]

    return render(request, "newApp/index.html", {"articles": articles_with_display})

def about(request):
    return render(request, "newApp/about.html")

def contact(request):
    success = False
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            success = True  # 폼이 성공적으로 제출되었음을 표시
    else:
        form = UserForm()
    
    return render(request, 'newApp/contact.html', {'form': form, 'success': success})

def post(request, date_str):
    try:
        # Format the date to YYYY년 MM월 DD일
        date = datetime.strptime(date_str, '%Y%m%d')
        display_date = date.strftime('%Y년 %-m월 %-d일')

        # 데이터베이스에서 해당 날짜의 기사 가져오기
        original_articles = News.objects.filter(created_dt__date=date.date(), news_id__in=SummarizeNews.objects.values('news_id')).values()
        summarized_articles = SummarizeNews.objects.filter(news_id__in=[article['news_id'] for article in original_articles]).values()

        # 원본 기사와 요약 기사 결합
        summarized_dict = {summary['news_id']: summary for summary in summarized_articles}
        combined_articles = []
        for article in original_articles:
            summary = summarized_dict.get(article['news_id'], {})
            if summary:
                combined_article = {
                    'title': article['title'],
                    'date': article['date'],
                    'image': article['image'],
                    'link': article['link'],
                    'description': article['description'],
                    'summary': summary,
                    'crawled_date': display_date
                }
                combined_articles.append(combined_article)

        # Render the template with articles
        return render(request, "newApp/post.html", {"articles": combined_articles})
    
    except ValueError:
        # Handle exceptions for date parsing
        return HttpResponse("Invalid date format. Please use the correct format: YYYY년 MM월 DD일", status=400)
    except News.DoesNotExist:
        # Handle exceptions for missing files
        return HttpResponse("The requested page does not exist.", status=404)

def redirect_to_today_post(request):
    today_date_str = datetime.now().strftime('%Y%m%d')
    return redirect('post', date_str=today_date_str)
