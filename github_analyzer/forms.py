from django import forms

class GitHubForm(forms.Form):
    username = forms.CharField(label='GitHub Username', max_length=100)
