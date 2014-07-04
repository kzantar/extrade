from django.conf.urls import patterns, url

from users.views import ProfileView, ProfilePasswordView

urlpatterns = patterns('',
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
    url(r'^profile/password/$', ProfilePasswordView.as_view(), name='profile_password'),
)
