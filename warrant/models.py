#-*- coding:utf-8 -*-
from django.db import models
from common.numeric import normalized
from datetime import datetime
from django.db.models import Sum, Count, F, Q
from django.utils.html import format_html
from decimal import Decimal as D, _Zero
from django.core.cache import cache
from common.lib import strmd5sum
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator

from time import sleep

# Create your models here.
class Prop:
    def __unicode__(self):
        return u"%s %s %s %s %s %s" % (self.pk, self.pair, self.amount, self.amo_sum, self.rate, self.ret_amount)
    @property
    def amo_sum(self):
        return self._amo_sum
    @property
    def ret_amount(self):
        return self._ret_amount
    @property
    def compl(self):
        return self.completed or self._completed
    @property
    def commiss(self):
        return normalized(self._commission_debit)
    @property
    def adeudo(self):
        return u"-%s%s" % (float(self._adeudo), self._pos)
    @property
    def total(self):
        return normalized(self._total - self._commission_debit, where="DOWN")
    @property
    def part(self):
        return self._part
    def exchange(self):
        return self._exchange()

class Orders(models.Model):
    created = models.DateTimeField(editable=False, auto_now_add=True, default=datetime.now)
    updated = models.DateTimeField(editable=False, auto_now=True, default=datetime.now)
    user = models.ForeignKey('users.Profile', related_name="%(app_label)s_%(class)s_related")
    commission = models.DecimalField(u"Комиссия %", max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(_Zero)], editable=False)
    pair = models.ForeignKey("currency.TypePair", related_name="%(app_label)s_%(class)s_related")
    amount = models.DecimalField(u"Количество", max_digits=14, decimal_places=8, validators=[MinValueValidator(D("10") ** -8)])
    rate = models.DecimalField(u"Стоимость", max_digits=14, decimal_places=8, validators=[MinValueValidator(D("10") ** -8)])
    cancel = models.BooleanField(u"отменен", default=False)
    completed = models.BooleanField(u"Завершен", default=False)

#    class Meta:
#        abstract = True


class Buy(Orders, Prop):
    sale = models.ForeignKey("warrant.Sale", verbose_name=u"Продажа", blank=True, null=True, related_name="sale_sale")
    @property
    def _md5key_subtotal(self):
        s = "Buy" + str(self.pk) + str(self.pair) + str(self.updated)
        return strmd5sum(s)
    def save(self, *args, **kwargs):
        print "Buy save"
        e=Buy.objects.filter(id=self.pk).filter(Q(cancel=True) | Q(completed=True)).exists()
        #    raise ValidationError(u'Этот ордер уже отменен или исполнен.')
        if not self.commission: self.commission = self.pair.commission
        if self._completed and not self.completed:
            self.completed = True
        if self.sale and self.sale._status:
            raise ValidationError(u'Этот ордер уже отменен или исполнен.')
        super(Buy, self).save(*args, **kwargs)
        if not (self.completed or self.cancel): self.exchange()
 
    @models.permalink
    def get_absolute_url_admin_change(self):
        return ('admin:warrant_buy_change', [str(self.id)])
    def _pir(self):
        if self.buy_buy:
            s=[]
            for l in self.buy_buy.all():
                s.append(u"<a style='white-space:pre;' href=\"%s\">%s</a>" % (l.get_absolute_url_admin_change(), l))
            return u",<br>".join(s)
    _pir.allow_tags = True
    _pir.short_description="пир"
    @property
    def _status(self):
        return self._completed or self.cancel or self.completed
    @property
    def _commission_debit(self):
        if self._completed:
            return self.amount * self.commission / D(100)
        return self._amo_sum * self.commission / D(100) or _Zero
    @property
    def _total(self):
        if self._completed:
            return self.amount
        return self._amo_sum
    @property
    def _adeudo(self):
        if self._completed:
            return self.amount * self.rate
        return self._amo_sum * self.rate
    @property
    def _pos(self):
        return self.pair.right
    @property
    def _amo_sum(self):
        return self._subtotal
    # buy
    @property
    def _subtotal(self):
        md5key = self._md5key_subtotal
        a = cache.get(md5key)
        if a is None or not a > _Zero:
            a=self.buy_buy.exclude(sale_sale__gte=0).aggregate(amount_sum=Sum('amount')).get('amount_sum') or _Zero
            for c in self.buy_buy.filter(sale_sale__gte=0).distinct():
                a += c.amount - c._subtotal
            if bool(self.sale) and not a:
                a += self.amount
            cache.set(md5key, a)
        return a
    @property
    def _ret_amount(self):
        if bool(self.sale):
            return _Zero
        return self.amount - self._subtotal
    @property
    def _completed(self):
        return bool(self.sale) or self._amo_sum == self.amount
    @property
    def _part(self):
        return not self._completed
    def getForSale(self):
        ex = Q(buy__gte=0) | Q(cancel=True) | Q(completed=True)
        fl = {"pair": self.pair, "rate__lte": self.rate}
        return Sale.objects.filter(**fl).exclude(ex).only('amount', 'rate')
    def _exchange(self):
        if self._completed or self.cancel or self.completed: return True
        s = self.getForSale()
        _amo_buy = self._ret_amount
        for r in s:
            _amo_sale = r._ret_amount
            if self._completed or self.cancel or self.completed: return True
            if _amo_sale == _amo_buy:
                self.buy_buy.add(r)
                continue
            if _amo_sale <= _amo_buy:
                self.buy_buy.add(r)
                continue
            if _amo_sale >= _amo_buy:
                r._exchange()
                continue
            return True

