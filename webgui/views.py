#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from django.shortcuts import get_object_or_404
from common.mixin import LoginRequiredMixin

from currency.models import TypePair
from warrant.models import Orders, Buy, Sale

from django.contrib.auth import login, get_user_model

Profile = get_user_model()


class ExchangeView(DetailView):
    template_name = 'exchange.html'
    model = TypePair
    slug_field = 'slug'
    slug_url_kwarg = 'pair'
    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
        #self.request.session['pair'] = self.object.slug
        #self.request.session.save()
        return super(ExchangeView, self).get_object(queryset=qs)
    def get(self, request, *args, **kwargs):
        _pair = self.request.session.get('pair', None)
        if not self.kwargs.get('pair'): self.kwargs['pair'] = _pair or TypePair.default()
        self.request.session['pair'] = self.kwargs.get('pair')
        self.request.session.save()
        return super(ExchangeView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super(ExchangeView, self).get_context_data(**kwargs)
        ctx['pair_list'] = TypePair.flr()
        ctx['order_buy'] = self.object.buy()
        ctx['order_sale'] = self.object.sale()
        ctx['order_history'] = self.object.history()

        if self.request.user.is_authenticated():
            user = Profile.objects.get(pk=self.request.user.pk)
            ctx['order_actives'] = self.object.actives(user)
        return ctx


class ProfileOrderHistoryView(LoginRequiredMixin, ListView):
    template_name = "order_history.html"
    model = Orders
    paginate_by = 41
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(user=self.request.user)
        print self.queryset
        return super(ProfileOrderHistoryView, self).get_queryset()

class ProfileTransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = "transactions_history.html"
    model = Orders
    paginate_by = 41
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(user=self.request.user)
        return super(ProfileTransactionHistoryView, self).get_queryset()
