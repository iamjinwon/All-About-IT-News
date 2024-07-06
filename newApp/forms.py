from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from .models import User

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['user_name', 'email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['user_name'].widget.attrs['placeholder'] = '이름'
        self.fields['user_name'].label = ''
        self.fields['email'].widget.attrs['placeholder'] = '이메일'
        self.fields['email'].label = ''
        self.fields['email'].required = False

    def clean_user_name(self):
        user_name = self.cleaned_data.get('user_name')
        if not user_name:
            raise ValidationError("이름을 입력해주세요.")
        return user_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("이메일을 입력해주세요.")
        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("유효하지 않은 이메일 형식입니다.")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("이미 구독된 이메일입니다.")

        return email
