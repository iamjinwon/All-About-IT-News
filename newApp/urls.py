from django.contrib import admin
from django.urls import path, include
from newApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.redirect_to_today_post, name='redirect_to_today_post'), 
    path('contact/', views.contact, name='contact'),
    path('index/', views.index, name='index'),
    path('post/<str:date_str>/', views.post, name='post'),
]
