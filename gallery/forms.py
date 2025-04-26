from django import forms
from .models import Comment, Rating, ContentSuggestion
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError



class CustomUserCreationForm(forms.ModelForm):
   password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
   password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

   class Meta:
      model = User
      fields = ['username', 'email', 'password1', 'password2']

   def clean_email(self):
      """Проверяем, что email введён корректно и не используется"""
      email = self.cleaned_data.get('email')

      if not email:
         raise ValidationError("Email обязателен.")

      try:
         validate_email(email)
      except ValidationError:
         raise ValidationError("Введите корректный email.")

      if User.objects.filter(email=email).exists():
         raise ValidationError("Этот email уже зарегистрирован.")

      return email

   def clean(self):
      """Проверяем, что пароли совпадают"""
      cleaned_data = super().clean()
      password1 = cleaned_data.get("password1")
      password2 = cleaned_data.get("password2")
      if password1 and password2 and password1 != password2:
         raise ValidationError("Пароли не совпадают.")
      return cleaned_data


class ContentSuggestionForm(forms.ModelForm):
   class Meta:
      model = ContentSuggestion
      fields = ['suggestion_type', 'model_name', 'model_bio', 'model_avatar', 'pack_title', 'pack_description', 'pack_photos']
      widgets = {
         'model_bio': forms.Textarea(attrs={'rows': 4}),
         'pack_description': forms.Textarea(attrs={'rows': 4}),
      }


class CommentForm(forms.ModelForm):
   class Meta:
      model = Comment
      fields = ['text']
      widgets = {
         'text': forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Напишите ваш комментарий...',
            'rows': 4
         }),
      }
      

class RatingForm(forms.ModelForm):
   class Meta:
      model = Rating
      fields = ['score']
      widgets = {
         'score': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
      }