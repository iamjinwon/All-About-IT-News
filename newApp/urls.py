from django.urls import path
from newApp import views
from newApp.views import unsubscribe, process_unsubscribe

urlpatterns = [
    path('', views.redirect_to_today_post, name='redirect_to_today_post'), 
    path('posting/', views.index, name='index'),
    path('news/<str:date_str>/', views.post, name='post'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
    path('unsubscribe/process_unsubscribe/', process_unsubscribe, name='process_unsubscribe'),
]