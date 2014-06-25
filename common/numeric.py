from decimal import Context, setcontext, ROUND_UP, ROUND_DOWN, Decimal

def normalize(d, where=None, place=8):
    amo_pla = (Decimal("10") ** -place)
    if where == 'UP': where = ROUND_UP
    if where == 'DOWN': where = ROUND_DOWN
    return (Decimal(d).quantize(amo_pla, rounding=where or ROUND_UP)).normalize()
