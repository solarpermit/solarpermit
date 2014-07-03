import threading
import statsd
# we reuse django_statsd's get_connection so that we automatically use the same django settings
from django_statsd import utils
from django.conf import settings

local = threading.local()
scope = None
if not hasattr(local, 'solarpermit_statsd'):
    local.solarpermit = {}
scope = local.solarpermit
if 'statsd_connection' not in scope:
    scope['statsd_connection'] = utils.get_connection()

def get_counter(*names):
    name = ".".join([normalize(str(n)) for n in names])
    return statsd.Counter(name, scope['statsd_connection'])

def define_report(name, field_map):
    if name not in scope:
        c = [(normalize(field_name),
              (lambda field_name:
                 lambda question_id:
                   get_counter("question", name, question_id, field_name))(field_name))
              for (field_name, field_def) in field_map.iteritems()]
        scope[name] = c
    return scope[name]

def get_report(name):
    if name in scope:
        return scope[name]

# could do something more generic like url encoding, but this is good enough
import re
def normalize(name):
    return re.sub(r"[ +,{}*]", "_", name).lower()
