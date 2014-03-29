import ast
import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import User
from django.conf import settings
from localflavor.us.us_states import STATE_CHOICES
from website.models import Jurisdiction

class PythonDataField(models.TextField):
    __metaclass__ = models.SubfieldBase
    description = '''Stores an arbitrary python literal (string,
    number, tuple, list, dict, boolean, or None) in a text field.'''

    def to_python(self, value):
        if not value:
            value = []
        if isinstance(value, list):
            return value
        return ast.literal_eval(value)

from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^website\.models\.reporting\.PythonDataField"])

class GeographicArea(models.Model):
    name = models.TextField()
    description = models.TextField()
    states = PythonDataField()
    jurisdictions = models.ManyToManyField(Jurisdiction)
    class Meta:
        app_label = 'website'
    def get_absolute_url(self):
        return reverse('geoarea-view', kwargs={'pk': self.pk})
    def where(self):
        return where_clause_for_area(states = self.states,
                                     jurisdictions = self.jurisdictions.all())
    def matches(self):
        return Jurisdiction.objects.filter(self.where())

def where_clause_for_area(states=None, jurisdictions=None):
    if states:
        q = Q(state__in = states)
    else:
        q = Q(pk__in = jurisdictions) | \
            Q(parent__in = jurisdictions)
    return q & ~Q(jurisdiction_type = 'U',
                  pk__in = settings.SAMPLE_JURISDICTIONS)
