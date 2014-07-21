import datetime
from django.utils.timezone import utc
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
import uuid

class API_Keys(models.Model):
    user = models.ForeignKey(User)
    key = models.TextField()
    enabled = models.BooleanField(default = True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    revoke_datetime = models.DateTimeField(blank=True, null=True)
    class Meta:
        app_label = "website"

    def createNew(self, user):
        self.user = user
        new_key = uuid.uuid4().hex
        self.key = new_key
        return self

    def revoke(self):
        self.enabled = False 
        self.revoke_datetime = datetime.datetime.utcnow().replace(tzinfo=utc)
        return self
