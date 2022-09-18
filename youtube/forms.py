from django import forms



class fileDownloader(forms.Form):
    
    link = forms.CharField(max_length=200,required=True, label=False )
