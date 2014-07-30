from django.core.urlresolvers import reverse
from django_jinja import filter
import urllib

@global_function
def url_params(url, **params):
    return '?'.join([url, urllib.urlencode(params)])
