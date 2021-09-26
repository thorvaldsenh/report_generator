from django import forms
import datetime
from .models import ClientList


class DateInput(forms.DateInput):
    input_type = 'date'


class FormName(forms.Form):
    database_clients = ClientList.objects.all()
    CLIENTS = tuple((x.code, x.name) for x in database_clients)

    client = forms.ChoiceField(choices=CLIENTS)
    today = datetime.date.today()
    startDate = forms.DateField(initial=datetime.datetime(today.year, 1, 1), widget=DateInput)
    endDate = forms.DateField(initial=today, widget=DateInput)
