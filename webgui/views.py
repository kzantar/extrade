#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from django.shortcuts import get_object_or_404
from common.mixin import LoginRequiredMixin
from django.db.models import Sum, Count, F, Q


from currency.models import TypePair
from warrant.models import Orders, Buy, Sale
from news.models import News
from warrant.forms import OrdersForm

from django.contrib.auth import login, get_user_model

Profile = get_user_model()


class ExchangeView(DetailView):
    template_name = 'exchange.html'
    model = TypePair
    slug_field = 'slug'
    slug_url_kwarg = 'pair'
    def get_object(self, queryset=None):
        qs = queryset or self.get_queryset()
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
        ctx['news'] = News.getlast()
        ctx['min_max_avg'] = min_max_avg = self.object.min_max_avg(to_round=8)
        ctx['buy_form'] = OrdersForm(prefix="buy", initial={"pair":self.object, "rate": min_max_avg[0]})
        ctx['sale_form'] = OrdersForm(prefix="sale", initial={"pair":self.object, "rate": min_max_avg[1]})
        user = self.request.user
        if user.is_authenticated() and user.is_active:
            user._update_pair(self.object)
            ctx['order_actives'] = self.object.actives(user)
        return ctx


class ProfileOrderHistoryView(LoginRequiredMixin, ListView):
    template_name = "order_history.html"
    model = Orders
    paginate_by = 5
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(user=self.request.user)
        return super(ProfileOrderHistoryView, self).get_queryset()

class ProfileTransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = "transactions_history.html"
    model = Orders
    paginate_by = 5
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(user=self.request.user).filter(completed=True)
        return super(ProfileTransactionHistoryView, self).get_queryset()

class ProfileFinancesView(LoginRequiredMixin, ListView):
    template_name = "balance_list.html"
    def get_queryset(self):
        return self.request.user.finances()