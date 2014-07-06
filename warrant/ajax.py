#-*- coding:utf-8 -*-
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
from django.http import Http404
from django.db.models import Q
from django.conf import settings
from currency.models import TypePair
from warrant.forms import OrdersForm

@dajaxice_register
def calc(request, form):
    dajax = Dajax()
    q=deserialize_form(form)
    ttype = ''
    if not q.get('buy-amount', None) is None: ttype='buy'
    if not q.get('sale-amount', None) is None: ttype='sale'
    form = OrdersForm(prefix=ttype, data=q)
    if form.is_valid():
        c=form.cleaned_data
        pair = c.get('pair')
        total, commission, pos = pair.calc(c.get('amount'), c.get('rate'), ttype)
        dajax.script("$('#{type}_total_result').text('{total} {right}');".format(**{"type":ttype, "total": total, "right":pair.right}))
        dajax.script("$('#{type}_commission_result').text('{commission} {pos}');".format(**{"type":ttype, "commission": commission, "pos":pos }))
        dajax.remove_css_class('#{type}_form input'.format(**{"type":ttype}), 'error')
    else:
        dajax.script("$('#info_{type}').text('{text}');".format(**{"type":ttype, "text":"Неправильно заполнено одно из полей.", }))
        for error in form.errors:
            dajax.add_css_class('#id_%s-%s' % (ttype, error), 'error')
    """
    pair = TypePair.objects.get(slug=slug)
    total, commission = pair.calc(amount, rate, ttype)
    dajax.script("$('#{type}_total_result').text('{total} {right}');".format(**{"type":ttype, "total": total, "right":pair.right}))
    dajax.script("$('#{type}_commission_result').text('{commission} {pos}');".format(**{"type":ttype, "commission": commission, "pos":pair.left if ttype=='buy' else pair.right}))
    if not request.user.is_authenticated:
        dajax.script("$('#info_{type}').text('');".format(**{}))
    """
    return dajax.json()
