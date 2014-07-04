#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from news.models import News

class NewsDetailView(DetailView):
    model = News
class NewsListView(ListView):
    model = News
