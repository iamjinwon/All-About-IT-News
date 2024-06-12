from django import forms
from django.core.exceptions import ValidationError
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_name', 'email']
        labels = {
            'user_name': '이름',
            'email': '이메일',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 구독된 이메일입니다.")
        return email
