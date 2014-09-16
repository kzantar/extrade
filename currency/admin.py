#-*- coding:utf-8 -*-
from django.contrib import admin
from currency.models import Valuta, TypePair, PaymentMethod

# Register your models here.

class TypePairAdmin(admin.ModelAdmin):
    pass

class PaymentMethodInline(admin.StackedInline):
    model = PaymentMethod
    extra = 0
    fieldsets = (
        (None, {'fields': (
            (
                'disable',
                'enable_user_bank',
            ),
            (
                'action',
                'method'
            ),
            'commission',
                (
                    'min_commission',
                    'max_commission'
                ),
                (
                    'min_amount',
                    'max_amount'
                ),
                (
                    'bank', 'description_bank'
                ),
            )}),
    )

class ValutaAdmin(admin.ModelAdmin):
    inlines = (PaymentMethodInline, )

admin.site.register(Valuta, ValutaAdmin)
admin.site.register(TypePair, TypePairAdmin)
