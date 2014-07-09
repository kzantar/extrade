#-*- coding:utf-8 -*-
from django.db import models

from decimal import Decimal as D, _Zero
from django.db.models import Avg, Max, Min
from django.template.defaultfilters import floatformat
from common.numeric import normalized
from django.db.models import Sum, Count, F, Q



# Create your models here.

class Valuta(models.Model):
    value = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        self.value = self.value.lower()
        super(Valuta, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.value.upper()

class TypePair(models.Model):
    left = models.ForeignKey("currency.Valuta", related_name="left_right")
    right = models.ForeignKey("currency.Valuta", related_name="funds_right")
    commission = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    slug = models.SlugField(editable=False)
    #decimal_places = models.PositiveIntegerField(default=8)
    def save(self, *args, **kwargs):
        self.slug = u"%s_%s" % (self.left.value, self.right.value)
        super(TypePair, self).save(*args, **kwargs)
    @classmethod
    def default(cls):
        c=cls.flr()
        if c.exists():
            return c[0].slug
        return ""
    def calc(self, amount, rate, ttype):
        amount = D(amount)
        rate = D(rate)
        total = normalized(amount * rate, where="DOWN")
        if ttype== 'sale':
            _amo = total
            pos = self.right
        else:
            _amo = amount
            pos = self.left
        commission = normalized(_amo * self.commission / D(100))
        return floatformat(total, -8), floatformat(commission, -8), pos
    def order_sale(self, user, amount, rate):
        return self.warrant_orders_related.model.sale.related.model.objects.create(user=user, amount=amount, rate=rate, pair=self)
    def order_buy(self, user, amount, rate):
        return self.warrant_orders_related.model.buy.related.model.objects.create(user=user, amount=amount, rate=rate, pair=self)
    @classmethod
    def flr(cls):
        return cls.objects.all()
    def __unicode__(self):
        return u"{left}/{right}".format(**{"left": self.left, "right":self.right})
    @property
    def tpair(self):
        return u"{left}/{right}".format(**{"left": self.left.value.upper(), "right":self.right.value.upper()})
    def min_max_avg(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.min_max_avg_rate(self, to_int, to_round)
    def sum_amount(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.sum_amount(self, to_int, to_round)
    def sum_total(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.sum_total(self, to_int, to_round)
    @property
    def sumamount(self):
        _sum = self.sum_amount(to_round=2)
        return u"{sum}".format(**{"sum":_sum,})
    @property
    def sumtotal(self):
        _sum = self.sum_total(to_round=2)
        return u"{sum}".format(**{"sum":_sum,})
    @property
    def min_max(self):
        v = self.min_max_avg(to_int=True)
        _min = v.pop()
        _max = v.pop()
        return u"{min} / {max}".format(**{"min":_min, "max":_max,})
    @property
    def _min_max(self):
        v = self.min_max_avg(to_int=True)
        _min = v.pop()
        _max = v.pop()
        return _min, _max
    def history(self):
        return self.warrant_orders_related.model.history(pair=self)
    def actives(self, user):
        return self.warrant_orders_related.model.actives(user=user, pair=self)
    def buy(self):
        for o in self.warrant_orders_related.model.buy.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    def sale(self):
        for o in self.warrant_orders_related.model.sale.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    @property
    def avg_rate(self):
        return self.min_max_avg(to_int=True)[2]
    @property
    def last_order(self):
        o = self.warrant_orders_related.filter(Q(cancel=True) | Q(completed=True))
        if o.exists():
            return self.warrant_orders_related.filter(Q(cancel=True) | Q(completed=True))[0]
    class Meta:
        unique_together = (("left", "right",),)
