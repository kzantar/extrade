from django.conf.urls import patterns, url

from warrant.views import BuyDetailView, SaleDetailView

urlpatterns = patterns('',
    url(r'^exchange/(?P<pair>\w+_\w+)/buy/$', BuyDetailView.as_view(), name='buy'),
    url(r'^exchange/(?P<pair>\w+_\w+)/sale/$', SaleDetailView.as_view(), name='sale'),
)
