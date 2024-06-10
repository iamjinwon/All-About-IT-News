import os
import sys
import django
from datetime import datetime, time
from django.conf import settings
from premailer import transform
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pytz

# 현재 경로와 프로젝트 경로 설정
current_path = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.join(current_path, '..')
sys.path.append(project_path)
os.chdir(project_path)

# Django settings 모듈을 설정합니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newProject.settings")
django.setup()

from newApp.models import News, SummarizeNews, User

def create_html():
    try:
        seoul_tz = pytz.timezone('Asia/Seoul')
        now = datetime.now(seoul_tz)
        today_start = datetime.combine(now.date(), time.min).astimezone(seoul_tz)
        today_end = datetime.combine(now.date(), time.max).astimezone(seoul_tz)
        date_formatted = now.strftime('%Y%m%d')

        # 데이터베이스에서 해당 날짜의 주요 기사 5개 가져오기
        original_articles = News.objects.filter(created_dt__range=(today_start, today_end), crucial=True)[:5]
        summarized_articles = SummarizeNews.objects.filter(news_id__in=[article.news_id for article in original_articles])

        if not original_articles.exists():
            print("오늘의 기사를 찾을 수 없습니다.")
            return ""
        if not summarized_articles.exists():
            print("오늘의 요약 기사를 찾을 수 없습니다.")
            return ""
        
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
                    'crawled_date': date_formatted
                }
                combined_articles.append(combined_article)

        # Combine all articles into one HTML string
        combined_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1" />
            <title>Main Content</title>
            <style>
                body {
                    font-family: 'Roboto', sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .main-content {
                    width: 70%;
                    margin: auto;
                    padding-top: 20px;
                }
                .section-heading {
                    margin-top: 30px;
                    text-align: center;
                    font-size: 24px;
                }
                .post-image {
                    margin-top: 20px;
                    width: 50%;
                    border-radius: 15px;
                    display: block;
                    margin-left: auto;
                    margin-right: auto;
                }
                .article-link {
                    margin-top: 10px;
                    text-align: center;
                    font-size: 0.7em;
                    color: gray;
                }
                .article-summary {
                    margin-top: 20px;
                    padding: 20px;
                    background-color: #fff;
                    border-radius: 15px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    line-height: 1.6;
                }
                .article-summary p {
                    margin: 10px 0;
                }
                .mb-4 {
                    margin-bottom: 32px; 
                }
            </style>
        </head>
        <body>
        """

        for article in combined_articles:
            article_html = f"""
            <div class="main-content">
                <h2 class="section-heading">{article['title']}</h2>
                <img class="post-image" src="{article['image']}" alt="..."/>
                <div class="article-link"><p>출처: <b><a href="{article['link']}" style="text-decoration: none; color: gray;">테크레시피</a></b></p></div>
                <div class="article-summary">
                    <p><i class="fas fa-check-circle"></i> {article['summary']['first_sentence']}</p>
                    <p><i class="fas fa-check-circle"></i> {article['summary']['second_sentence']}</p>
                    <p><i class="fas fa-check-circle"></i> {article['summary']['third_sentence']}</p>
                </div>
                <div class="mb-4"></div>
            </div>
            """
            combined_html += article_html

        combined_html += """
        </body>
        </html>
        """

        # 인라인 스타일 적용
        inlined_html = transform(combined_html)

        return inlined_html
        
    except Exception as e:
        print(f"오류가 발생했습니다: {str(e)}")
        return ""

def send_email_with_attachment():
    html_content = create_html()
    if not html_content:
        print("No HTML content to send.")
        return

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = settings.EMAIL_HOST_USER
    smtp_password = settings.EMAIL_HOST_PASSWORD

    from_email = smtp_user
    subject = '오늘의 IT 뉴스입니다.'

    recipients = User.objects.values_list('email', flat=True)

    for recipient in recipients:
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
