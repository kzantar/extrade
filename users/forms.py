#-*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from users.models import ProfileBalance, ProfilePayNumber
from currency.models import Valuta, PaymentMethod
from django.forms.widgets import HiddenInput, TextInput, Textarea, NumberInput, Select
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from decimal import Decimal as D, _Zero
from common.numeric import normalized
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from users.models import AddressBook




Profile = get_user_model()


class Email(forms.EmailField):

    def clean(self, value):
        super(Email, self).clean(value)
        try:
            Profile.objects.get(email=value)
            raise forms.ValidationError((u'Этот e-mail адрес уже занят.'))
        except Profile.DoesNotExist:
            return value


class UserRegistrationForm(forms.Form):

    username = forms.CharField(label=u"Имя пользователя", max_length=20)

    email = Email()
    password1 = forms.CharField(
        widget=forms.PasswordInput(), label=(u'Пароль'))
    password2 = forms.CharField(
        widget=forms.PasswordInput(), label=(u'Пароль (ещё раз)'))

    def clean_username(self):
        if Profile.objects.filter(username=self.cleaned_data['username']).exists():
            raise forms.ValidationError((u'Это имя пользователя уже занято.'))
        return self.cleaned_data['username']
    def clean_password(self):
        if self.cleaned_data['password1'] != self.cleaned_data['password2']:
            raise forms.ValidationError((u'Пароли не совпадают'))
        return self.cleaned_data['password1']


class EmailAuthenticationForm(AuthenticationForm):
    """
    Override the default AuthenticationForm to force email-as-username behavior.
    """
    message_incorrect_password = (
        u'Пожалуйста введите корректный логин и пароль.')
    message_inactive = (u'Этот аккаунт не активирован.')

    def __init__(self, request=None, *args, **kwargs):
        super(EmailAuthenticationForm, self).__init__(request, *args, **kwargs)
        del self.fields['username']
        self.fields['email'] = forms.EmailField(
            label=('E-mail'), max_length=75)
        self.fields.insert(0, 'email', self.fields.pop('email'))

    def clean(self):
        username = self.cleaned_data.get('username')
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(email=email, password=password)
            if self.user_cache is None:
                raise forms.ValidationError(self.message_incorrect_password)
            if not self.user_cache.is_active:
                raise forms.ValidationError(self.message_inactive)
        self.check_for_test_cookie()
        return self.cleaned_data



class ProfileForm(forms.ModelForm):

    def __init__(self, request=None, *args, **kwargs):
        super(ProfileForm, self).__init__(request, *args, **kwargs)
        #self.fields['email'].widget.attrs['readonly'] = True

    class Meta:
        model = Profile
        exclude = (
            'password', 'last_login', 'is_superuser', 'groups',
            'user_permissions', 'date_joined', 'is_active',
            'is_staff', 'admin_comment', 'balance')
        widgets = {
            'tel': forms.TextInput(attrs={
                'placeholder': (u'Формат: +12345678910')
            }),
        }

