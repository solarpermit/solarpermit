import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.contrib.localflavor.us.models import PhoneNumberField

class Address(models.Model):
    address1 = models.CharField(max_length=255, blank=True, null=True)
    address2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=8, blank=True, null=True)
    zip_code = models.CharField(max_length=32, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.address1+', '+self.address2+', '+self.city+', '+self.state+' '+self.zip_code
    class Meta:
        app_label = 'website'
