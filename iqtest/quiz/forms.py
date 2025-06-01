from django import forms
from django.contrib.auth.models import User
from .models import Review


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=255,
        label='',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'E-mail or username'})
        )
    password = forms.CharField(
        label='',
        widget=forms.PasswordInput(attrs={'class': 'input', 'placeholder': 'Password'})
        )

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Username', 'required': 'required'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'Email', 'required': 'required'}),
        }

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data).exists():
            raise forms.ValidationError('Email is already in use.')
        return data
    
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, i) for i in range(1, 6)]),  # Dropdown for 1-5
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about your experience!'})
        }