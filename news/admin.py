#-*- coding:utf-8 -*-
from django.contrib import admin
from news.models import News

# Register your models here.

class NewsAdmin(admin.ModelAdmin):
    list_display=('__unicode__', 'title', 'smalltext')

admin.site.register(News, NewsAdmin)
