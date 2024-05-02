from django.urls import path
from newApp import views

urlpatterns = [
    path('index.html', views.index),
    path('about.html', views.about),
    path('contact.html', views.contact),
    path('post.html', views.post),
    # path('history', views.index),
]
