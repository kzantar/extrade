from decimal import Context, setcontext, Decimal
from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_FLOOR, ROUND_HALF_DOWN, ROUND_HALF_EVEN, ROUND_HALF_UP, ROUND_UP, ROUND_05UP

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
