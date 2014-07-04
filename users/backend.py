# -*- encoding: utf-8 -*-

from django.contrib.auth import authenticate
from django.contrib.auth import login, get_user_model
from django.conf import settings
from django.contrib.gis.geoip import GeoIP
from registration.backends import simple
from registration import signals

from common.helpers import get_client_ip

Profile = get_user_model()


class Backend(simple.SimpleBackend):

    def register(self, request, **kwargs):
        g = GeoIP()
        geo_data = g.country(get_client_ip(request))
        username, email, password = kwargs['username'], kwargs['email'], kwargs['password1']
        user = Profile.objects.create_user(username, email, password)
        user.country = geo_data['country_code'] or 'RU'
        user.save()

        new_user = authenticate(email=email, password=password)
        login(request, new_user)
        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user

    def post_registration_redirect(self, request, user):
        return (request.GET.get('next') or settings.LOGIN_REDIRECT_URL, (), {})


def get_user(email, queryset=None):
    """
    Return the user with given email address.
    Note that email address matches are case-insensitive.
    """
    if queryset is None:
        queryset = Profile.objects
    return queryset.get(email=email)


class EmailAuthBackend(object):

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, email=None, password=None, username=None):
        try:
            if not email and username:
                email = username
            user = get_user(email)
            if user.check_password(password):
                return user
        except Profile.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return None
