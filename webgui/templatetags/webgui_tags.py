#-*- coding:utf-8 -*-
from django import template

from warrant.models import Orders
from currency.models import TypePair
from django.template import RequestContext
from django.template.defaultfilters import floatformat
import ctypes

register = template.Library()

@register.simple_tag
def get_id(user, obj, action):
    s = "O" + str(obj.commission) + str(obj.amount) + str(obj.pk) + str(obj.user.pk) + str(user.pk) + str(action)
    return ctypes.c_size_t(hash(s)).value

@register.simple_tag
def get_action(user, obj):
    return obj.w_action(user)

@register.simple_tag
def get_action_deals(user, obj):
    if obj.w_action(user) == 'sale': return "+"
    if obj.w_action(user) == 'buy': return "-"


@register.simple_tag
def get_description_deals(user, obj):
    if obj.w_action(user) == 'sale':
        return u"Продажа {w_amo_sum_total} {left} с вашего ордера #{pk} по цене {rate} {right} всего {w_total_total} {right} (-{commission}%)".format(**{
            "w_amo_sum_total": floatformat(obj.el.w_amo_sum_total, -8),
            "left": obj.el.pair.left,
            "pk": obj.pk,
            "rate": floatformat(obj.profitable.rate, -8),
            "right": obj.el.pair.right,
            "w_total_total": floatformat(obj.el.w_total_total, -8),
            "commission": obj.commission,
            })
    if obj.w_action(user) == 'buy':
        return u"Покупка {w_amo_sum_total} {left} (-{commission}%) с вашего ордера #{pk} по цене {rate} {right}".format(**{
            "w_amo_sum_total": floatformat(obj.el.w_amo_sum_total, -8),
            "left": obj.el.pair.left,
            "pk": obj.pk,
            "rate": floatformat(obj.profitable.rate, -8),
            "right": obj.el.pair.right,
            "w_total_total": floatformat(obj.el.w_total_total, -8),
            "commission": obj.commission,
            })


@register.simple_tag
def get_action_write(obj):
    if obj.is_action('sale'): return "+"
    if obj.is_action('buy'): return "-"

@register.simple_tag
def get_action_cancel(obj):
    return "+"
    #if obj.is_action('sale'): return "-"
    #if obj.is_action('buy'): return "+"

@register.inclusion_tag('information.html', takes_context=True)
def information(context):
    request = context.get('request')
    pair=context.get('typepair', None)
    if not pair:
        if request:
            slug = request.session.get('pair', None)
        else:
            slug = TypePair.default()
        pair = TypePair.flr().get(slug=slug)
    _max, _min, _avg = pair.min_max_avg_hour(to_int=True)
    sum_amount = pair.sum_amount()
    sum_total = pair.sum_total()
    return {
        'min': _min,
        'max': _max,
        'avg': _avg,
        'last_order': pair.last_order,
        'sum_amount': sum_amount,
        'sum_total': sum_total,
        'pair': pair,
    }
    return {}
