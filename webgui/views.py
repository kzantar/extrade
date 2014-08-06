#-*- coding:utf-8 -*-
from django.shortcuts import render
from django.views.generic.edit import FormMixin
from django.views.generic import ListView, DetailView, RedirectView, TemplateView
from django.shortcuts import get_object_or_404
from common.mixin import LoginRequiredMixin, StaffRequiredMixin
from django.db.models import Sum, Count, F, Q


from currency.models import TypePair
from warrant.models import Orders, Buy, Sale
from news.models import News
from warrant.forms import OrdersForm
from users.models import ProfileBalance
from users.forms import AddBalanceForm

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseRedirect, Http404

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
    paginate_by = 41
    def get_queryset(self):
        sort_by = self.kwargs.get('sort_by')
        q = self.model._default_manager.filter(user=self.request.user).order_by('-created')
        if sort_by == 'active': q = q.exclude(Q(cancel=True) | Q(completed=True)).distinct()
        if sort_by == 'executed': q = q.filter(completed=True)
        if sort_by == 'part_executed': q = q.filter(cancel=True).exclude(completed=True).filter(Q(sale__sale_sale__gte=1) | Q(buy__buy_buy__gte=1)).distinct()
        if sort_by == 'cancel': q = q.filter(cancel=True)
        self.queryset = q
        return super(ProfileOrderHistoryView, self).get_queryset()

class ProfileTransactionView(LoginRequiredMixin, ListView):
    template_name = "transactions.html"
    paginate_by = 41
    model = ProfileBalance
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(
            profile = self.request.user
        ).filter(
            
        ).filter(
        ).order_by()
        return super(ProfileTransactionView, self).get_queryset()
class ProfileTransactionHistoryView(LoginRequiredMixin, ListView):
    template_name = "transactions_history.html"
    model = Orders
    paginate_by = 41
    def get_queryset(self):
        self.queryset = self.model._default_manager.filter(
                Q(
                    user=self.request.user,
                ) | Q(
                    sale__buy__user=self.request.user,
                ) | Q(
                    buy__sale__user=self.request.user,
                ), Q(
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
            ).order_by('-updated')
        return super(ProfileTransactionHistoryView, self).get_queryset()

class ProfileFinancesView(LoginRequiredMixin, ListView):
    template_name = "balance_list.html"
    def get_queryset(self):
        return self.request.user.finances()

class CommissionRecordsView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    template_name = "commission_records.html"
    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.request.user.commission_records_orders()
        raise Http404
