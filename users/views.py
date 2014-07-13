#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, RedirectView, View, ListView
from common.mixin import LoginRequiredMixin
from django.views.generic.edit import FormMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.contrib import messages


from django.contrib.auth import get_user_model
from users.models import ProfileBalance

from users.forms import ProfileForm, AddBalanceForm

# Create your views here.
Profile = get_user_model()

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'
    success_url = reverse_lazy('profile')

    def __init__(self, *args, **kwargs):
        super(ProfileView, self).__init__(*args, **kwargs)
        self.redirect = None

    def _set_form(self, model, key, ctx, form):
        ctx[key] = form(
            self.request.POST if key in self.request.POST else None,
            prefix=key, instance=self.request.user)

    def _save_form(self, key, model, ctx):
        if ctx[key].is_valid():
            model.objects.filter(profile=self.request.user).delete()
            for form in ctx[key].forms:
                form_data = form.cleaned_data
                save = form_data.get('data', False) \
                    or form_data.get('event_type', False)
                if save and form not in ctx[key].deleted_forms:
                    item = form.save()

            self.redirect = True

    def get_context_data(self, **kwargs):
        ctx = super(ProfileView, self).get_context_data(**kwargs)
        
        ctx['profile_form'] = ProfileForm(
            self.request.POST or None, prefix='profile_form',
            instance=self.request.user)

        return ctx

    def post(self, request, *args, **kwargs):
        ctx = self.get_context_data(**kwargs)
        self.redirect = False

        if ctx['profile_form'].is_valid():
            profile = ctx['profile_form'].save()
            return HttpResponseRedirect(self.success_url)

        self._save_form('profile_contacts', ProfileContacts, ctx)
        self._save_form('profile_payment', ProfilePaymentMethod, ctx)
        self._save_form('profile_notifications', ProfileNotification, ctx)

        if self.redirect is True:
            return HttpResponseRedirect(self.success_url)

        return self.render_to_response(ctx)


class ProfilePasswordView(LoginRequiredMixin, RedirectView):

    def get_redirect_url(self, **kwargs):
        old_password = self.request.POST.get('old_password', False)
        new_password1 = self.request.POST.get('new_password1', False)
        new_password2 = self.request.POST.get('new_password2', False)

        if not old_password or not new_password1 or not new_password2:
            messages.success(
                self.request,
                (u'Для смены пароля необходимо указать все данные'))

        elif not new_password1 == new_password2:
            messages.success(
                self.request,
                (u'Новый пароль не совпадает. Пожалуйста попробуйте ещё раз'))

        elif not self.request.user.check_password(old_password):
            messages.success(
                self.request,
                (u'Неверный текущий пароль. Пожалуйста попробуйте ещё раз'))
        else:
            user = Profile.objects.get(pk=self.request.user.pk)
            user.set_password(new_password2)
            user.save()
            messages.success(
                self.request,
                (u'Пароль успешно изменён. Теперь вы можете войти в '
                  u'систему используя новый пароль'))

        return reverse_lazy('change_email_create')
