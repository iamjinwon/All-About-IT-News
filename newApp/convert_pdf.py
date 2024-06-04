import pdfkit
from django.conf import settings
from django.template.loader import render_to_string
import os
import json
from datetime import datetime
from bs4 import BeautifulSoup

def convert_to_pdf():
    try:
        today = datetime.now()
        date_formatted = today.strftime('%Y%m%d')

        directory_path = os.path.join(settings.BASE_DIR, 'newApp', 'media', 'news', 'tech_recipe')
        original_json_path = os.path.join(directory_path, f"{date_formatted}.json")
        summarized_json_path = os.path.join(directory_path, f"summarize_{date_formatted}.json")

        if not os.path.exists(original_json_path):
            print("Original JSON file not found.")
            return
        if not os.path.exists(summarized_json_path):
            print("Summarized JSON file not found.")
            return

        with open(original_json_path, 'r') as file:
            original_articles = json.load(file)
        
        with open(summarized_json_path, 'r') as file:
            summarized_articles = json.load(file)
        
        for i, article in enumerate(original_articles):
            article['summary'] = summarized_articles[i]
            article['crawled_date'] = date_formatted

        articles_html = []
        for article in original_articles:
            article_html_content = render_to_string('newApp/post.html', {"articles": [article]})
            soup = BeautifulSoup(article_html_content, 'html.parser')
            main_content = soup.find(class_='main-content')
            inline_styles = soup.find('style').get_text() if soup.find('style') else ''

            if main_content is None:
                print("No main-content found in HTML.")
                continue

            main_content_html = str(main_content)
            article_html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Main Content</title>
                <link rel="stylesheet" href="{settings.STATIC_URL}css/styles.css">
                <link rel="stylesheet" href="https://use.fontawesome.com/releases/v6.3.0/css/all.css">
                <style>
                    {inline_styles}
                    body {{
                        font-family: 'Roboto', sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        margin: 0;
                        padding: 0;
                    }}
                    .main-content {{
                        transform: scale(0.7);
                        transform-origin: center top;
                        width: 70%;
                        margin: auto;
                        padding-top: 50px;  /* 상단 여백 추가 */
                    }}
                    .section-heading {{
                        margin-top: 50px;
                        text-align: center;
                        display: block;
                    }}
                    .post-image {{
                        margin-top: 20px;
                        width: 100%;
                        border-radius: 15px;
                        display: block;
                        margin-left: auto;
                        margin-right: auto;
                    }}
                    .article-link {{
                        margin-top: 10px;
                        text-align: center;
                        font-size: 0.7em;
                        color: gray;
                    }}
                    .article-summary {{
                        margin-top: 20px;
                        padding: 20px;
                        background-color: #fff;
                        border-radius: 15px;
                        box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                        line-height: 1.6;
                    }}
                    .article-summary p {{
                        margin: 10px 0;
                    }}
                    .mb-4 {{
                        margin-bottom: 2rem;
                    }}
                </style>
            </head>
            <body>
                <div class="main-content">
                    {main_content_html}
                </div>
            </body>
            </html>
            """
            articles_html.append(article_html)
        
        combined_html = '<div style="page-break-after: always;"></div>'.join(articles_html)
        html_file_path = os.path.join(settings.BASE_DIR, 'newApp', 'static', 'temp_post.html')
        with open(html_file_path, 'w') as file:
            file.write(combined_html)
        
        if not os.path.exists(html_file_path):
            print("HTML file was not created.")
            return

        pdf_file_path = os.path.join(settings.BASE_DIR, 'newApp', 'static', 'output.pdf')

        try:
            # pdfkit 옵션 설정
            options = {
                'quiet': '',
                'enable-local-file-access': '',  # 로컬 파일 접근 활성화
                'no-stop-slow-scripts': '',  # 느린 스크립트 중단 방지
                'margin-top': '20mm',  # 상단 여백 추가
                'margin-bottom': '20mm',  # 하단 여백 추가
                'margin-left': '10mm',  # 좌측 여백 추가
                'margin-right': '10mm',  # 우측 여백 추가
            }

            pdfkit.from_file(html_file_path, pdf_file_path, options=options, configuration=settings.PDFKIT_CONFIG)
            if os.path.exists(pdf_file_path):
                print("PDF file was created successfully.")
            else:
                print("PDF file was not created.")
        except Exception as e:
            print(f"PDF conversion failed: {str(e)}")
        

    except Exception as e:
        print(f"An error occurred: {str(e)}")

# 테스트 코드 실행
if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 프로젝트 디렉토리를 sys.path에 추가
    project_dir = Path(__file__).resolve().parent.parent
    sys.path.append(str(project_dir))

    # Django settings 모듈을 설정합니다.
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "newProject.settings")
    import django
    django.setup()

    # 함수 호출 시 현재 날짜 사용
    convert_to_pdf()
