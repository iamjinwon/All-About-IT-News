[English](README.md) | 한국어
# All About IT news : 자동화 IT 뉴스 웹사이트

<div align="center">
  <br>
  <img src="https://i.ibb.co/BtYZ3yx/DALL-E-2024-06-27-22-48-57-Create-a-wide-logo-for-a-website-named-ALL-ABOUT-IT-NEWS-The-logo-should.webp" style="border-radius:15px;">
  <br>


![](https://img.shields.io/badge/language-Python-b44dff.svg)
![](https://img.shields.io/badge/Database-mySQL-4479A1.svg)

</div>

**All About IT news**는 매일 최신 IT 뉴스동향을 파악하기 위한 5개의 뉴스를 제공합니다. 간단한 구독과정을 통해, 매일 아침 6시에 이메일로 IT 정보를 받아보실 수도 있습니다❗️
**All About IT news**는 앞으로도 꾸준하게 업데이트 될 예정이니 많은 관심 부탁드립니다.😁

웹사이트 주소 : https://allabout-it.p-e.kr/itnews/posting/

- 📢 <b>주요 이슈들로 구성된 뉴스</b> : Chatgpt API를 이용한 프롬프트 엔지니어링을 통해 중요한 뉴스들을 효과적으로 선별했습니다.
- 📋 <b>요약된 형태의 뉴스</b> : Chatgpt API를 이용한 프롬프트 엔지니어링을 통해 중요한 뉴스들을 효과적으로 3줄로 했습니다.
- 🤖 <b>자동화 프로세스</b> : 매일 오전 5시에 뉴스가 업데이트되고, 주중에는 오전 6시마다 구독자들에게 이메일을 전송해드립니다!
- 💻 <b>웹사이트 배포</b> : AWS ec2를 이용하여 웹사이트를 배포하였고, 웹사이트는 자유롭게 이용이 가능합니다.
----

목차
=================
- [All About IT news : 자동화 IT 뉴스 웹사이트](#all-about-it-news)
- [목차](#목차)
  - [설치방법](#설치방법)
  - [초기화과정](#초기화과정)


### 개발환경
- Python 3.10 이상
- MySQL 서버
- pip (Python 패키지 관리자)

### 설치방법

1. Github에서 소스 코드 가져오기
```bash
git clone https://github.com/iamjinwon/2024_All_About_IT_News.git
cd 2024_All_About_IT_News
```

2. 패키지 설치 및 초기화 진행
```bash
pip install .
initialize_2024_all_about_it_news
```

3. 서버실행
```bash
python manage.py runserver
```

### 설정 파일 구성
**initialize_2024_all_about_it_news** 명령어는 다음과 같은 작업들을 수행합니다 :
- MySQL 서버 및 클라이언트 설치
- 필요한 시스템 패키지 설치
- '.env'파일 생성
- Django 마이그레이션 수행

#### Mysql 설치 및 설정
- MySQL 서버와 클라이언트를 설치합니다. 설치 후, 초기 보안 설정을 진행합니다.
```bash
sudo apt-get install -y mysql-server
sudo mysql_secure_installation
sudo apt-get install -y pkg-config libmysqlclient-dev
sudo apt-get install -y build-essential
sudo apt-get install -y python3-dev
```
- **참고** : MySQL 설치 과정 중 암호 설정 및 보안 관련 질문이 나올 수 있습니다. 이를 사용자 본인에 알맞게 적절히 설정해 주세요.

#### '.env' 파일 생성
- 사용자의 데이터베이스 정보와 OpenAI의 API 키를 입력받아 '.env' 파일을 생성합니다.
```bash
Enter your database name: 
Enter your database user: 
Enter your database password: 
Enter your database host (default: localhost): 
Enter your database port (default: 3306): 
Enter your OpenAI API key: 
```

#### Django 마이그레이션
- Django 마이그레이션을 수행하여 데이터베이스를 설정합니다.
```bash
python manage.py makemigrations
python manage.py migrate
```

----

## 사용된 라이브러리
- beautifulsoup4 : 크롤링과정에서 사용.
- openai : chatGpt API 이용.
- [premailer](https://github.com/peterbe/premailer) : 이메일의 style을 inline-style로 바꾸는데 사용.


## 기술 스택

| Python | Django | HTML | MySQL | gunicorn | nginx | 
| :--------: | :--------: | :------: | :------: | :------: | :------: |
| <img src="images/python.png" width="100" height="100"> | <img src="images/django.png" width="100" height="100"> | <img src="images/html.png" width="100" height="100"> | <img src="images/mysql.png" width="100" height="100"> | <img src="images/gunicorn.png" width="100" height="100"> | <img src="images/nginx.png" width="100" height="100"> |