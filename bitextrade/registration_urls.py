from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views


urlpatterns = patterns('',

      url(r'', include('registration.backends.default.urls')),
      #override the default urls
      url(r'^password/change/$',
                    auth_views.password_change,
                    name='password_change'),
      url(r'^password/change/done/$',
                    auth_views.password_change_done,
                    name='password_change_done'),
      url(r'^password/reset/$',
                    auth_views.password_reset,
                    name='password_reset'),
      url(r'^reg/password/reset/complete/$',
                    auth_views.password_reset_complete,
                    {'template_name': "password_reset_complete.html"},
                    name='password_reset_complete'),
      url(r'^reg/password/reset/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$',
                    auth_views.password_reset_confirm,
                    {'template_name': "password_reset_confirm.html"},
                    name='password_reset_confirm'),

      url(r'^reg/password/reset/done/$',
                    "django.contrib.auth.views.password_reset_done",
                    {'template_name': "password_reset_done.html"},
                    name='password_reset_done'),
      url(r'^reg/password/reset/$',
                    "django.contrib.auth.views.password_reset",
                    {'template_name': "password_reset_form.html"},
                    name='auth_password_reset'),

      #and now add the registration urls
)
