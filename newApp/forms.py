from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_name', 'email']
        labels = {
            'user_name': '이름',
            'email': '이메일',
        }

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if not user_name:
            raise ValidationError("이름을 입력해주세요.")
        return user_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("유효하지 않은 이메일 형식입니다.")

        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 구독된 이메일입니다.")

        return email
