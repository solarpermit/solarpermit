from django_jinja import filter
from django.utils.safestring import mark_safe
import jinja2
import simplejson

@filter
def json(value):
    return mark_safe(simplejson.dumps(value))
