#-*- coding:utf-8 -*-
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from django.http import Http404
from django.db.models import Q
from django.conf import settings
from currency.models import TypePair

@dajaxice_register
def calc(request, amount, rate, slug, ttype):
    dajax = Dajax()
    pair = TypePair.objects.get(slug=slug)
    total, commission = pair.calc(amount, rate, ttype)
    dajax.script("$('#{type}_total_result').text('{total} {right}');".format(**{"type":ttype, "total": total, "right":pair.right}))
    dajax.script("$('#{type}_commission_result').text('{commission} {pos}');".format(**{"type":ttype, "commission": commission, "pos":pair.left if ttype=='buy' else pair.right}))
    return dajax.json()
