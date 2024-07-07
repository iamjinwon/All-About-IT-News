English | [한국어](README_kor.md)
# All About IT news : Automated IT News Website

<div align="center">
  <br>
  <img src="https://i.ibb.co/BtYZ3yx/DALL-E-2024-06-27-22-48-57-Create-a-wide-logo-for-a-website-named-ALL-ABOUT-IT-NEWS-The-logo-should.webp" style="border-radius:15px;">
  <br>


![](https://img.shields.io/badge/language-Python-b44dff.svg)
![](https://img.shields.io/badge/Database-mySQL-4479A1.svg)

</div>

**All About IT news** provides 5 pieces of news every day to keep you updated with the latest IT trends. Through a simple subscription process, you can receive IT information via email every morning at 6 AM❗️
**All About IT news** will continue to be updated, so please stay tuned.😁

**Website URL** : https://allabout-it.p-e.kr/itnews/posting/

- 📢 <b>News composed of major issues</b>: Important news is effectively selected through prompt engineering using the ChatGPT API.
- 📋 <b>Summarized news</b>: Important news is effectively summarized in three lines using prompt engineering with the ChatGPT API.
- 🤖 <b>Automated process</b>: News is updated daily at 5 AM, and subscribers receive emails every weekday at 6 AM!
- 💻 <b>Website deployment</b>: The website is deployed using AWS EC2 and is freely available for use.
----

Table of Contents
=================
- [All About IT news : Automated IT News Website](#all-about-it-news)
- [Table of Contents](#Table-of-Contents)
  - [Installation Instructions](#Installation-Instructions)
  - [Initialization Process](#Initialization-Process)


### Development Environment
- Python 3.10 or higher
- MySQL Server
- pip (Python package manager)

### Installation Instructions

1. Clone the source code from Github
```bash
git clone https://github.com/iamjinwon/2024_All_About_IT_News.git
cd 2024_All_About_IT_News
```

2. Install packages and initialize
```bash
pip install .
initialize_2024_all_about_it_news
```

3. Run the server
```bash
python manage.py runserver
```

### Configuration File Setup
**initialize_2024_all_about_it_news** command performs the following tasks :
- Install MySQL server and client
- Install necessary system packages
- Create the '.env' file
- Perform Django migrations

#### MySQL Installation and Setup
- Install MySQL server and client. After installation, proceed with the initial security setup.
```bash
sudo apt-get install -y mysql-server
sudo mysql_secure_installation
sudo apt-get install -y pkg-config libmysqlclient-dev
sudo apt-get install -y build-essential
sudo apt-get install -y python3-dev
```
- **Note** :During the MySQL installation process, you may be prompted to set passwords and configure security settings. Please configure these settings appropriately.

#### Creating the '.env' File
- Enter your database information and OpenAI API key to create the '.env' file.
```bash
Enter your database name: 
Enter your database user: 
Enter your database password: 
Enter your database host (default: localhost): 
Enter your database port (default: 3306): 
Enter your OpenAI API key: 
```

#### Django Migrations
- Perform Django migrations to set up the database.
```bash
python manage.py makemigrations
python manage.py migrate
```

----

## Libraries Used
- beautifulsoup4: Utilized for web scraping processes.
- openai: Employed for leveraging the ChatGPT API.
- [premailer](https://github.com/peterbe/premailer) : Used for converting email styles to inline styles.


## Technology Stack
| Python | Django | HTML | MySQL | gunicorn | nginx | 
| :--------: | :--------: | :------: | :------: | :------: | :------: |
| <img src="images/python.png" width="100" height="100"> | <img src="images/django.png" width="100" height="100"> | <img src="images/html.png" width="100" height="100"> | <img src="images/mysql.png" width="100" height="100"> | <img src="images/gunicorn.png" width="100" height="100"> | <img src="images/nginx.png" width="100" height="100"> |