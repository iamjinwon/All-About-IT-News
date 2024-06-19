import os
import sys
import django
from datetime import datetime, time
from django.conf import settings
from django.db.models import Sum, F
from premailer import transform
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz

current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newProject.settings")
django.setup()

from newApp.models import News, SummarizeNews, User


def create_html(recipient_email):
    try:
        seoul_tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(seoul_tz)
        today_start = datetime.combine(now.date(), time.min).astimezone(seoul_tz)
        today_end = datetime.combine(now.date(), time.max).astimezone(seoul_tz)
        date_formatted = now.strftime('%Y년 %-m월 %-d일')
        user = User.objects.get(email=recipient_email)

        original_articles = News.objects.filter(created_dt__range=(today_start, today_end), crucial=True)[:5]
        summarized_articles = SummarizeNews.objects.filter(news_id__in=[article.news_id for article in original_articles])

        if not original_articles.exists():
            print("오늘의 기사를 찾을 수 없습니다.")
            return ""
        if not summarized_articles.exists():
            print("오늘의 요약 기사를 찾을 수 없습니다.")
            return ""
        
        summarized_news = SummarizeNews.objects.filter(news__in=[article.news_id for article in original_articles])
        views_count = summarized_news.aggregate(total_views=Sum('views'))['total_views'] or 0
        summarized_news.update(views=F('views') + 1)

        views_count = int(views_count / len(original_articles))

        summarized_dict = {summary.news_id: summary for summary in summarized_articles}
        combined_articles = []
        for article in original_articles:
            summary = summarized_dict.get(article.news_id)
            if summary:
                combined_article = {
                    'title': article.title,
                    'date': article.date,
                    'image': article.image,
                    'link': article.link,
                    'description': article.description,
                    'summary': {
                        'first_sentence': summary.first_sentence,
                        'second_sentence': summary.second_sentence,
                        'third_sentence': summary.third_sentence,
                    },
                    'crawled_date': date_formatted,
                    'views_count': views_count,
                }
                combined_articles.append(combined_article)

        unsubscribe_url = f"http://127.0.0.1:8000/IT_news/unsubscribe/?token={user.unsubscribe_token}"

        combined_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Main Content</title>
            <style>
                body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                }}
                .main-content {{
                width: 70%;
                margin: auto;
                }}
                .section-heading {{
                margin-top: 30px;
                text-align: center;
                font-size: 24px;
                }}
                .post-image {{
                width: 728px;
                height: 409.250px;
                margin: 20px auto;
                display: block;
                }}
                .article-link {{
                margin-top: 10px;
                text-align: center;
                color: gray;
                }}
                .article-summary {{
                background-color: #ffffff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: left;
                width : 698px;
                margin: 20px auto; 
                }}
                .article-summary p {{
                margin: 0;
                padding: 0;
                color: #212529;
                }}
                .mb-4 {{
                margin-bottom: 32px; 
                }}
                .summary-box {{
                background-color: #e9ecef;
                border-radius: 10px;
                margin: 20px auto;
                padding: 15px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: left;
                font-family: 'Roboto', sans-serif;
                font-size: 15px;
                width: 728px;
                }}
            </style>
        </head>
        <body>
        <div class="main-content">
        """
        summary_box_html = f"""
        <div class="text-center" style="margin-top: 60px; text-align: center;">
            <p style="font-size: 30px; font-weight: bold; margin-bottom: 5px;">
                🔥 매일 아침 6시에 최신 
                <span style="color: red;">IT 뉴스</span> 5가지를 무료로 받아보세요 🔥
            </p>
            <p style="font-size: 14px; color: gray; margin-top: 5px; margin-bottom: 10px;">
                {date_formatted} | 조회 수 : <span id="views-count">{views_count}</span>
            </p>
        </div>
        <h3 style="text-align: center; margin-top: 60px;">오늘의 뉴스 한줄요약 </h3>
        <div class="summary-box">
        """
        for article in combined_articles:
            summary_box_html += f"""
            <div>✅ {article['title']}</div>
            """
        summary_box_html += "</div>"

        combined_html += summary_box_html

        for article in combined_articles:
            article_html = f"""
                <h2 class="section-heading">{article['title']}</h2>
                <img class="post-image" src="{article['image']}" alt="..."/>
                <div class="article-link"><p style="margin : 32px 0 32px 0;">출처: <b><a href="{article['link']}" style="text-decoration: none; color: gray;">테크레시피</a></b></p></div>
                <div class="article-summary">
                    <p>✅ {article['summary']['first_sentence']}</p>
                    <p style="margin-top: 20px;">✅ {article['summary']['second_sentence']}</p>
                    <p style="margin-top: 20px;">✅ {article['summary']['third_sentence']}</p>
                </div>
                <div class="mb-4"></div>
            """
            combined_html += article_html

        combined_html += f"""
        </div>
        <div style="text-align: center; margin-top: 70px; height: 50px;">
            <a href="{unsubscribe_url}" id="unsubscribe-button" style="text-decoration: none; color: white; background-color: red; padding: 10px 20px; border-radius: 5px;">뉴스레터 구독취소하기</a>
        </div>
        </body></html>
        """ 
        return transform(combined_html)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return ""

def create_html_for_gmail(recipient_email):
    try:
        seoul_tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(seoul_tz)
        today_start = datetime.combine(now.date(), time.min).astimezone(seoul_tz)
        today_end = datetime.combine(now.date(), time.max).astimezone(seoul_tz)
        date_formatted = now.strftime('%Y년 %-m월 %-d일')
        user = User.objects.get(email=recipient_email)

        original_articles = News.objects.filter(created_dt__range=(today_start, today_end), crucial=True)[:5]
        summarized_articles = SummarizeNews.objects.filter(news_id__in=[article.news_id for article in original_articles])

        if not original_articles.exists():
            print("오늘의 기사를 찾을 수 없습니다.")
            return ""
        if not summarized_articles.exists():
            print("오늘의 요약 기사를 찾을 수 없습니다.")
            return ""
        
        summarized_news = SummarizeNews.objects.filter(news__in=[article.news_id for article in original_articles])
        views_count = summarized_news.aggregate(total_views=Sum('views'))['total_views'] or 0
        summarized_news.update(views=F('views') + 1)

        views_count = int(views_count / len(original_articles))

        summarized_dict = {summary.news_id: summary for summary in summarized_articles}
        combined_articles = []
        for article in original_articles:
            summary = summarized_dict.get(article.news_id)
            if summary:
                combined_article = {
                    'title': article.title,
                    'date': article.date,
                    'image': article.image,
                    'link': article.link,
                    'description': article.description,
                    'summary': {
                        'first_sentence': summary.first_sentence,
                        'second_sentence': summary.second_sentence,
                        'third_sentence': summary.third_sentence,
                    },
                    'crawled_date': date_formatted,
                    'views_count': views_count,
                }
                combined_articles.append(combined_article)

        unsubscribe_url = f"http://127.0.0.1:8000/IT_news/unsubscribe/?token={user.unsubscribe_token}"

        combined_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Main Content</title>
            <style>
                body {{
                font-family: 'Roboto', sans-serif;
                margin: 0;
                padding: 0;
                }}
                .main-content {{
                width: 70%;
                margin: auto;
                }}
                .section-heading {{
                margin-top: 30px;
                text-align: center;
                font-size: 24px;
                }}
                .post-image {{
                width: 728px;
                height: 409.250px;
                margin: 20px auto;
                display: block;
                }}
                .article-link {{
                margin-top: 10px;
                text-align: center;
                color: gray;
                }}
                .article-summary {{
                background-color: #ffffff;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: left;
                width : 698px;
                margin: 20px auto;
                background-color: #e9ecef;
                }}
                .article-summary p {{
                margin: 0;
                padding: 0;
                color: #212529;
                }}
                .mb-4 {{
                margin-bottom: 32px; 
                }}
                .summary-box {{
                background-color: #e9ecef;
                border-radius: 10px;
                margin: 20px auto;
                padding: 15px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                text-align: left;
                font-family: 'Roboto', sans-serif;
                font-size: 15px;
                width: 728px;
                }}
            </style>
        </head>
        <body>
        <div class="main-content">
        """
        summary_box_html = f"""
        <div class="text-center" style="margin-top: 60px; text-align: center;">
            <p style="font-size: 30px; font-weight: bold; margin-bottom: 5px;">
                🔥 매일 아침 6시에 최신 
                <span style="color: red;">IT 뉴스</span> 5가지를 무료로 받아보세요 🔥
            </p>
            <p style="font-size: 14px; color: gray; margin-top: 5px; margin-bottom: 10px;">
                {date_formatted} | 조회 수 : <span id="views-count">{views_count}</span>
            </p>
        </div>
        <h3 style="text-align: center; margin-top: 60px;">오늘의 뉴스 한줄요약 </h3>
        <div class="summary-box">
        """
        for article in combined_articles:
            summary_box_html += f"""
            <div>✅ {article['title']}</div>
            """
        summary_box_html += "</div>"

        combined_html += summary_box_html

        for article in combined_articles:
            article_html = f"""
                <h2 class="section-heading">{article['title']}</h2>
                <img class="post-image" src="{article['image']}" alt="..."/>
                <div class="article-link"><p style="margin : 32px 0 32px 0;">출처: <b><a href="{article['link']}" style="text-decoration: none; color: gray;">테크레시피</a></b></p></div>
                <div class="article-summary">
                    <p>✅ {article['summary']['first_sentence']}</p>
                    <p style="margin-top: 20px;">✅ {article['summary']['second_sentence']}</p>
                    <p style="margin-top: 20px;">✅ {article['summary']['third_sentence']}</p>
                </div>
                <div class="mb-4"></div>
            """
            combined_html += article_html

        combined_html += f"""
        </div>
        <div style="text-align: center; margin-top: 70px; height: 50px;">
            <a href="{unsubscribe_url}" id="unsubscribe-button" style="text-decoration: none; color: white; background-color: red; padding: 10px 20px; border-radius: 5px;">뉴스레터 구독취소하기</a>
        </div>
        </body></html>
        """ 
        return transform(combined_html)

    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return ""

def send_email_with_attachment():
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    from_email = smtp_user
    subject = '오늘의 IT 뉴스입니다.'

    recipients = User.objects.values_list('email', flat=True)

    for recipient in recipients:
        if '@gmail.com' in recipient:
            html_content = create_html_for_gmail(recipient)
        else:
            html_content = create_html(recipient)

        if not html_content:
            print("No HTML content to send.")
            continue

        msg = MIMEMultipart('alternative')
        msg['From'] = from_email
        msg['To'] = recipient
        msg['Subject'] = subject

        part = MIMEText(html_content, 'html')
        msg.attach(part)

        try:
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.ehlo()
            smtp.starttls()
            smtp.login(smtp_user, smtp_password)
            smtp.sendmail(from_email, recipient, msg.as_string())
            smtp.quit()
            print(f"Email sent to {recipient}")
        except Exception as e:
            print(f"Failed to send email to {recipient}: {e}")



if __name__ == "__main__":
    send_email_with_attachment()
