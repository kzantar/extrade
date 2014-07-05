#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.views.generic import DetailView, RedirectView

from warrant.models import Buy, Sale

# Create your views here.
class BuyDetailView(DetailView, FormMixin):
    def post(self, request):
        pass

class SaleDetailView(DetailView, FormMixin):
    def post(self, request):
        pass
