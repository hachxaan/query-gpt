from django import forms
from .models import Query, User


class QueryForm(forms.ModelForm):

    author = forms.ModelChoiceField(
        disabled=True,
        queryset=User.objects.all(),
        empty_label=None,
        required=False,
        widget=forms.Select(attrs={'readonly': 'readonly'})
    )
    
    sql_query = forms.CharField(
        widget=forms.Textarea(attrs={'id': 'sql-query'})
    )

    class Meta:
        model = Query
        fields = ['title', 'description', 'author', 'active', 'sql_query']
