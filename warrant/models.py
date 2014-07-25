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
from django.db.models import Avg, Max, Min
from django.contrib.auth.models import User
from django.template.defaultfilters import floatformat

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
    def ret_sum(self):
        return self.ret_amount * self.rate
    @property
    def compl(self):
        return self.completed or self._completed
    @property
    def commiss(self):
        return floatformat(normalized(self._commission_debit), -8)
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
    @classmethod
    def flr(cls, pair=None):
        return cls.objects.exclude(Q(cancel=True) | Q(completed=True)).filter(pair=pair)

class Orders(models.Model):
    created = models.DateTimeField(editable=False, auto_now_add=True, default=datetime.now)
    updated = models.DateTimeField(editable=False, auto_now=True, default=datetime.now)
    user = models.ForeignKey('users.Profile', related_name="%(app_label)s_%(class)s_related")
    commission = models.DecimalField(u"Комиссия %", max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(_Zero)], editable=False)
    pair = models.ForeignKey("currency.TypePair", related_name="%(app_label)s_%(class)s_related")
    amount = models.DecimalField(u"Количество", max_digits=14, decimal_places=8, validators=[MinValueValidator(D("10") ** -7)])
    rate = models.DecimalField(u"Стоимость", max_digits=14, decimal_places=8, validators=[MinValueValidator(D("10") ** -7)])
    cancel = models.BooleanField(u"отменен | отменен частично", default=False)
    completed = models.BooleanField(u"Завершен", default=False)
    @property
    def w_status(self):
        if self.el.completed: return "Исполнен"
        if self.el.cancel: return "Отменен"
        if not self.el._status: return "Активен"
    @property
    def w_percent(self):
        return int((self.amount - self.el.ret_amount) / self.amount * 100)
    @property
    def status(self):
        return self.el._status
    @property
    def el(self):
        if self.is_action('sale'):
            return self.sale
        if self.is_action('buy'):
            return self.buy
    @property
    def it(self):
        if self.is_action('buy'):
            return self.buy
        if self.is_action('sale'):
            return self.sale
    def w_action(self, user):
        return self.el._w_action(user)
    @property
    def current(self):
        return self.el.get_rate
    @property
    def profitable(self):
        return self.el.get_rate
    @classmethod
    def set_completed(cls, pk):
        return cls.objects.filter(id=pk).update(completed=True)
    @classmethod
    def is_active_order(cls, user, pk):
        return cls.objects.filter(id=pk).exclude(Q(cancel=True) | Q(completed=True))
    @property
    def sum_order_current(self):
        if self.is_action('sale'): res = self.sale._sum_ret
        if self.is_action('buy'): res = self.buy._ret_amount
        return floatformat(res, -8)
    @classmethod
    def sum_from_user_buy_sale(cls, user, valuta):
        _c1 = cls.objects.filter(user=user).count()
        _c2 = cls.objects.filter(Q(buy__user=user) | Q(sale__user=user)).count()
        _c3 = cls.objects.filter(Q(buy__user=user) | Q(sale__user=user) | Q(sale__sale_sale__user=user) | Q(buy__buy_buy__user=user)).count()
        _c4 = cls.objects.filter(cancel=False).count()
        _c5 = cls.objects.filter(completed=True).count()
        _md5key = strmd5sum("sum" + str(_c1) + str(_c2) + str(_c3) + str(_c4) + str(_c5) + str(user.pk) + str(valuta))
        _s = cache.get(_md5key)
        if _s is None:
            obj = cls.objects.filter(
                    user=user
                ).filter(
                    Q(pair__left__value=valuta) |
                    Q(pair__right__value=valuta)
                ).only('pair', 'rate', 'amount').distinct()
            _s=_Zero
            for c in obj:
                print c.el.pair.left.value, c.el.pair.right.value, valuta
                if c.is_action('sale'):
                    if c.sale.pair.left.value == valuta:
                        #print "AAA btc", valuta
                        _s += c.sale._debit_left
                        # btc
                    if c.sale.pair.right.value == valuta:
                        #print "BBB usd", valuta
                        _s -= c.sale._debit_right
                        # usd
                if c.is_action('buy'):
                    if c.buy.pair.left.value == valuta:
                        # btc
                        _s -= c.buy._debit_left
                        #print "CCC btc", valuta
                    if c.buy.pair.right.value == valuta:
                        #print "DDD usd", valuta
                        # usd
                        _s += c.buy._debit_right
            cache.set(_md5key, _s)
        print "total:", _s, valuta
        return _s
    @classmethod
    def min_buy_rate(cls, pair):
        return cls.objects.filter(
            pair=pair, sale__gte=1
            ).exclude(
            Q(cancel=True) | Q(completed=True)
            ).aggregate(Min('rate')).values()[0] or _Zero
    @classmethod
    def max_sale_rate(cls, pair):
        return cls.objects.filter(
            pair=pair, buy__gte=1
            ).exclude(
            Q(cancel=True) | Q(completed=True)
            ).aggregate(Max('rate')).values()[0] or _Zero
    @classmethod
    def min_max_avg_rate(cls, pair, to_int=None, to_round=None):
        r = cls.objects.filter(pair=pair).exclude(Q(cancel=True) | Q(completed=True)).aggregate(Avg('rate'))
        v=[cls.min_buy_rate(pair), cls.max_sale_rate(pair), r.get('rate__avg')]
        v = [x if not x is None else _Zero for x in v]
        if to_int: return [x.__int__() for x in v]
        if to_round: return [round(x, to_round) for x in v]
        return v
    @classmethod
    def sum_amount(cls, pair, to_int=None, to_round=None):
        q = cls.objects.filter(pair=pair, buy__gte=1)
        v = q.filter(completed=True).aggregate(Sum('amount')).values()[0] or _Zero
        for v1 in q.filter(completed=False).only('amount', 'rate'):
            v += v1.el._total
        if v is None: v = _Zero
        if to_int: return v.__int__()
        if to_round: return round(v, to_round)
        return v
    @classmethod
    def sum_total(cls, pair, to_int=None, to_round=None):
        q = cls.objects.filter(pair=pair).filter(sale__gte=1)
        v = q.filter(completed=True).extra(select={'total_sum':"sum(rate * amount)"},).get().total_sum or _Zero
        for v1 in q.filter(completed=False).only('amount', 'rate'):
            v += v1.el._total
        if v is None: v = _Zero
        if to_int: return v.__int__()
        if to_round: return round(v, to_round)
        return v
    @classmethod
    def actives(cls, user, pair=None):
        for o in cls.objects.filter(
                pair=pair, user=user
            ).exclude(
                Q(cancel=True) |
                Q(completed=True)
            ).only('updated', 'rate', 'amount').distinct(
            ).order_by('-rate'):
            if o.is_action('sale'):
                yield o.updated.strftime("%d.%m.%y %H:%M"), "sell", o.rate, o.el._ret_amount, o.el._sum_ret, o.pk
            if o.is_action('buy'):
                yield o.updated.strftime("%d.%m.%y %H:%M"), "buy", o.rate, o.el._ret_amount, o.el._sum_ret, o.pk
    @classmethod
    def history(cls, pair=None):
        for o in cls.objects.filter(
                    pair=pair
                ).filter(
                    Q(cancel=True, buy__buy_buy__gte=1) |
                    Q(cancel=True, sale__sale_sale__gte=1) |
                    Q(completed=True)
                ).only('updated', 'rate', 'amount').distinct(
                ).order_by('-updated')[:40]:
            if o.is_action('sale'):
                yield o.updated.strftime("%d.%m.%y %H:%M"), "sell", o.rate, o.amount, o.total, o.pk
            if o.is_action('buy'):
                yield o.updated.strftime("%d.%m.%y %H:%M"), "buy", o.rate, o.amount, o.total, o.pk
    @property
    def _keys(self):
        s = "key2" + str(self.pk) + str(self.updated) + str(getattr(self, "%s_%s" % (self.action,) * 2).count()) + self.action
        #print "s"
        return s
    @property
    def action(self):
        md5key = strmd5sum("order actions" + str(self.pk))
        a = cache.get(md5key)
        if a is None:
            if hasattr(self, 'sale'): a='sale'
            if hasattr(self, 'buy'): a='buy'
            cache.set(md5key, a)
        return a
    def is_action(self, action):
        return self.action == action
    @property
    def total(self):
        return self.amount * self.rate
    @property
    def _left(self):
        return self.pair.left
    @property
    def _right(self):
        return self.pair.right

