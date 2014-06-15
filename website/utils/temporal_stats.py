import threading
import statsd
from django_statsd import utils
from django.conf import settings

local = threading.local()
scope = None
if not hasattr(local, 'solarpermit_statsd'):
    local.solarpermit = {}
scope = local.solarpermit
if 'statsd_connection' not in scope:
    # reuse django_statsd's get_connection so that we automatically use the same django settings
    scope['connection'] = utils.get_connection()

def get_gauge(name):
    return statsd.Gauge(name, scope['statsd_connection'])

def suggestions():
    if 'suggestions' not in scope:
        scope['suggestions'] = get_gauge("question.suggested")
    return scope['suggestions']

def answers():
    if 'answers' not in scope:
        scope['answers'] = get_gauge("question.answered")
    return scope['answers']