class Sale(Orders, Prop):
    buy = models.ForeignKey("warrant.Buy", verbose_name=u"Покупка", blank=True, null=True, related_name="buy_buy")
    @property
    def _md5key_subtotal(self):
        s = "Sale" + str(self.pk) + str(self.pair) + str(self.updated)
        return strmd5sum(s)
    def save(self, *args, **kwargs):
        print "Sale save"
        e=Sale.objects.filter(id=self.pk).filter(Q(cancel=True) | Q(completed=True)).exists()
        #    raise ValidationError(u'Этот ордер уже отменен или исполнен.')
        if not self.commission: self.commission = self.pair.commission
        if self._completed and not self.completed:
            self.completed = True
        if self.buy and self.buy._status:
            raise ValidationError(u'Этот ордер уже отменен или исполнен.')
        super(Sale, self).save(*args, **kwargs)
        if not (self.completed or self.cancel): self.exchange()

    @models.permalink
    def get_absolute_url_admin_change(self):
        return ('admin:warrant_sale_change', [str(self.id)])
    def _pir(self):
        if self.sale_sale:
            s=[]
            for l in self.sale_sale.all():
                s.append(u"<a style='white-space:pre;' href=\"%s\">%s</a>" % (l.get_absolute_url_admin_change(), l))
            return format_html(",<br>".join(s))
    _pir.allow_tags = True
    _pir.short_description=u"пир"
    @property
    def _status(self):
        return self._completed or self.cancel or self.completed
    @property
    def _commission_debit(self):
        return self._total * self.commission / D(100)
    @property
    def _total(self):
        if self._completed:
            return self.amount * self.rate
        return self._amo_sum * self.rate
    @property
    def _adeudo(self):
        if self._completed:
            return self.amount
        return self._amo_sum
    @property
    def _pos(self):
        return self.pair.left
    @property
    def _amo_sum(self):
        return self._subtotal
    # sale
    @property
    def _subtotal(self):
        md5key = self._md5key_subtotal
        a = cache.get(md5key)
        if a is None or not a > _Zero:
            a=self.sale_sale.exclude(buy_buy__gte=0).aggregate(amount_sum=Sum('amount')).get('amount_sum') or _Zero
            for c in self.sale_sale.filter(buy_buy__gte=0).distinct():
                a += c.amount - c._subtotal
            if bool(self.buy) and not a:
                a += self.amount
            cache.set(md5key, a)
        return a
    @property
    def _ret_amount(self):
        if bool(self.buy):
            return _Zero
        return self.amount - self._subtotal
    @property
    def _completed(self):
        return bool(self.buy or self._amo_sum == self.amount)
    @property
    def _part(self):
        return not self._completed
    def getForBuy(self):
        ex = Q(sale__gte=0) | Q(cancel=True) | Q(completed=True)
        fl = {"pair": self.pair, "rate__gte": self.rate}
        return Buy.objects.filter(**fl).exclude(ex).only('amount', 'rate')
    def _exchange(self):
        if self._completed or self.cancel or self.completed: return True
        s = self.getForBuy()
        _amo_sale = self._ret_amount
        for r in s:
            _amo_buy = r._ret_amount
            if self._completed or self.cancel or self.completed: return True
            if _amo_buy == _amo_sale:
                self.sale_sale.add(r)
                continue
            if _amo_buy <= _amo_sale:
                self.sale_sale.add(r)
                continue
            if _amo_buy >= _amo_sale:
                r._exchange()
                continue
            return True

