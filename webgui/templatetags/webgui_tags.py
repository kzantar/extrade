from django import template

from warrant.models import Orders
from currency.models import TypePair
from django.template import RequestContext
from django.template.defaultfilters import floatformat


register = template.Library()

@register.simple_tag
def get_action(user, obj):
    return obj.w_action(user)

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
