#-*- coding:utf-8 -*-
from django import forms
from warrant.models import Orders

class OrderForm(forms.Form):
    class Meta:
        model = Orders
        fields = ('amount', 'rate', )
