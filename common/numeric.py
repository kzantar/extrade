#-*- coding:utf-8 -*-
from decimal import Context, setcontext, Decimal
from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, ROUND_05UP
from django.core.validators import BaseValidator


def normalized(d, where=None, place=8):
    amo_pla = (Decimal("10") ** -place)
    if where == 'C': where = ROUND_CEILING
    if where == 'DOWN': where = ROUND_DOWN
    if where == 'F': where = ROUND_FLOOR
    if where == 'HD': where = ROUND_HALF_DOWN
    if where == 'HE': where = ROUND_HALF_EVEN
    if where == 'HP': where = ROUND_HALF_UP
    if where == 'UP': where = ROUND_UP
    if where == '0UP': where = ROUND_05UP
    return (Decimal(d).quantize(amo_pla, rounding=where or ROUND_UP)).normalize()

def format_number(num):
    dec = Decimal(num)
    tup = dec.as_tuple()
    delta = len(tup.digits) + tup.exponent
    digits = ''.join(str(d) for d in tup.digits)
    if delta <= 0:
        zeros = abs(tup.exponent) - len(tup.digits)
        val = '0.' + ('0'*zeros) + digits
    else:
        val = digits[:delta] + ('0'*tup.exponent) + '.' + digits[delta:]
    val = val.rstrip('0')
    if val[-1] == '.':
        val = val[:-1]
    if tup.sign:
        return '-' + val
    return val

class MinValidator(BaseValidator):
    compare = lambda self, a, b: a < b
    clean = lambda self, x: x - (Decimal(10) ** -8)
    message = (u'Убедитесь, что это значение больше %(limit_value)s.')
    code = 'min_values'
