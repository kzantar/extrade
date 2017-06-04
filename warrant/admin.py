#-*- coding:utf-8 -*-
from django.contrib import admin
from warrant.models import Buy, Sale, Orders
from django.db.models import Sum, Count, F, Q

# Register your models here.

class BuyAdmin(admin.ModelAdmin):
    list_display=('__str__', '_pir', 'sale', 'compl', '_adeudo', 'commiss', 'adeudo', 'completed')
    list_editable = ('completed', )
    raw_id_fields = ('sale',)

class SaleAdmin(admin.ModelAdmin):
    list_display=('__str__', '_pir', 'buy', 'compl', '_total', 'commiss', 'adeudo', 'completed')
    list_editable = ('completed', )
    raw_id_fields = ('buy',)

admin.site.register(Sale, SaleAdmin)
admin.site.register(Buy, BuyAdmin)
