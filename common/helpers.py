# -*- encoding: utf-8 -*-

import os
import urllib


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    # Заглушка для локалки ip Google
    if ip in ('127.0.0.1', 'localhost'):
        ip = '74.125.77.147'
    return ip