class Buy(Orders, Prop):
    sale = models.ForeignKey("warrant.Sale", verbose_name=u"Продажа", blank=True, null=True, related_name="sale_sale")
    @property
    def _md5key_total(self):
        s = "Buy _md5key_total" + self._keys
        return strmd5sum(s)
    @property
    def _md5key_subtotal(self):
        s = "Buy _md5key_subtotal" + self._keys
        return strmd5sum(s)
    @property
    def _md5key_adeudo(self):
        s = "Buy _md5key__adeudo" + self._keys
        return strmd5sum(s)
    @property
    def _keys(self):
        s = "key1" + str(self.pk) + str(self.updated) + str(self.buy_buy.count())
        if not self.sale is None: s += str('sale')
        return s
    def save(self, *args, **kwargs):
        self.updated = datetime.today()
        if not self.commission: self.commission = self.pair.commission
        if self._completed and not self.completed:
            self.completed = True
        #if self.sale and self.sale._status:
        #    raise ValidationError(u'Этот ордер уже отменен или исполнен.')
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
    def _w_action(self, user):
        if user == self.user:
            return "buy"
        else:
            return "sale"
    @property
    def _status(self):
        return self._completed or self.cancel or self.completed
    @property
    def _commission_debit(self):
        if self._completed:
            return self.amount * self.commission / D(100)
        return self._amo_sum * self.commission / D(100) or _Zero
    @property
    def _sum_ret(self):
        return self._ret_amount * self.rate
    # buy
    # менее выгодная цена, купить дороже
    # выгодная цена - дешевле
    @property
    def get_rate(self):
        _sale = self.sale
        _buy = self
        if _sale and _sale.created <= _buy.created:
            return _sale
        return _buy
    @property
    def _rate(self):
        return self.get_rate.rate
    @property
    def _total(self):
        if self._completed:
            return self.amount
        return self._amo_sum
    @property
    def _adeudo(self):
        buy = self.buy_buy
        a = _Zero
        if self._status:
            if self.cancel:
                print self.pk, self._part_amo_sum * self._rate, "EEE"
                pass
            else:
                a = self._part_amo_sum * self._rate
        else:
            a = self._ret_amount * self.rate
        if not a and buy.exists() and self.sale is None:
            a=_Zero
        if buy.exists():
            for c in buy.exclude():
                a += c._part_amo_sum * c._rate
        print "ss", self.pk, a
        return a
    @property
    def _debit_left(self):
        # btc
        #return self._total
        return normalized(self._total - self._commission_debit, where="DOWN")
    @property
    def _debit_right(self):
        # usd
        return self._adeudo
    @property
    def _pos(self):
        return self.pair.right
    @property
    def _amo_sum(self):
        return self._subtotal
    @property
    def _part_amo_sum(self):
        if self._subtotal > _Zero:
            return (self.amount - self._subtotal) or self.amount
        return _Zero
    @property
    def w_amo_sum(self):
        return self._part_amo_sum
    @property
    def w_total(self):
        return self.w_amo_sum * self._rate
    # buy
    @property
    def _subtotal(self):
        md5key = self._md5key_subtotal
        a = cache.get(md5key)
        if a is None:
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
        ex = Q(buy__gte=0) | Q(cancel=True) | Q(completed=True) | Q(user=self.user)
        fl = {"pair": self.pair, "rate__lte": self.rate}
        return Sale.objects.select_for_update().filter(**fl).exclude(ex).only('amount', 'rate')
    def _exchange(self):
        if self._completed or self.cancel or self.completed: return True
        s = self.getForSale()
        #_amo_buy = self._ret_amount
        for r in s:
            if self._completed or self.cancel or self.completed: return True
            if r._ret_amount == self._ret_amount:
                self.buy_buy.add(r)
                Orders.set_completed(self.pk)
                return True
            if r._ret_amount < self._ret_amount:
                self.buy_buy.add(r)
                Orders.set_completed(r.pk)
                return self._exchange()
            if r._ret_amount >= self._ret_amount:
                r._exchange()
                return True
            return True

