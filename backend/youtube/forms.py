from django import forms

class fileDownloader(forms.Form):
    FORMAT_CHOICES = [
        ('mp3', 'MP3 (Audio Only)'),
        ('mp4', 'MP4 (Video)'),
    ]
    
    QUALITY_CHOICES = [
        ('low', 'Low Quality'),
        ('medium', 'Medium Quality'),
        ('high', 'High Quality'),
    ]
    
    link = forms.CharField(
        max_length=200, 
        required=True, 
        label=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter YouTube URL here...',
            'class': 'url-input'
        })
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        initial='mp3',
        label='Format',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    quality = forms.ChoiceField(
        choices=QUALITY_CHOICES,
        initial='medium',
        label='Quality',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
