from django.db import models
from django.contrib.auth.models import User

class LogFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='log_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

from django import forms
from .models import LogFile

class LogFileForm(forms.ModelForm):
    class Meta:
        model = LogFile
        fields = ['file']

class FilteringOptions(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add fields for filtering options (e.g., date, severity level, keywords)

