from django.db import models

class News(models.Model):
    news_id = models.AutoField(primary_key=True)  # AutoField로 수정
    title = models.CharField(max_length=45, blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    image = models.TextField(blank=True, null=True)
    link = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_dt = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    crucial = models.BooleanField(default=False)

    class Meta:
        managed = True  # Django가 이 모델을 관리하도록 변경
        db_table = 'News'

class SummarizeNews(models.Model):
    news = models.OneToOneField(News, models.DO_NOTHING, primary_key=True)
    first_sentence = models.TextField(blank=True, null=True)
    second_sentence = models.TextField(blank=True, null=True)
    third_sentence = models.TextField(blank=True, null=True)
    created_dt = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Summarize_news'

class User(models.Model):
    user_id = models.AutoField(primary_key=True) 
    user_name = models.CharField(max_length=45, null=True, blank=True) 
    email = models.CharField(max_length=45)

    class Meta:
        managed = False
        db_table = 'user'

class UserSend(models.Model):
    user = models.ForeignKey(User, models.DO_NOTHING)
    news = models.ForeignKey(News, models.DO_NOTHING)
    send = models.BooleanField(default=False)  # send 필드 추가

    class Meta:
        managed = False
        db_table = 'user_send'

class Gpt(models.Model):
    news = models.OneToOneField('News', on_delete=models.CASCADE, primary_key=True)
    fe_input_tokens = models.IntegerField(null=True)
    fe_output_tokens = models.IntegerField(null=True)
    fe_total_tokens = models.IntegerField(null=True)
    fe_cost = models.FloatField(null=True)
    su_input_tokens = models.IntegerField(null=True)
    su_output_tokens = models.IntegerField(null=True)
    su_total_tokens = models.IntegerField(null=True)
    su_cost = models.FloatField(null=True)
    created_dt = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'Gpt'