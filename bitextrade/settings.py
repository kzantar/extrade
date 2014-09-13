#-*- coding:utf-8 -*-
"""
Django settings for bitextrade project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

AUTH_USER_MODEL = 'users.Profile'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'mc7=8$!ep*g45qaj^ocm+@+b+8g1-f#!c5eqlg!wbj&(-!i*1h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
GEOIP_PATH = os.path.join(PROJECT_ROOT, 'geoip')

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []

SITE_ID=1

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'south',
    'registration',
    'secureauth',
    'widget_tweaks',
    'change_email',
    'chunks',
    'dajaxice',
    'dajax',

    'webgui',  # ордера
    'warrant',  # ордера
    'currency', # валюта
    'users',  # пользователи
    'news',  # новости
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'dajaxice.finders.DajaxiceFinder',
)


ROOT_URLCONF = 'bitextrade.urls'

WSGI_APPLICATION = 'bitextrade.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "bitextrade",                      # Or path to database file if using sqlite3.
        'USER': 'bitextrade',                      # Not used with sqlite3.
        'PASSWORD': 'GhotEgfi',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': { 'init_command': 'SET storage_engine=INNODB;' }
    },
    'innodb': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "bitextrade",                      # Or path to database file if using sqlite3.
        'USER': 'bitextrade',                      # Not used with sqlite3.
        'PASSWORD': 'GhotEgfi',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        'OPTIONS': { 'init_command': 'SET storage_engine=INNODB;' }
    }
}

USE_CACHE = not DEBUG
#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#   }
#}


TIMEOUT = 3600
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': os.path.join(BASE_DIR, "cache/"),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, "static"),
)

STATIC_ROOT = os.path.join(PROJECT_ROOT, "collected_static")

#MEDIA_ROOT = os.path.join(BASE_DIR, "media")
#MEDIA_URL = '/f/'

EMAIL_HOST = 'mx.artela.net'
EMAIL_PORT = 587
EMAIL_HOST_PASSWORD = 'KfeJG75G49'
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'noreply@bitextrade.com'
SERVER_EMAIL = DEFAULT_FROM_EMAIL = EMAIL_CHANGE_FROM_EMAIL = 'noreply@bitextrade.com'


ACCOUNT_ACTIVATION_DAYS=1

try:
    from settings_local import *
except ImportError:
    pass
DEBUG_T=False

if DEBUG_T:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]
    DEBUG_TOOLBAR_CONFIG = {
        'JQUERY_URL':'',
        'EXCLUDE_URLS': ('/admin',), # не работает, но в разработке есть...
    }