class Sale(Orders, Prop):
    buy = models.ForeignKey("warrant.Buy", verbose_name=u"Покупка", blank=True, null=True, related_name="buy_buy")
    @property
    def _md5key_total(self):
        s = "Sale _md5key_total" + self._keys
        return strmd5sum(s)
    @property
    def _md5key_subtotal(self):
        s = "Sale _md5key_subtotal" + self._keys
        return strmd5sum(s)
    @property
    def _keys(self):
        s = "key" + str(self.pk) + str(self.updated) + str(self.sale_sale.count())
        if not self.buy is None: s += str('buy')
        return s
    def save(self, *args, **kwargs):
        self.updated = datetime.today()
        if not self.commission: self.commission = self.pair.commission
        if self._completed and not self.completed:
            self.completed = True
        #if self.buy and self.buy._status:
        #    raise ValidationError(u'Этот ордер уже отменен или исполнен.')
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
    def _w_action(self, user):
        if user == self.user:
            return "sale"
        else:
            return "buy"
    @property
    def _status(self):
        return self._completed or self.cancel or self.completed
    @property
    def _commission_debit(self):
        return self._total * self.commission / D(100)
    @property
    def _sum_ret(self):
        return self._ret_amount * self._rate
        s = _Zero
        for el in self.sale_sale.all():
            s += el._adeudo
        return s
    # sale
    # менее выгодная цена, продать дешевле
    # выгодная цена - дороже
    @property
    def get_rate(self):
        _sale = self
        _buy = self.buy
        if _buy:
            if _sale.created <= _buy.created:
                return _sale
            return _buy
        return _sale
    @property
    def _rate(self):
        return self.get_rate.rate
    @property
    def _total(self):
        sale = self.sale_sale
        a = _Zero
        if self._status:
            a = self._part_amo_sum * self._rate
        #else:
        #    a = self.amount * self.rate
        if sale.exists() and self.buy is None:
            a = _Zero
        if sale.exists():
            for c in sale.exclude():
                a += c._part_amo_sum * c._rate
        return a
    @property
    def _adeudo(self):
        if self._completed:
            return self.amount
        return self._amo_sum
    @property
    def _debit_left(self):
        # btc
        if not self.cancel:
            return self.amount
        return self._adeudo
    @property
    def _debit_right(self):
        # usd
        #return self._total
        return normalized(self._total - self._commission_debit, where="DOWN")
    @property
    def _pos(self):
        return self.pair.left
    @property
    def _amo_sum(self):
        return self._subtotal
    @property
    def _part_amo_sum(self):
        if self._subtotal > _Zero:
            return (self.amount - self._subtotal) or self.amount
        return _Zero
    @property
    def w_amo_sum(self):
        return self._part_amo_sum
    @property
    def w_total(self):
        return self.w_amo_sum * self._rate
    # sale
    @property
    def _subtotal(self):
        md5key = self._md5key_subtotal
        a = cache.get(md5key)
        if a is None:
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
        ex = Q(sale__gte=0) | Q(cancel=True) | Q(completed=True) | Q(user=self.user)
        fl = {"pair": self.pair, "rate__gte": self.rate}
        return Buy.objects.select_for_update().filter(**fl).exclude(ex).only('amount', 'rate')
    def _exchange(self):
        if self._completed or self.cancel or self.completed: return True
        s = self.getForBuy()
        #_amo_sale = self._ret_amount
        for r in s:
            _amo_buy = r._ret_amount
            if self._completed or self.cancel or self.completed: return True
            if r._ret_amount == self._ret_amount:
                self.sale_sale.add(r)
                Orders.set_completed(self.pk)
                return True
            if r._ret_amount < self._ret_amount:
                self.sale_sale.add(r)
                Orders.set_completed(r.pk)
                return self._exchange()
            if r._ret_amount >= self._ret_amount:
                r._exchange()
                return True
            return True
