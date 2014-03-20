import datetime
from django.core.urlresolvers import reverse
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from localflavor.us.us_states import STATE_CHOICES
from website.models import Jurisdiction

class GeographicArea(models.Model):
    name = models.TextField()
    description = models.TextField()
    jurisdictions = models.ManyToManyField(Jurisdiction)
    class Meta:
        app_label = 'website'
    def get_absolute_url(self):
        return reverse('geoarea-view', kwargs={'pk': self.pk})
