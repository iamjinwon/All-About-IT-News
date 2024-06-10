DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'IT_news',
        'USER' : 'teamlab',
        'PASSWORD' : '',
        'HOST' : '127.0.0.1',
        'PORT' : '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'", 
            'charset': 'utf8mb4',
            'use_unicode': True,
        },
    }
}

SECRET_KEY = ''
