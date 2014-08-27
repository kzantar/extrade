#-*- coding:utf-8 -*-
from django.db import models
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from decimal import Decimal as D, _Zero
from django.core.validators import RegexValidator, MinValueValidator
from currency.models import Valuta
from django.db.models import Avg, Max, Min, Sum
from django.template.defaultfilters import floatformat
from warrant.models import Orders
from django.core.cache import cache
from common.lib import strmd5sum
from django.utils.safestring import mark_safe
from common.numeric import normalized
from datetime import datetime
import ctypes

from django.core.exceptions import ValidationError


# Create your models here.


class MyCustomUserManager(BaseUserManager):
    def create_user(self, email, username='', password=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=MyCustomUserManager.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        u = self.create_user(email, email, password=password)
        u.is_active = u.is_staff = u.is_superuser = True
        u.save(using=self._db)
        return u


class Profile(AbstractBaseUser, PermissionsMixin):
    username = models.CharField((u'Имя пользователя'), max_length=40, unique=True)
    email = models.EmailField('E-mail', unique=True)
    pair = models.ForeignKey("currency.TypePair", blank=True, null=True, editable=False)
    date_joined = models.DateTimeField(
        (u'Дата регистрации'), default=timezone.now)
    is_active = models.BooleanField(
        (u'Активный'), default=True,
        help_text=(u'Отметьте, если пользователь должен считаться активным. '
                    u'Уберите эту отметку вместо удаления аккаунта.'))
    is_staff = models.BooleanField(
        (u'Статус персонала'), default=False,
        help_text=(u'Отметьте, если пользователь может входить в '
                    u'административную часть сайта.'))
    class Meta:
        verbose_name = (u'Профиль')
        verbose_name_plural = (u'Профили')

    USERNAME_FIELD = 'email'

    objects = MyCustomUserManager()

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def email_user(self, subject, message, from_email=None):
        send_mail(subject, message, from_email, [self.email])

    def get_role(self):
        """if cache.get('get_role_%s' % self.pk) is None:
            cache.set(
                'get_role_%s' % self.pk,
                [x['role'] for x in self.profilerole_set.all().values('role')] or ['client'])
        return cache.get('get_role_%s' % self.pk) or list()
        """
        return [x['role'] for x in self.profilerole_set.all().values('role')] or ['customer']

    def is_performer(self):
        performer = self.get_role()
        if 'manager' in performer:
            performer.remove('manager')
        if performer:
            return True
        return False

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        return super(Profile, self).save(*args, **kwargs)

    def _user_balance(self, valuta):
        q=self.profilebalance_set.filter(valuta__value=valuta, profile=self, cancel=False, confirm=True)
        _c1 = q.filter(accept=True).count()
        _c2 = q.aggregate(Sum('value')).values()[0] or _Zero
        md5key = strmd5sum("_user_balance" + str(q.count()) + str(valuta) + str(self.pk) + str(_c1) + str(_c2))
        b = cache.get(md5key)
        if b is None:
            balance_plus = q.filter(
                    action="+", accept=True
                ).distinct(
                ).extra(
                    select={
                        'total':"""sum(
                            CASE
                                WHEN users_profilebalance.min_commission and (users_profilebalance.value * users_profilebalance.commission / 100) < users_profilebalance.min_commission THEN users_profilebalance.value - users_profilebalance.min_commission
                                WHEN users_profilebalance.max_commission > 0 and (users_profilebalance.value * users_profilebalance.commission / 100) > users_profilebalance.max_commission THEN users_profilebalance.value - users_profilebalance.max_commission
                                ELSE (users_profilebalance.value * (1 - users_profilebalance.commission / 100))
                            END
                            )"""
                        },
                ).get(
                ).total or _Zero
            balance_plus = normalized(balance_plus, where="DOWN")
            balance_minus = q.filter(action="-").distinct().extra(select={'total':"sum(users_profilebalance.value)"},).get().total or _Zero
            balance_minus = normalized(balance_minus, where="DOWN")
            b = balance_plus - balance_minus
            cache.set(md5key, b)
        return b

    def finances(self):
        for v in Valuta.objects.all():
            yield v, self.orders_balance(v.value), v.pk

    def commission_records_orders(self):
        for v in Valuta.objects.all():
            yield v, floatformat(Orders.sum_from_commission(v.value), -8), v.pk
    def commission_records(self):
        for v in Valuta.objects.all():
            yield v, floatformat(self._commission_records(v.value), -8), v.pk

    def _user_balance_val(self, valuta):
        return self._user_balance(valuta)

    def _commission_records(self, valuta):
        return ProfileBalance.sum_from_commission(valuta=valuta)

    def orders_balance(self, valuta):
        return self._user_balance_val(valuta=valuta) - Orders.sum_from_user_buy_sale(user=self, valuta=valuta)

    def _update_pair(self, pair):
        if not pair == self.pair:
            self.pair = pair
            self.save()
    @property
    def amount_right(self):
        if self.pair:
            return self.orders_balance(self.pair.right.value)
        return _Zero
    @property
    def amount_left(self):
        if self.pair:
            return self.orders_balance(self.pair.left.value)
        return _Zero
    @property
    def balance_left(self):
        return mark_safe("<span>{amo}<span> {pos}".format(**{"amo":floatformat(self.amount_left, -8), "pos":self.pair.left}))
    @property
    def balance_right(self):
        return mark_safe("<span>{amo}</span> {pos}".format(**{"amo":floatformat(self.amount_right, -8), "pos":self.pair.right}))

class ProfileBalance(models.Model):
    created = models.DateTimeField(editable=False, auto_now_add=True, default=datetime.now)
    updated = models.DateTimeField(editable=False, auto_now=True, default=datetime.now)
    ACTIONS=(
        ('+', 'пополнение'),
        ('-', 'списание'),
    )
    value = models.DecimalField(u"количество", max_digits=14, decimal_places=8, validators=[MinValueValidator(_Zero)])
    valuta = models.ForeignKey("currency.Valuta", verbose_name=u"валюта")
    profile = models.ForeignKey("users.Profile", verbose_name=(u'Профиль'))
    action = models.CharField((u'действие'), choices=ACTIONS, max_length=1, validators=[RegexValidator(regex='^[+-]$', message=u'не допускаются значения кроме [+-]', code='invalid_action')])
    paymethod = models.ForeignKey("currency.PaymentMethod")
    bank = models.TextField((u'номер счета на ввод / вывод'), max_length=255, blank=True, null=True)
    accept = models.BooleanField(verbose_name=(u'Подтвердить'), default=False)
    confirm = models.BooleanField(verbose_name=(u'Подтверждено пользователем'), default=True)
    cancel = models.BooleanField(verbose_name=(u'Отменить'), default=False)
    commission = models.DecimalField(u"Комиссия %", max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(_Zero)], editable=False)
    min_commission = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Минимальная комиссия", validators=[MinValueValidator(_Zero)], editable=False)
    max_commission = models.DecimalField(max_digits=14, decimal_places=8, default=0.00, verbose_name=u"Максимальная комиссия", validators=[MinValueValidator(_Zero)], editable=False)

    def save(self, *args, **kwargs):
        if not self.action:
            self.action = self.paymethod.action
        if not self.min_commission:
            self.min_commission = self.paymethod.min_commission
        if not self.max_commission:
            self.max_commission = self.paymethod.max_commission
        if not self.commission:
            self.commission = self.paymethod.commission
        super(ProfileBalance, self).save(*args, **kwargs)
    def clean(self):
        if self.pk:
            old = ProfileBalance.objects.get(pk=self.pk)
            if (old.cancel and self.accept and not old.accept == self.accept) or \
                (old.cancel and not old.value == self.value) or \
                (old.cancel and not old.confirm == self.confirm):
                raise ValidationError(u'Изменения не сохранены. Так как эта заявка была отменена.')

    @property
    def _total_transaction(self):
        return self._total
    @property
    def w_total_transaction(self):
        return "%s%s %s" % (self.action, floatformat(self._total_transaction, -8), self.valuta)
    @property
    def w_transaction(self):
        if self.action == "+":
            value = self.value
        elif self.action== "-":
            value = normalized(self.value - self._commission_debit, where="DOWN")
        return "%s %s" % (floatformat(value, -8), self.valuta)
    @property
    def w_status(self):
        if self.cancel: return "отменен"
        if not self.confirm: return "в ожидании"
        if self.accept: return "выполнено"
        if not self.accept and not self.accept: return "в ожидании"
    @property
    def w_is_commission(self):
        return self.max_commission > _Zero or self.min_commission > _Zero or self.commission > _Zero
    @property
    def w_commission(self):
        if self.min_commission > _Zero and (self.value * self.commission / D(100)) < self.min_commission:
            return u"{commission} {valuta}".format(**{"commission":floatformat(self.min_commission, -8), "valuta": self.valuta})
        elif self.max_commission > _Zero and (self.value * self.commission / D(100)) > self.max_commission:
            return u"{commission} {valuta}".format(**{"commission":floatformat(self.max_commission, -8), "valuta": self.valuta})
        else:
            return u"{commission}%".format(**{"commission":self.commission,})
    @property
    def number_id(self):
        s = str(self.pk) + str(self.profile.pk) + 'b'
        return ctypes.c_size_t(hash(s)).value

    @classmethod
    def exists_input(cls, valuta, user, paymethod):
        cb = cls.objects.filter(accept=False, cancel=False, profile=user, action="+", valuta=valuta, confirm=False, paymethod=paymethod)
        if cb.exists():
            return cb[0]
        return None
    @classmethod
    def sum_commission(cls, flr={}, ex={}):
        return cls.objects.filter(**flr).filter(accept=True, cancel=False, confirm=True).distinct(
            ).extra(
                select={
                    'total':"""sum(
                    CASE
                        WHEN users_profilebalance.min_commission and (users_profilebalance.value * users_profilebalance.commission / 100) < users_profilebalance.min_commission THEN users_profilebalance.min_commission
                        WHEN users_profilebalance.max_commission > 0 and (users_profilebalance.value * users_profilebalance.commission / 100) > users_profilebalance.max_commission THEN users_profilebalance.max_commission
                        ELSE (users_profilebalance.value * users_profilebalance.commission / 100)
                    END
                    )""",
                },
            ).get(
            ).total or _Zero
    @classmethod
    def sum_from_commission(cls, valuta):
        return cls.objects.filter(
                accept=True, cancel=False, confirm=True, valuta__value=valuta
            ).distinct(
            ).extra(
                select={
                    'total':"""sum(
                    CASE
                        WHEN users_profilebalance.min_commission and (users_profilebalance.value * users_profilebalance.commission / 100) < users_profilebalance.min_commission THEN users_profilebalance.min_commission
                        WHEN users_profilebalance.max_commission > 0 and (users_profilebalance.value * users_profilebalance.commission / 100) > users_profilebalance.max_commission THEN users_profilebalance.max_commission
                        ELSE (users_profilebalance.value * users_profilebalance.commission / 100)
                    END
                    )""",
                },
            ).get(
            ).total or _Zero
    @property
    def _commission_debit(self):
        if self.min_commission > _Zero and (self.value * self.commission / D(100)) < self.min_commission:
            return self.min_commission
        elif self.max_commission > _Zero and (self.value * self.commission / D(100)) > self.max_commission:
            return self.max_commission
        else:
            return (self.value * self.commission / D(100))
    @property
    def _total(self):
        if self.action == "+":
            return normalized(self.value - self._commission_debit, where="DOWN")
        elif self.action == "-":
            return self.value
    def total_admin(self):
        v = normalized(self.value - self._commission_debit, where="DOWN")
        return floatformat(v, -8)
    total_admin.short_description = u'итого'
    @classmethod
    def exists_output(cls, valuta, user, paymethod):
        cb = cls.objects.filter(accept=False, cancel=False, profile=user, action="-", valuta=valuta, paymethod=paymethod)
        if cb.exists():
            return cb[0]
        return None
    def __unicode__(self):
        return u"{action}{amount}".format(**{"action": self.action, "amount": self.value})
    class Meta:
        verbose_name = u'перевод'
        verbose_name_plural = u'переводы средств'

class ProfileRole(models.Model):
    PROFILE_ROLE = (
        ('manager', (u'Менеджер')),
        ('customer', (u'клиент')),
    )

    profile = models.ForeignKey("users.Profile", verbose_name=(u'Профиль'))
    role = models.CharField((u'Роль'), choices=PROFILE_ROLE, max_length=15)

    class Meta:
        verbose_name = (u'Роль пользователя')
        verbose_name_plural = (u'Роли пользователя')
        unique_together = (('profile', 'role'),)

    def __unicode__(self):
        return self.role
