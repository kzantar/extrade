from django.conf.urls import patterns, url

from webgui.views import ExchangeView, ProfileOrderHistoryView,\
                            ProfileTransactionHistoryView,\
                            ProfileTransactionView,\
                            ProfileFinancesView, \
                            CommissionRecordsView, \
                            CountersTotalView
from django.views.generic import TemplateView
from currency.models import TypePair

urlpatterns = patterns('',
    url(r'^exchange/(?P<pair>\w+_\w+)/$', ExchangeView.as_view(), name='exchange'),
    url(r'^(exchange/)?$', ExchangeView.as_view(), name='auction'),
    url(r'^profile/transactions/history/$', ProfileTransactionHistoryView.as_view(), name='history_transactions'),
    url(r'^profile/transactions/$', ProfileTransactionView.as_view(), name='transactions'),
    url(r'^profile/transactions/(?P<user_id>\d+)/$', ProfileTransactionView.as_view(), name='transactions'),
    url(r'^profile/order/history/$', ProfileOrderHistoryView.as_view(), name='history_order'),
    url(r'^profile/order/history/(?P<sort_by>active|executed|part_executed|cancel)/$', ProfileOrderHistoryView.as_view(), name='history_order'),
    url(r'^profile/finances/$', ProfileFinancesView.as_view(), name='finances'),
    url(r'^profile/commission_records/$', CommissionRecordsView.as_view(), name='commission_records'),
    url(r'^profile/counters_total/$', CountersTotalView.as_view(), name='counters_total'),
    url(r'^rules/$', TemplateView.as_view(template_name="rules.html"), name='rules'),
)
