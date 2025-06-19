from django import forms
from .models import *


class LocationSearchForm(forms.Form):
    region = forms.ModelChoiceField(
        queryset=Regions.objects.all(),
        label='Регион',
        required=True
    )
    people = forms.IntegerField(
        label='Количество человек',
        min_value=1,
        required=True
    )
    date = forms.DateField(
        label='Дата мероприятия',
        input_formats=['%Y-%m-%d'],
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )
