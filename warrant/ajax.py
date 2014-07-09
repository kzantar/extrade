#-*- coding:utf-8 -*-
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
from django.http import Http404
from django.db.models import Q
from django.conf import settings
from currency.models import TypePair
from warrant.forms import OrdersForm
from warrant.models import Orders
from django.template.defaultfilters import floatformat


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
        pair, amount, rate = c.get('pair'), c.get('amount'), c.get('rate')
        total, commission, pos = pair.calc(amount, rate, ttype, totext=True)
        dajax.script("$('#{type}_total_result').text('{total} {right}');".format(**{"type":ttype, "total": total, "right":pair.right}))
        dajax.script("$('#{type}_commission_result').text('{commission} {pos}');".format(**{"type":ttype, "commission": commission, "pos":pos }))
        dajax.remove_css_class('#{type}_form input'.format(**{"type":ttype}), 'error')
    else:
        dajax.script("$('#info_{type}').text('{text}');".format(**{"type":ttype, "text":"Неправильно заполнено одно из полей.", }))
        for error in form.errors:
            dajax.add_css_class('#id_%s-%s' % (ttype, error), 'error')
    return dajax.json()

@dajaxice_register
def order(request, form):
    dajax = Dajax()
    q=deserialize_form(form)
    ttype = ''
    if not q.get('buy-amount', None) is None: ttype = 'buy'
    if not q.get('sale-amount', None) is None: ttype = 'sale'
    form = OrdersForm(prefix=ttype, data=q)
    if form.is_valid():
        c=form.cleaned_data
        user=request.user
        if user.is_authenticated() and user.is_active:
            pair, amount, rate = c.get('pair'), c.get('amount'), c.get('rate')
            total, commission, pos = pair.calc(amount, rate, ttype)
            if ttype == 'buy': pos = pair.right
            if ttype == 'sale': pos = pair.left
            valuta = pos.value
            balance = user.orders_balance(valuta)
            if ttype == 'buy': _sum = balance - total
            if ttype == 'sale': _sum = balance - amount
            if _sum >= 0:
                _ret = getattr(pair, "order_%s" % ttype)(user, amount, rate)
                dajax.remove_css_class('#{type}_form input'.format(**{"type":ttype}), 'error')
                dajax.script("location.reload();")
            else:
                text = "Сумма сделки превышает ваш баланс на {sum} {valuta}".format(**{"sum":floatformat(-_sum, -8), "valuta": pos })
                dajax.script("$('#info_{type}').text('{text}');".format(**{"type":ttype, "text":text, }))
    else:
        dajax.script("$('#info_{type}').text('{text}');".format(**{"type":ttype, "text":"Неправильно заполнено одно из полей.", }))
        for error in form.errors:
            dajax.add_css_class('#id_%s-%s' % (ttype, error), 'error')
    return dajax.json()

@dajaxice_register
def cancel(request, pk):
    dajax = Dajax()
    user=request.user
    if user.is_authenticated() and user.is_active:
        o = Orders.is_active_order(user=user, pk=pk)
        if o.exists():
            _o=o[0]
            if o.update(cancel=True) > 0:
                dajax.script("$('#active_orders_list-{pk}').remove()".format(**{"pk": pk,}))
                dajax.script("alert('ордер на сумму {sum} отменен успешно')".format(**{"sum": _o.sum_order_current}))
    return dajax.json()
