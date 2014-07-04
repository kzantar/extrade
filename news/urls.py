from django.conf.urls import patterns, url

from news.views import NewsDetailView, NewsListView

urlpatterns = patterns('',
    url(r'^(?P<pk>\d+)/detail/$', NewsDetailView.as_view(), name='news_detail'),
    url(r'^list/$', NewsListView.as_view(), name='news_list'),
)
