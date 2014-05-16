from django.core.urlresolvers import reverse
from django_jinja import library
import urllib

lib = library.Library()

@lib.global_function
def url_params(url, **params):
    return '?'.join([url, urllib.urlencode(params)])
