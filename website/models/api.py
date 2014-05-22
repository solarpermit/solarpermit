from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

class API_Keys(models.Model):
    user = models.ForeignKey(User)
    key = models.TextField()
    class Meta:
        app_label = "website"
