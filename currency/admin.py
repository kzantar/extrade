#-*- coding:utf-8 -*-
from django.contrib import admin
from currency.models import Valuta, TypePair

# Register your models here.

class TypePairAdmin(admin.ModelAdmin):
    pass

class ValutaAdmin(admin.ModelAdmin):
    pass

admin.site.register(Valuta, ValutaAdmin)
admin.site.register(TypePair, TypePairAdmin)
