#This file is for the dev site.  Can be used as example for other sites.
#To use this, rename to settings_local.py for your site.

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'solarpermit',
        'HOST': '',
        'PORT': '3306',
        'USER': '',
        'PASSWORD': '',
    'OPTIONS' : { 'init_command': 'SET storage_engine=INNODB;', 'unix_socket' : '/opt/bitnami/mysql/tmp/mysql.sock',}
    },
             
#    'natSolDB': {
#        'ENGINE': 'django.db.backends.mysql',
#        'NAME': 'natSolDB',
#        'HOST': 'localhost',
#        'PORT': '3306',
#        'USER': 'read',
#        'PASSWORD': '',
#    }

}

CSRF_COOKIE_DOMAIN = ''
SITE_URL = "http://127.0.0.1:9001"
CACHE_PREFIX = 'solarpermitdev' #make this unique
#for Django 1.4 or above
#django.core.context_processors.auth is moved to django.contrib.auth.context_processors.auth
TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.request',
    #'django.core.context_processors.i18n',
    'django.contrib.auth.context_processors.auth', #this is required for admin
    #'django.core.context_processors.csrf', #necessary for csrf protection
)

#SITE_URL = "http://dev.solarpermit.org"

INTERNAL_IPS = ('127.0.0.1', '127.0.0.2')

ADMIN_EMAIL_ADDRESS = 'info@solarpermit.org'

ENABLE_GOOGLE_ANALYTICS = False

DEFAULT_FROM_EMAIL = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = ''
EMAIL_HOST=''
EMAIL_PORT=''

