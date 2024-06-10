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

SECRET_KEY = 'django-insecure-gddb)2@+aik@5uq#wh*=1dh-zs*s*x+@x3m4(#s3n0o#p4&+-d'
