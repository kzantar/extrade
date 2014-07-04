#-*- coding:utf-8 -*-
from django.conf.urls import patterns, include, url
from django.conf import settings

from users.forms import UserRegistrationForm, EmailAuthenticationForm

from django.conf.urls.static import static
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'bitextrade.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'', include('webgui.urls')),
    url(r'', include('warrant.urls')),
    url(r'', include('currency.urls')),
    url(r'', include('users.urls')),
    url(r'^news/', include('news.urls')),
    url(r'^accounts/login/$', 'secureauth.views.login', {'authentication_form': EmailAuthenticationForm}, name='login'),
    url(r'^security/', include('secureauth.urls')),
    url(r'^accounts/register/$', 'registration.views.register', {'backend': 'users.backend.Backend', 'form_class': UserRegistrationForm}, name='registration_register'),
    #url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^accounts/', include('bitextrade.registration_urls')),
    url(r'', include('bitextrade.change_email_urls')),

) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
