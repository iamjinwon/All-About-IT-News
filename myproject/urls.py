"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf -> 현재 urls.py가 아니라 다른 urls.py로 위임을 하려면 어떻게 해야 하는가?
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

# http://127.0.0.1/
# http://127.0.0.1/app/

# http://127.0.0.1/create/
# http://127.0.0.1/read/1/

# 기본적으로 라우팅과 관련된 정보가 적혀있어야 함
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('myapp.urls')) # 사용자가 접속을 했을 때 admin이 아닌 다른 경로로 접속을 하면 myapp의 urls로 위임을 하는 것
]
