#-*- coding:utf-8 -*-
from django.db import models

from decimal import Decimal as D, _Zero
from django.db.models import Avg, Max, Min
from django.template.defaultfilters import floatformat
from common.numeric import normalized
from django.db.models import Sum, Count, F, Q
from django.core.cache import cache
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from common.numeric import MinValidator
from common.lib import strmd5sum



# Create your models here.

class PaymentMethod(models.Model):
    ACTIONS=(
        ('+', 'пополнение'),
        ('-', 'списание'),
    )
    disable = models.BooleanField(verbose_name=(u'отключить'), default=False)
    enable_user_bank = models.BooleanField(verbose_name=(u'Включить пользовательские реквизиты'), default=False)
    enable_account_number = models.BooleanField(verbose_name=(u'уникальный номер счета из списка'), help_text=u"<a href='../../../users/profilepaynumber/'>cписок</a>", default=False)
    method = models.CharField((u'Метод оплаты'), max_length=255)
    action = models.CharField((u'действие'), choices=ACTIONS, max_length=1, validators=[RegexValidator(regex='^[+-]$', message=u'не допускаются значения кроме [+-]', code='invalid_action')])
    commission = models.DecimalField(u"Комиссия %", max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(_Zero)])
    min_commission = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Минимальная комиссия", validators=[MinValueValidator(_Zero)])
    max_commission = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Максимальная комиссия", validators=[MinValueValidator(_Zero)])
    min_amount = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Минимальная сумма", validators=[MinValueValidator(_Zero)])
    max_amount = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Максимальная сумма", validators=[MinValueValidator(_Zero)])
    valuta = models.ForeignKey("currency.Valuta", related_name="payment_method")
    bank = models.TextField((u'номер счета'), blank=True, null=True, help_text=u"При включенной опции 'уникальный номер счета из списка', номер подставляется в значение {{ pay_number }}<br>Виден после создания заявки.")
    description_bank = models.TextField((u'описание'), blank=True, null=True, help_text=u"видно до создания заявки")
    def calc_commission(self, amount, rev=False):
        if self.min_commission > _Zero and (amount * self.commission / D(100)) < self.min_commission:
            if rev: return amount + self.min_commission
            return amount - self.min_commission
        elif self.max_commission > _Zero and (amount * self.commission / D(100)) > self.max_commission:
            if rev:return amount + self.max_commission
            return amount - self.max_commission
        else:
            if rev: return amount / (D(1) - self.commission / D(100))
            return amount * (D(1) - self.commission / D(100))
    @property
    def w_min_commission(self):
        return u"мин. {amount} {valuta}".format(**{ "amount":floatformat(self.min_commission, -8), "valuta":self.valuta })
    @property
    def w_max_commission(self):
        return u"макс. {amount} {valuta}".format(**{ "amount":floatformat(self.max_commission, -8), "valuta":self.valuta })
    @property
    def w_commission(self):
        if self.commission > _Zero:
            return u"{commission}% ".format(**{"commission": floatformat(self.commission, -2)})
        return ""
    @property
    def w_is_commission(self):
        return self.max_commission > _Zero or self.min_commission > _Zero or self.commission > _Zero
    @property
    def w_commissions(self):
        if self.w_is_commission:
            s, st=[], ""
            if self.min_commission > _Zero:
                s += [(self.w_min_commission),]
            if self.max_commission > _Zero:
                s += [(self.w_max_commission),]
            if s:
                st = u", ".join(s)
                if self.commission > _Zero:
                    st = "(" + st + ")"
            return u"Комиссия {commission}{min_max}".format(**{"min_max": st, "commission": self.w_commission})
        return ""
    @property
    def w_method(self):
        return u"{method} [{commission}%]".format(**{"commission": self.commission, "action": self.get_action_display(), "method": self.method})
    @property
    def validators(self):
        v = []
        if self.min_amount <= self.min_commission and self.min_commission: v+= [MinValidator(self.min_commission), ]
        if self.min_amount > self.min_commission and self.min_amount: v += [MinValueValidator(self.min_amount), ]
        if self.max_amount: v += [MaxValueValidator(self.max_amount), ]
        return v
    @classmethod
    def commission_default_inp(cls):
        if cls.inp().exists():
            return cls.inp()[0].commission
        return _Zero
    @classmethod
    def commission_default_out(cls):
        if cls.out().exists():
            return cls.out()[0].commission
        return _Zero
    @classmethod
    def validators_default_inp(cls):
        if cls.inp().exists():
            return cls.inp()[0].validators
        return [MinValueValidator(_Zero)]
    @classmethod
    def validators_default_out(cls):
        if cls.out().exists():
            return cls.out()[0].validators
        return [MinValueValidator(_Zero)]
    @classmethod
    def inp(cls):
        return cls.objects.filter(action="+", disable=False)
    @classmethod
    def out(cls):
        return cls.objects.filter(action="-", disable=False)
    def __unicode__(self):
        return u"{action} {method} [{commission}%]".format(**{"commission": self.commission, "action": self.get_action_display(), "method": self.method})
    class Meta:
        verbose_name = u'метод оплаты'
        verbose_name_plural = u'методы оплаты'

