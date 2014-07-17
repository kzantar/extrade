#-*- coding:utf-8 -*-
from django.db import models

from decimal import Decimal as D, _Zero
from django.db.models import Avg, Max, Min
from django.template.defaultfilters import floatformat
from common.numeric import normalized
from django.db.models import Sum, Count, F, Q
from django.core.cache import cache



# Create your models here.

class Valuta(models.Model):
    value = models.SlugField(unique=True)
    bank = models.TextField((u'номер счета на ввод'), blank=True, null=True)
    commission_inp = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=u"коммиссия на ввод")
    commission_out = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name=u"коммиссия на вывод")
    def save(self, *args, **kwargs):
        self.value = self.value.lower()
        super(Valuta, self).save(*args, **kwargs)
    @property
    def val(self):
        return self.value
    def __unicode__(self):
        return self.value.upper()

class TypePair(models.Model):
    left = models.ForeignKey("currency.Valuta", related_name="left_right")
    right = models.ForeignKey("currency.Valuta", related_name="funds_right")
    commission = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    slug = models.SlugField(editable=False)
    #decimal_places = models.PositiveIntegerField(default=8)
    def save(self, *args, **kwargs):
        if self.pk: cache.delete(self.cache_unicode_key)
        if self.pk: cache.delete(self.cache_tpair_key)
        self.slug = u"%s_%s" % (self.left.value, self.right.value)
        super(TypePair, self).save(*args, **kwargs)
    @classmethod
    def default(cls):
        c=cls.flr()
        if c.exists():
            return c[0].slug
        return ""
    def calc(self, amount, rate, ttype, totext=None):
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
        if totext:
            return floatformat(total, -8), floatformat(commission, -8), pos
        return total, commission, pos
    def order_sale(self, user, amount, rate):
        return self.warrant_orders_related.model.sale.related.model.objects.create(user=user, amount=amount, rate=rate, pair=self)
    def order_buy(self, user, amount, rate):
        return self.warrant_orders_related.model.buy.related.model.objects.create(user=user, amount=amount, rate=rate, pair=self)
    @classmethod
    def flr(cls):
        return cls.objects.all()
    @property
    def cache_tpair_key(self):
        return 'typepair_tpair' + str(self.id)
    @property
    def cache_unicode_key(self):
        return 'typepair__unicode__' + str(self.id)
    def __unicode__(self):
        key = self.cache_unicode_key
        ret = cache.get(key)
        if ret is None:
            ret = u"{left}/{right}".format(**{"left": self.left, "right":self.right})
            cache.set(key, ret)
        return ret
    @property
    def tpair(self):
        key = self.cache_tpair_key
        ret = cache.get(key)
        if ret is None:
            ret = u"{left}/{right}".format(**{"left": self.left.value.upper(), "right":self.right.value.upper()})
            cache.set(key, ret)
        return ret
    def min_max_avg(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.min_max_avg_rate(self, to_int, to_round)
    def sum_amount(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.sum_amount(self, to_int, to_round)
    def sum_total(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.sum_total(self, to_int, to_round)
    def in_orders_sum_buy(self):
        q = self.warrant_orders_related.filter(buy__gte=1).filter(completed=False, cancel=False)
        v = _Zero
        for v1 in q.only('amount', 'rate'):
            v += v1.el._sum_ret
        return v
    def in_orders_sum_sell(self):
        q = self.warrant_orders_related.filter(sale__gte=1).filter(completed=False, cancel=False)
        v = _Zero
        for v1 in q.only('amount', 'rate'):
            v += v1.el._ret_amount
        return v
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
        for o in self.warrant_orders_related.model.buy.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).order_by("-rate").distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    def sale(self):
        for o in self.warrant_orders_related.model.sale.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).order_by("-rate").distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    @property
    def avg_rate(self):
        return self.min_max_avg(to_round=6)[2]
    @property
    def last_order(self):
        o = self.warrant_orders_related.filter(Q(cancel=True, buy__buy_buy__gte=1) | Q(completed=True)).filter(buy__gte=1).only('updated', 'rate', 'amount').order_by('-updated')
        if o.exists():
            return o[0]
    class Meta:
        unique_together = (("left", "right",),)
