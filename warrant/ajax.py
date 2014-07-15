#-*- coding:utf-8 -*-
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
from django.http import Http404
from django.db.models import Q
from django.conf import settings
from currency.models import TypePair, Valuta
from warrant.forms import OrdersForm
from warrant.models import Orders
from users.forms import AddBalanceForm, GetBalanceForm
from users.models import ProfileBalance

from django.template.defaultfilters import floatformat
from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.shortcuts import get_object_or_404

from decimal import Decimal as D, _Zero
from common.numeric import normalized

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
                #dajax.script("alert('ордер на сумму {sum} отменен успешно')".format(**{"sum": _o.sum_order_current}))
                dajax.script("location.reload();")
    return dajax.json()

@dajaxice_register
def get_form_input_balance(request, valuta, form=None, edit=None, cancel=None):
    """
    ввод
    """
    dajax = Dajax()
    v = get_object_or_404(Valuta, pk=valuta)
    if form: edit = 1
    if form: form=deserialize_form(form)
    cb = ProfileBalance.exists_input(valuta, request.user)
    if cancel:
        cb.cancel=True
        cb.save()
        return get_form_input_balance(request, valuta, form, edit, cancel=None)
    form = AddBalanceForm(user=request.user, instance=cb, data=form, initial={'valuta':valuta}, commission=v.commission_inp)
    if form.is_valid():
        form.instance.action="+"
        form.save()
        if cb: obj = "<p>Заявка на ввод средств успешно отредактированна.</p>"
        if not cb: obj = "<p>Заявка на ввод средств успешно создана.</p>"
    else:
        if not edit and form.instance and form.instance.pk:
            obj = """
<p>Вы уже создали заявку на ввод средств.</p>
<p>Её можно <a href="#" onclick="Dajaxice.warrant.get_form_input_balance(Dajax.process, {{'valuta': '{valuta}', 'edit':'1'}});return false;">отредактировать</a>
заново или <a href="#" onclick="Dajaxice.warrant.get_form_input_balance(Dajax.process, {{'cancel': 1, 'valuta': '{valuta}'}});return false;">отменить</a></p>
""".format(**{"valuta": form.instance.valuta.pk})
        else:
            c = {"form": form, "url": ".", "submit": "пополнить %s" % v, "functions": "get_form_input_balance", "valuta": v}
            c.update(csrf(request))
            obj = render_to_string("balance_form.html", c)
    dajax.assign('#balance_form_content', 'innerHTML', obj)
    return dajax.json()

@dajaxice_register
def get_form_output_balance(request, valuta, form=None, edit=None, cancel=None):
    """
    вывод
    """
    dajax = Dajax()
    v = get_object_or_404(Valuta, pk=valuta)
    if form: edit = 1
    if form: form=deserialize_form(form)
    cb = ProfileBalance.exists_output(valuta, request.user)
    if cancel:
        cb.cancel=True
        cb.save()
        return get_form_output_balance(request, valuta, form, edit, cancel=None)
    form = GetBalanceForm(user=request.user, instance=cb, data=form, initial={'valuta':valuta}, commission=v.commission_inp)
    if form.is_valid():
        form.instance.action="-"
        form.save()
        if cb: obj = "<p>Заявка на вывод средств успешно отредактированна.</p>"
        if not cb: obj = "<p>Заявка на вывод средств успешно создана.</p>"
    else:
        if not edit and form.instance and form.instance.pk:
            obj = """
<p>Вы уже создали заявку на вывод средств.</p>
<p>Её можно <a href="#" onclick="Dajaxice.warrant.get_form_output_balance(Dajax.process, {{'valuta': '{valuta}', 'edit':'1'}});return false;">отредактировать</a>
заново или <a href="#" onclick="Dajaxice.warrant.get_form_output_balance(Dajax.process, {{'cancel': 1, 'valuta': '{valuta}'}});return false;">отменить</a></p>
""".format(**{"valuta": form.instance.valuta.pk})
        else:
            c = {"form": form, "url": ".", "submit": "вывести %s" % v, "functions": "get_form_output_balance"}
            c.update(csrf(request))
            obj = render_to_string("balance_form.html", c)
    dajax.assign('#balance_form_content', 'innerHTML', obj)
    return dajax.json()


@dajaxice_register
def calc_inp(request, value, valuta, act="-"):
    dajax = Dajax()
    v = get_object_or_404(Valuta, pk=valuta)

    calc_value = normalized(D(value) * (D(1) - v.commission_inp / D(100) ), where="DOWN") or _Zero
    calc_value1 = normalized(D(value) / (D(1) - v.commission_inp / D(100) ), where="C") or _Zero
    if act == "-":
        dajax.assign('#calc-value-result', 'value', floatformat(calc_value, -8).replace(",", "."))
    else:
        dajax.assign('#balance-value', 'value', floatformat(calc_value1, -8).replace(",", "."))
        dajax.assign('#calc-value-result', 'value', floatformat(value, -8).replace(",", "."))
    return dajax.json()

@dajaxice_register
def calc_out(request, value, valuta, act="-"):
    dajax = Dajax()
    v = get_object_or_404(Valuta, pk=valuta)
    calc_value = normalized(D(value) * (D(1) - v.commission_out / D(100) ), where="DOWN") or _Zero
    calc_value1 = normalized(D(value) / (D(1) - v.commission_out / D(100) ), where="C") or _Zero

    if act == "-":
        dajax.assign('#calc-value-result', 'value', floatformat(calc_value, -8).replace(",", "."))
    else:
        dajax.assign('#balance-value', 'value', floatformat(calc_value1, -8).replace(",", "."))
        dajax.assign('#calc-value-result', 'value', floatformat(value, -8).replace(",", "."))
    return dajax.json()
