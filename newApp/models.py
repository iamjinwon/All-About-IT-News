from django.db import models
import uuid

class News(models.Model):
    news_id = models.AutoField(primary_key=True)
    title = models.TextField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    info = models.CharField(max_length=45, blank=True, null=True)
    crucial = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'News'

class SummarizeNews(models.Model):
    news = models.OneToOneField(News, models.DO_NOTHING, primary_key=True)
    first_sentence = models.TextField(blank=True, null=True)
    second_sentence = models.TextField(blank=True, null=True)
    third_sentence = models.TextField(blank=True, null=True)
    created_dt = models.DateTimeField(blank=True, null=True)
    views = models.IntegerField(default=0)  # 조회수 필드 추가

    class Meta:
        managed = True
        db_table = 'Summarize_news'

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=45, null=True, blank=True)
    email = models.CharField(max_length=45)
    unsubscribe_token = models.UUIDField(default=uuid.uuid4, editable=False)

    class Meta:
        managed = True
        db_table = 'user'

class UserSend(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    news = models.ForeignKey(News, models.DO_NOTHING)
    send = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'user_send'

class Gpt(models.Model):
    task = models.CharField(max_length=45)  # 작업 유형을 나타내는 필드
    input_tokens = models.IntegerField()  # 입력 토큰 수
    output_tokens = models.IntegerField()  # 출력 토큰 수
    total_tokens = models.IntegerField()  # 총 토큰 수
    cost_dollar = models.FloatField()  # 비용(달러)
    cost_won = models.FloatField()  # 비용(원)
    created_dt = models.DateTimeField(auto_now_add=True)  # 생성 날짜와 시간

    class Meta:
        managed = True
        db_table = 'Gpt'
