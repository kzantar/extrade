#-*- coding:utf-8 -*-
from django.contrib import admin
from currency.models import Valuta, TypePair

# Register your models here.

class TypePairAdmin(admin.ModelAdmin):
    pass

class ValutaAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('value', 'bank', )
            }
        ),
        (u'коммиссия', {
            'classes': ('collapse',),
            'fields': ('commission_inp', 'commission_out'),
            }),
        (u'Ограничения на вывод', {
            'classes': ('collapse',),
            'fields': ('out_min_amount', 'out_max_amount'),
            }),
        (u'Ограничения на ввод', {
            'classes': ('collapse',),
            'fields': ('inp_min_amount', 'inp_max_amount'),
            }),
    )
    

admin.site.register(Valuta, ValutaAdmin)
admin.site.register(TypePair, TypePairAdmin)