class Valuta(models.Model):
    value = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        self.value = self.value.lower()
        super(Valuta, self).save(*args, **kwargs)
    @property
    def paymethods_inp(self):
        p = self.payment_method.filter(action="+", disable=False)
        if self.payment_method.exists() and p.exists():
            return p
        return self.payment_method.none()
    @property
    def paymethods_out(self):
        p = self.payment_method.filter(action="-", disable=False)
        if self.payment_method.exists() and p.exists():
            return p
        return self.payment_method.none()
    def default_paymethod(self, action):
        if self.payment_method.filter(action=action, disable=False).exists():
            return self.payment_method.filter(action=action, disable=False)[0]
        return self.payment_method.none()
    @property
    def default_paymethod_inp(self):
        return self.default_paymethod("+")
    @property
    def default_paymethod_out(self):
        return self.default_paymethod("-")
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
    def cache_lastorder_key(self):
        return 'lastorder' + str(self.id)
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
    def min_max_avg_hour(self, to_int=None, to_round=None):
        return self.warrant_orders_related.model.min_max_avg_rate_hour(self, to_int, to_round)
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
        for o in self.warrant_orders_related.model.buy.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).order_by("-rate", '-amount').distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    def sale(self):
        for o in self.warrant_orders_related.model.sale.related.model.objects.filter(pair=self).exclude(Q(cancel=True) | Q(completed=True)).order_by("rate", '-amount').distinct():
            yield o.rate, o.ret_amount, o.ret_sum
    @property
    def avg_rate(self):
        return self.min_max_avg(to_round=6)[2]
    @property
    def last_rate(self):
        if self.last_order:
            return float('{0:.7g}'.format(self.last_order.rate))
        return _Zero
    @property
    def last_order(self):
        c = self.warrant_orders_related.count()
        key = self.cache_lastorder_key + str(c)
        o = cache.get(key)
        if o is None:
            o = self.warrant_orders_related.filter(
                    Q(
                        sale__buy__completed=True,
                    ) | Q(
                        buy__sale__completed=True,
                    ) | Q(
                        completed=True,
                    ), Q(
                        sale__buy__gte=1,
                    ) | Q(
                        buy__sale__gte=1,
                    )
                ).only('updated', 'rate', 'amount').distinct(
                    ).order_by('-updated')
            cache.set(key, o)
            #o = self.warrant_orders_related.filter(Q(cancel=True, buy__buy_buy__gte=1) | Q(completed=True)).filter(buy__gte=1).only('updated', 'rate', 'amount').order_by('-updated', '-created')
        if o.exists():
            return o[0]
        return o.none()
    class Meta:
        unique_together = (("left", "right",),)
