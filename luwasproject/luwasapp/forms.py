from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, IncidentReport

class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['incident_type', 'severity', 'category', 'location', 'latitude', 'longitude', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make location, latitude, and longitude read-only
        self.fields['location'].widget.attrs['readonly'] = True
        self.fields['latitude'].widget.attrs['readonly'] = True
        self.fields['longitude'].widget.attrs['readonly'] = True
