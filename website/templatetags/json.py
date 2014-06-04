from django_jinja import library
from django.utils.safestring import mark_safe
import jinja2
import simplejson

lib = library.Library()

@lib.filter
def json(value):
    return mark_safe(simplejson.dumps(value))
