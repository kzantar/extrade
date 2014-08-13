#-*- coding:utf-8 -*-
from dajaxice.decorators import dajaxice_register
from dajaxice.utils import deserialize_form
from dajax.core import Dajax
from django.http import Http404
from django.db.models import Q
from django.conf import settings
from currency.models import TypePair, Valuta, PaymentMethod
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

from datetime import datetime


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
            if o.update(cancel=True, updated=datetime.today()) > 0:
                dajax.script("$('#active_orders_list-{pk}').remove()".format(**{"pk": pk,}))
                #dajax.script("alert('ордер на сумму {sum} отменен успешно')".format(**{"sum": _o.sum_order_current}))
                dajax.script("location.reload();")
    return dajax.json()

@dajaxice_register
def get_form_input_balance(request, valuta, paymethod=None, form=None, edit=None, cancel=None, confirm=None):
    """
    ввод
    """
    dajax = Dajax()
    args, initial = { }, { 'valuta':valuta }
    v = get_object_or_404(Valuta, pk=valuta)

    if form: edit = 1
    if form: form=deserialize_form(form)
    if form: paymethod = form.get('paymethod')

    if paymethod: paymethod = get_object_or_404(PaymentMethod, pk=paymethod, disable=False)
    if not paymethod: paymethod = v.default_paymethod_inp
    cb = ProfileBalance.exists_input(valuta, request.user, paymethod=paymethod)
    #if cb and cb.paymethod: paymethod = cb.paymethod
    if paymethod:
        args.update({ "commission": paymethod.w_is_commission, "validators": paymethod.validators })
        initial.update({ "paymethod":paymethod })

    if cb and not cb.confirm and confirm:
        cb.confirm=True
        cb.save()
        return get_form_input_balance(request, valuta, form, edit)
    if cancel and cb and not cb.confirm:
        cb.cancel=True
        cb.save()
        return get_form_input_balance(request, valuta, form, edit)
    form = AddBalanceForm(user=request.user, instance=cb, data=form, initial=initial, **args)
    if form.is_valid():
        form.instance.action="+"
        form.instance.confirm=False
        form.save()
        if cb and not (cb.confirm or cb.cancel): obj = "<p>Заявка на ввод средств успешно отредактированна.</p>"
        if not cb: obj = render_to_string("balance_form.html", {"confirm":True, "instance": form.instance, "action": "ввод", "save_now": True, "paymethods": v.paymethods_inp, "paymethod":paymethod, "functions": "get_form_input_balance", "valuta": v})
    elif cb and cb.confirm:
        obj = "<p>Заявка ожидает подтверждения.</p>" # if exists_input confirm=True
    else:
        if not edit and form.instance and form.instance.pk:
            obj = render_to_string("balance_form.html", {"confirm":True, "instance": form.instance, "action": "ввод", "cancel_or_edit": True, "paymethods": v.paymethods_inp, "paymethod":paymethod, "functions": "get_form_input_balance", "valuta": v})
        elif v.paymethods_inp.exists():
            c = {"form": form, "url": ".", "paymethods": v.paymethods_inp, "paymethod":paymethod, "submit": "пополнить %s" % v, "functions": "get_form_input_balance", "valuta": v}
            c.update(csrf(request))
            obj = render_to_string("balance_form.html", c)
        else:
            obj = """
<p>Ввод средств для {valuta} не установлен.</p>
""".format(**{"valuta": v})
    dajax.assign('#balance_form_content', 'innerHTML', obj)
    return dajax.json()

@dajaxice_register
def get_form_output_balance(request, valuta, paymethod=None, form=None, edit=None, cancel=None):
    """
    вывод
    """
    dajax = Dajax()
    args, initial = { }, { 'valuta':valuta }
    v = get_object_or_404(Valuta, pk=valuta)

    if form: edit = 1
    if form: form=deserialize_form(form)

    if form: paymethod = form.get('paymethod')
    if paymethod: paymethod = get_object_or_404(PaymentMethod, pk=paymethod, disable=False)
    if not paymethod: paymethod = v.default_paymethod_out
    cb = ProfileBalance.exists_output(valuta, request.user, paymethod=paymethod)
    if cb and cb.paymethod: paymethod = cb.paymethod
    if paymethod:
        args.update({ "commission": paymethod.w_is_commission, "validators": paymethod.validators })
        initial.update({ "paymethod":paymethod })

    if cancel:
        cb.cancel=True
        cb.save()
        return get_form_output_balance(request, valuta, form, edit, cancel=None)
    form = GetBalanceForm(user=request.user, instance=cb, data=form, initial=initial, **args)
    if form.is_valid():
        form.instance.action="-"
        form.save()
        if cb: obj = "<p>Заявка на вывод средств успешно отредактированна.</p>"
        if not cb: obj = render_to_string("balance_form.html", {"instance": form.instance, "action": "вывод", "save_now": True, "paymethods": v.paymethods_out, "paymethod":paymethod, "functions": "get_form_output_balance", "valuta": v})
    else:
        if not edit and form.instance and form.instance.pk:
            obj = render_to_string("balance_form.html", {"instance": form.instance, "action": "вывод", "cancel_or_edit": True, "paymethods": v.paymethods_out, "paymethod":paymethod, "functions": "get_form_output_balance", "valuta": v})
        elif v.paymethods_out.exists():
            c = {"form": form, "url": ".", "paymethods": v.paymethods_out, "paymethod":paymethod, "submit": "вывести %s" % v, "functions": "get_form_output_balance", "valuta": v}
            c.update(csrf(request))
            obj = render_to_string("balance_form.html", c)
        else:
            obj = """
<p>Вывод средств для {valuta} не установлен.</p>
""".format(**{"valuta": v})
    dajax.assign('#balance_form_content', 'innerHTML', obj)
    return dajax.json()


@dajaxice_register
def calc_paymethod(request, value, paymethod, act="-"):
    dajax = Dajax()
    v = get_object_or_404(PaymentMethod, pk=paymethod, disable=False)
    calc_value = v.calc_commission(D(value))
    calc_value1 = v.calc_commission(D(value), True)
    if act == "-":
        dajax.assign('#calc-value-result', 'value', floatformat(calc_value, -8).replace(",", "."))
    else:
        dajax.assign('#balance-value', 'value', floatformat(calc_value1, -8).replace(",", "."))
        dajax.assign('#calc-value-result', 'value', floatformat(value, -8).replace(",", "."))
    return dajax.json()