class AddBalanceForm(forms.ModelForm):
    calc_value = forms.CharField(widget=forms.NumberInput(attrs={"step":"1e-8", "id":"calc-value-result", "onkeyup": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val(), 'act': '+'});", "onchange": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val(), 'act': '+'});"}), label=u"Вы получите", required=False)
    class Meta:
        model = ProfileBalance
        fields = ('user_bank', 'value', 'valuta', 'calc_value', 'paymethod')
        labels = {
                "value": u"Сумма к оплате",
            }
        widgets = {
                'paymethod': HiddenInput(attrs={"id": "balance-paymethod"}),
                'valuta': HiddenInput(attrs={"id": "balance-valuta"}),
                'value': NumberInput(attrs={"id": "balance-value", "onkeyup": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val()});", "onchange": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val()});"}),
            }
    def __init__(self, user=None, validators=None, commission=False, *args, **kwargs):
        super(AddBalanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        initial = getattr(self, 'initial', None)
        self.user = user
        if validators: self.fields['value'].validators = validators
        if initial and initial.get('paymethod'): self.fields['value'].validators = initial.get('paymethod').validators
        if (initial and initial.get('paymethod') and not initial.get('paymethod').enable_user_bank) or not (initial and initial.get('paymethod')):
            del self.fields['user_bank']
        else:
            self.fields['user_bank'].required = True
        if initial and initial.get('paymethod'):
            self.fields['paymethod'].queryset = initial.get('paymethod').valuta.paymethods_inp
        else:
            self.fields['paymethod'].queryset = PaymentMethod.objects.none()
        self.fields['paymethod'].empty_label=None
        if not commission:
            del self.fields['calc_value']
    def save(self, *args, **kwargs):
        self.instance.profile = self.user
        if self.instance.paymethod.enable_account_number:
            pay_number = ProfilePayNumber.get_or_accept(self.user, self.instance.paymethod)
            self.instance.bank = pay_number.get_merged_text('bank')
        else:
            self.instance.bank = self.instance.paymethod.bank

        e1 = Profile.objects.filter(pk=self.user.pk).values_list('email', flat=True)
        e2 = Profile.objects.filter(is_active=True, is_staff=True).values_list('email', flat=True)
        subject = u"оформлена новая заявка на пополнение средств"
        message = u"оформлена новая заявка на пополнение средств"
        AddressBook.send_action(subject, message)
        return super(AddBalanceForm, self).save(*args, **kwargs)

class GetBalanceForm(forms.ModelForm):
    calc_value = forms.CharField(widget=forms.NumberInput(attrs={"step":"1e-8", "id":"calc-value-result", "onkeyup": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val(), 'act': '+'});", "onchange": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val(), 'act': '+'});"}), label=u"Вы получите", required=False)
    class Meta:
        model = ProfileBalance
        labels = {
            'user_bank': u"Реквизиты",
            'value': u"Сумма на вывод",
        }
        fields = ('user_bank', 'value', 'valuta', 'calc_value', 'paymethod')
        widgets = {
                'paymethod': HiddenInput(attrs={"id": "balance-paymethod"}),
                'valuta': HiddenInput(attrs={"id": "balance-valuta"}),
                'value': NumberInput(attrs={"id": "balance-value", "onkeyup": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val()});", "onchange": "Dajaxice.warrant.calc_paymethod(Dajax.process, {'value':$(this).val(), 'paymethod':$('#balance-paymethod').val()});"}),
            }
    def __init__(self, user=None, validators=None, commission=False, *args, **kwargs):
        super(GetBalanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        initial = getattr(self, 'initial', None)
        self.user = user
        self.fields['user_bank'].required = True
        if validators: self.fields['value'].validators = validators
        if initial and initial.get('paymethod'): self.fields['value'].validators = initial.get('paymethod').validators
        if (initial and initial.get('paymethod') and not initial.get('paymethod').enable_user_bank) or not (initial and initial.get('paymethod')):
            del self.fields['user_bank']
        else:
            self.fields['user_bank'].required = True
        if initial and initial.get('paymethod'):
            self.fields['paymethod'].queryset = initial.get('paymethod').valuta.paymethods_out
        else:
            self.fields['paymethod'].queryset = PaymentMethod.objects.none()
        self.fields['paymethod'].empty_label=None
        if not commission:
            del self.fields['calc_value']
    def is_valid(self):
        valid = super(GetBalanceForm, self).is_valid()
        init_val = self.initial.get('value', _Zero)
        if not valid:
            return valid
        value = self.cleaned_data['value']
        valuta = self.cleaned_data['valuta']
        balance = self.user.orders_balance(valuta.value)
        _sum = (balance + init_val) - value
        if not _sum >= _Zero:
            self._errors['value'] = (u'Недостаточно средств на счете',)
            return False
        return True
    def save(self, *args, **kwargs):
        self.instance.profile = self.user

        e1 = Profile.objects.filter(pk=self.user.pk).values_list('email', flat=True)
        e2 = Profile.objects.filter(is_active=True, is_staff=True).values_list('email', flat=True)
        subject = u"оформлена новая заявка на вывод средств"
        message = u"оформлена новая заявка на вывод средств"
        AddressBook.send_action(subject, message)
        return super(GetBalanceForm, self).save(*args, **kwargs)

class UserAdminForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = Profile

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True

