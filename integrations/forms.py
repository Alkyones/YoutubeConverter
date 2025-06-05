from django import forms
from .models import TelegramIntegration

class TelegramIntegrationForm(forms.ModelForm):
    class Meta:
        model = TelegramIntegration
        fields = ['name', 'description', 'telegram_bot_token', 'telegram_chat_id']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a name for this integration.'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Optional: Describe what this integration is for.'
            }),
            'telegram_bot_token': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Paste your Telegram bot token here.'
            }),
            'telegram_chat_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the chat ID where notifications will be sent.'
            }),
        }