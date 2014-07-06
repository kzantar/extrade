#-*- coding:utf-8 -*-
from django import forms
from warrant.models import Orders
from django.forms.widgets import HiddenInput, NumberInput

class OrdersForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ('amount', 'rate', 'pair')
        widgets = {
                "amount":NumberInput(attrs={"class":"buyBtcInp"}),
                "rate":NumberInput(attrs={"class":"buyBtcInp"}),
                "pair":HiddenInput(),
            }
