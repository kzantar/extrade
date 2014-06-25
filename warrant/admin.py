#-*- coding:utf-8 -*-
from django.contrib import admin
from warrant.models import Buy, Sale, Orders
from django.db.models import Sum, Count, F, Q

# Register your models here.

class BuyAdmin(admin.ModelAdmin):
    list_display=('__unicode__', '_pir', 'sale', 'compl', 'total', 'commiss', 'adeudo', 'completed')
    list_editable = ('completed', 'sale')

class SaleAdmin(admin.ModelAdmin):
    list_display=('__unicode__', '_pir', 'buy', 'compl', 'total', 'commiss', 'adeudo', 'completed')
    list_editable = ('completed', 'buy')

admin.site.register(Sale, SaleAdmin)
admin.site.register(Buy, BuyAdmin)
