#-*- coding:utf-8 -*-
from django import forms
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm



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
        self.fields['email'].widget.attrs['readonly'] = True

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

class UserAdminForm(UserChangeForm):

    class Meta(UserChangeForm.Meta):
        model = Profile

    def __init__(self, *args, **kwargs):
        super(UserAdminForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = True
