from django.conf.urls import patterns, url

from webgui.views import ExchangeView, ProfileOrderHistoryView, ProfileTransactionHistoryView, ProfileFinancesView
from django.views.generic import TemplateView
from currency.models import TypePair

urlpatterns = patterns('',
    url(r'^exchange/(?P<pair>\w+_\w+)/$', ExchangeView.as_view(), name='exchange'),
    url(r'^(exchange/)?$', ExchangeView.as_view(), name='auction'),
    url(r'^profile/transactions/history/$', ProfileTransactionHistoryView.as_view(), name='history_transactions'),
    url(r'^profile/order/history/$', ProfileOrderHistoryView.as_view(), name='history_order'),
    url(r'^profile/finances/$', ProfileFinancesView.as_view(), name='finances'),
    url(r'^rules/$', TemplateView.as_view(template_name="rules.html"), name='rules'),
)
