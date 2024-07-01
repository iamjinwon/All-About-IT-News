from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db.models import Sum, F
from newApp.models import News, SummarizeNews
from .forms import UserForm
from .models import User, News
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

def index(request):
    news_dates = News.objects.dates('created_dt', 'day', order='DESC')

    formatted_articles = []
    for date in news_dates:
        formatted_date = date.strftime('%Y%m%d')
        articles = News.objects.filter(
            created_dt__date=datetime.strptime(formatted_date, '%Y%m%d').date(),
            crucial=True
        )
        if articles.exists():
            first_article = articles.first()
            formatted_articles.append({
                'date': formatted_date,
                'display_date': datetime.strptime(formatted_date, '%Y%m%d').strftime('%Y년 %m월 %d일'),
                'image': first_article.image,
                'title': first_article.title,
            })

    subscriber_count = User.objects.count()

    return render(request, "newApp/index.html", {"articles": formatted_articles, "subscriber_count": subscriber_count})


def post(request, date_str):
    try:
        date = datetime.strptime(date_str, '%Y%m%d')
        display_date = date.strftime('%Y년 %-m월 %-d일')

        original_articles = News.objects.filter(created_dt__date=date.date(), news_id__in=SummarizeNews.objects.values('news_id')).values()
        summarized_articles = SummarizeNews.objects.filter(news_id__in=[article['news_id'] for article in original_articles]).values()

        if not original_articles.exists():
            print("오늘의 기사를 찾을 수 없습니다.")
            return ""
        if not summarized_articles.exists():
            print("오늘의 요약 기사를 찾을 수 없습니다.")
            return ""

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
                    'info' : article['info'],
                    'summary': summary,
                    'crawled_date': display_date
                }
                combined_articles.append(combined_article)

        # 조회수 증가 및 조회수 가져오기
        summarized_news = SummarizeNews.objects.filter(news__in=[article['news_id'] for article in original_articles])
        views_count = summarized_news.aggregate(total_views=Sum('views'))['total_views'] or 0
        summarized_news.update(views=F('views') + 1)
        
        # 조회수를 정수형으로 변환
        views_count = int(views_count / len(combined_articles))

        subscriber_count = User.objects.count()

        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                try:
                    form.save()
                    return JsonResponse({"success": True})
                except ValidationError as e:
                    return JsonResponse({"success": False, "error_message": str(e)})
            else:
                error_messages = [str(error) for error_list in form.errors.values() for error in error_list]
                return JsonResponse({"success": False, "error_message": " ".join(error_messages)})
        else:
            form = UserForm()

        return render(request, "newApp/post.html", {
            "articles": combined_articles,
            "display_date": display_date,
            "subscriber_count": subscriber_count,
            "views_count": views_count,
            "form": form,
            "date_str": date_str,
        })

    except ValueError:
        return HttpResponse("Invalid date format. Please use the correct format: YYYY년 MM월 DD일", status=400)
    except News.DoesNotExist:
        return HttpResponse("The requested page does not exist.", status=404)

def redirect_to_today_post(request):
    today_date_str = datetime.now().strftime('%Y%m%d')
    yesterday_date_str = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
    
    today_exists = News.objects.filter(created_dt__date=datetime.now().date()).exists()

    if today_exists:
        return redirect('post', date_str=today_date_str)
    else:
        yesterday_exists = News.objects.filter(created_dt__date=datetime.now().date() - timedelta(days=1)).exists()
        if yesterday_exists:
            return redirect('post', date_str=yesterday_date_str)
        else:
            return HttpResponse("No articles available for today or yesterday.", status=404)

def unsubscribe(request):
    token = request.GET.get('token')
    user = get_object_or_404(User, unsubscribe_token=token) 
    return render(request, 'newApp/unsubscribe.html', {'user': user})

@csrf_exempt
def process_unsubscribe(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        user_name = data.get('name')
        try:
            user = User.objects.get(email=email, user_name=user_name)
            user.delete()
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'User not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})