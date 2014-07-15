#-*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from users.models import ProfileBalance
from django.forms.widgets import HiddenInput, TextInput, Textarea, NumberInput
from django.core.mail import send_mail
from django.db.models import Q
from django.conf import settings
from decimal import Decimal as D, _Zero
from common.numeric import normalized




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

    username = forms.CharField(label=u"Имя пользователя")

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
    calc_value = forms.CharField(widget=forms.NumberInput(attrs={"id":"calc-value-result", "onkeyup": "Dajaxice.warrant.calc_inp(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val(), 'act': '+'});", "onchange": "Dajaxice.warrant.calc_inp(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val(), 'act': '+'});"}), label=u"вы получите", required=False)
    class Meta:
        model = ProfileBalance
        fields = ('value', 'valuta', 'calc_value')
        widgets = {
                'valuta': HiddenInput(attrs={"id": "balance-valuta"}),
                'value': NumberInput(attrs={"id": "balance-value", "onkeyup": "Dajaxice.warrant.calc_inp(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val()});", "onchange": "Dajaxice.warrant.calc_inp(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val()});"}),
            }
    def __init__(self, user=None, commission=_Zero, *args, **kwargs):
        super(AddBalanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.user = user
        if not commission > _Zero:
            del self.fields['calc_value']
    def save(self, *args, **kwargs):
        self.instance.profile = self.user
        self.instance.bank = self.instance.valuta.bank

        self.instance.value *= ( 1 - self.instance.valuta.commission_inp / D(100))
        self.instance.value = normalized(self.instance.value, where="DOWN")

        e1 = Profile.objects.filter(pk=self.user.pk).values_list('email', flat=True)
        e2 = Profile.objects.filter(is_active=True, is_staff=True).values_list('email', flat=True)
        subject = u"оформлена новая заявка на пополнение средств"
        message = u"оформлена новая заявка на пополнение средств"
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, e1)
            send_mail(subject, message, from_email, e2)
        except:
            pass
        return super(AddBalanceForm, self).save(*args, **kwargs)

class GetBalanceForm(forms.ModelForm):
    calc_value = forms.CharField(widget=forms.NumberInput(attrs={"id":"calc-value-result", "onkeyup": "Dajaxice.warrant.calc_out(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val(), 'act': '+'});", "onchange": "Dajaxice.warrant.calc_out(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val(), 'act': '+'});"}), label=u"вы получите", required=False)
    class Meta:
        model = ProfileBalance
        fields = ('bank', 'value', 'valuta', 'calc_value')
        widgets = {
                'valuta': HiddenInput(attrs={"id": "balance-valuta"}),
                'value': NumberInput(attrs={"id": "balance-value", "onkeyup": "Dajaxice.warrant.calc_out(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val()});", "onchange": "Dajaxice.warrant.calc_out(Dajax.process, {'value':$(this).val(), 'valuta':$('#balance-valuta').val()});"}),
            }
    def __init__(self, user=None, commission=_Zero, *args, **kwargs):
        super(GetBalanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.user = user
        self.fields['bank'].required = True
        if not commission > _Zero:
            del self.fields['calc_value']
    def save(self, *args, **kwargs):
        self.instance.profile = self.user
        self.instance.value *= ( 1 - self.instance.valuta.commission_out / D(100))
        self.instance.value = normalized(self.instance.value, where="DOWN")

        e1 = Profile.objects.filter(pk=self.user.pk).values_list('email', flat=True)
        e2 = Profile.objects.filter(is_active=True, is_staff=True).values_list('email', flat=True)
        subject = u"оформлена новая заявка на вывод средств"
        message = u"оформлена новая заявка на вывод средств"
        from_email = settings.DEFAULT_FROM_EMAIL
        try:
            send_mail(subject, message, from_email, e1)
            send_mail(subject, message, from_email, e2)
        except:
            pass
        return super(GetBalanceForm, self).save(*args, **kwargs)

class UserAdminForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = Profile

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
