#This file is for the dev site.  Can be used as example for other sites.
#To use this, rename to settings_local.py for your site.

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solarpermit',
        'HOST': '',
        'PORT': '3306',
        'USER': 'root',
        'PASSWORD': 'letmein',
    'OPTIONS' : { 'init_command': 'SET storage_engine=INNODB;', 'unix_socket' : '/opt/bitnami/mysql/tmp/mysql.sock',}
    },
             
    'natSolDB': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'natSolDB',
        'HOST': '198.61.201.124',
        'PORT': '3306',
        'USER': 'read',
        'PASSWORD': 'thisisreadonly',
    }

}


CSRF_COOKIE_DOMAIN = 'dev.solarpermit.org'
SITE_URL = "http://dev.solarpermit.org"
CACHE_PREFIX = 'solarpermitdev' #make this unique
#for Django 1.4 or above
#django.core.context_processors.auth is moved to django.contrib.auth.context_processors.auth
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    #'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth', #this is required for admin
    #'django.core.context_processors.csrf', #necessary for csrf protection
)

INTERNAL_IPS = ('127.0.0.1', '127.0.0.2')

ENABLE_GOOGLE_ANALYTICS = False

DEFAULT_FROM_EMAIL = 'no-reply@solarpermit.org'
EMAIL_HOST_USER = 'thatguyrenic@gmail.com'
EMAIL_HOST_PASSWORD = 'HJiYnqFC9H1Kc4OjS8KfLQ'
EMAIL_SUBJECT_PREFIX = ''
EMAIL_HOST='smtp.mandrillapp.com'
EMAIL_PORT='587'
EMAIL_USE_TLS=True

SOLARPERMIT_VERSION=''
FORUM_INTEGRATION = False