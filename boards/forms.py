from django import forms
from boards.models import Card, Column, Members


class BoardForm(forms.Form):
    title = forms.CharField(max_length=36)
    background = forms.ImageField()


class MembersForm(forms.ModelForm):
    class Meta:
        model = Members
        fields = '__all__'


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'Leave a comment'
    }))


class CardForm(forms.ModelForm):

    class Meta:
        model = Card
        fields = '__all__'


class ColumnForm(forms.ModelForm):

    class Meta:
        model = Column
        fields = ['name']


class SearchUserForm(forms.Form):
    user = forms.CharField(label='Search by user', max_length=250)


class SearchMarkForm(forms.Form):
    mark = forms.CharField(label='Search by mark', max_length=250)
