from django.conf.urls import patterns, url

from webgui.views import ExchangeView, ProfileOrderHistoryView, ProfileTransactionHistoryView
from currency.models import TypePair

urlpatterns = patterns('',
    url(r'^exchange/(?P<pair>\w+_\w+)/', ExchangeView.as_view(), name='exchange'),
    url(r'^(exchange/)?$', ExchangeView.as_view(), name='auction'),
    url(r'^profile/transactions/history/$', ProfileTransactionHistoryView.as_view(), name='history_transactions'),
    url(r'^profile/order/history/$', ProfileOrderHistoryView.as_view(), name='history_order'),
)
