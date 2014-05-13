#This file is for the dev site.  Can be used as example for other sites.
#To use this, rename to settings_local.py for your site.

DEBUG = True
INTERNAL_IPS = ('127.0.0.1', '23.253.204.16','10.210.32.248')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solarpermit',
        'HOST': 'localhost',
        'PORT': '3306',
        'USER': 'solarpermit_user',
        'PASSWORD': 'asdf238yr9n9237vnaa56av3',
    'OPTIONS' : { 'init_command': 'SET storage_engine=INNODB;',}
    }
}

#for Django 1.4 or above
#django.core.context_processors.auth is moved to django.contrib.auth.context_processors.auth
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    #'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth', #this is required for admin
    #'django.core.context_processors.csrf', #necessary for csrf protection
)

CSRF_COOKIE_DOMAIN = 'staging.solarpermit.org'
SITE_URL = "http://staging.solarpermit.org"

SERVER_EMAIL = 'thatguyrenic@gmail.com'
DEFAULT_FROM_EMAIL = 'no-reply@solarpermit.org'
EMAIL_HOST_USER = 'thatguyrenic@gmail.com'
EMAIL_HOST_PASSWORD = "HJiYnqFC9H1Kc4OjS8KfLQ"
EMAIL_SUBJECT_PREFIX = ''
EMAIL_HOST='smtp.mandrillapp.com'
EMAIL_PORT='587' #EMAIL_PORT='465'
EMAIL_USE_TLS=True
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ENABLE_GOOGLE_ANALYTICS = True
FEEDBACK_EMAIL = 'feedback@solarpermit.org'
MAINTENANCE_MODE = False

SAMPLE_JURISDICTIONS=['1', '101105']

#COMPRESS_ENABLED = False
