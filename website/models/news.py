import datetime
from django.db import models
from django.conf import settings
from website.models import Jurisdiction

class News(models.Model):
    published = models.DateField(db_index=True)
    url = models.TextField()
    title = models.TextField()
    class Meta:
        abstract = True
        app_label = 'website'

class PressRelease(News):
    42

class Article(News):
    publisher = models.TextField()

class Event(News):
    start = models.DateTimeField()
    end = models.DateTimeField()
    expiration = models.DateField(db_index=True)
    location = models.ForeignKey(Jurisdiction)
