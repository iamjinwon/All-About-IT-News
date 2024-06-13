from django.shortcuts import render, redirect, HttpResponse
from django.core.exceptions import ValidationError
from datetime import datetime
from newApp.models import News, SummarizeNews
from .forms import UserForm
from .models import User

def index(request):
    # 데이터베이스에서 뉴스 날짜 목록을 가져오기
    news_dates = News.objects.dates('created_dt', 'day', order='DESC')

    formatted_articles = []
    for date in news_dates:
        formatted_date = date.strftime('%Y%m%d')
        formatted_articles.append(formatted_date)

    articles_with_display = [(date, datetime.strptime(date, '%Y%m%d').strftime('%Y년 %-m월 %-d일')) for date in formatted_articles]

    subscriber_count = User.objects.count()  # 구독자 수 계산

    return render(request, "newApp/index.html", {"articles": articles_with_display, "subscriber_count": subscriber_count})

def contact(request):
    success = False
    error_message = None
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                success = True
                form = UserForm()  # 폼을 새 인스턴스로 초기화하여 입력 칸 비우기
            except ValidationError as e:
                error_message = e.message
        else:
            error_message = form.errors.as_text()
    else:
        form = UserForm()
    
    subscriber_count = User.objects.count()  # 구독자 수 계산

    return render(request, 'newApp/contact.html', {
        'form': form,
        'success': success,
        'error_message': error_message,
        'subscriber_count': subscriber_count,  # 구독자 수 템플릿에 전달
    })

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

        subscriber_count = User.objects.count()  # 구독자 수 계산

        # Render the template with articles and display_date
        return render(request, "newApp/post.html", {"articles": combined_articles, "display_date": display_date, "subscriber_count": subscriber_count})
    
    except ValueError:
        # Handle exceptions for date parsing
        return HttpResponse("Invalid date format. Please use the correct format: YYYY년 MM월 DD일", status=400)
    except News.DoesNotExist:
        # Handle exceptions for missing files
        return HttpResponse("The requested page does not exist.", status=404)

def redirect_to_today_post(request):
    today_date_str = datetime.now().strftime('%Y%m%d')
    return redirect('post', date_str=today_date_str)
