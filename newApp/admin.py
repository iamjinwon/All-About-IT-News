from django.contrib import admin
from .models import News, SummarizeNews, User, UserSend

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'link')
    search_fields = ('title', 'link')

@admin.register(SummarizeNews)
class SummarizeNewsAdmin(admin.ModelAdmin):
    list_display = ('news', 'first_sentence', 'created_dt')
    search_fields = ('news__title',)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email',)
    search_fields = ('email',)

@admin.register(UserSend)
class UserSendAdmin(admin.ModelAdmin):
    list_display = ('user', 'news', 'send')
    search_fields = ('user__email', 'news__title')
