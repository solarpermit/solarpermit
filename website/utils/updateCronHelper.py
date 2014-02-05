from django.conf import settings
from django.utils import simplejson as json
from datetime import datetime, timedelta, date
import datetime as ad
from django.db.models import *
#import time

from server.website.models import EntityView, EntityViewCount

class UpdateCron():
    strMsg = ''
    objDateTimeNow = None
    
    def __init__(self):
        self.strMsg += '---------- Update Start ----------<br />'
        self.update_30days_top10()
        self.strMsg += '<br />---------- Update End ----------<br /><br />'
        
    def update_30days_top10(self):
        self.objDateTimeNow = date.today()
        obj30daysbefore = self.objDateTimeNow - timedelta(days=31)
        evs = EntityView.objects.filter(latest_datetime__gt = obj30daysbefore).values('entity_name', 'entity_id').annotate(record_sum = Count('entity_name'))
        self.strMsg += str(evs)
        for ev in evs:
            entity_name = ev['entity_name']
            entity_id = ev['entity_id']
            record_sum = ev['record_sum']
            evc = EntityViewCount.objects.filter(entity_name = entity_name, entity_id = entity_id)
            if len(evc) > 0:
                evc = evc[0]
            else:
                evc = EntityViewCount()
            evc.entity_name = entity_name
            evc.entity_id = entity_id
            evc.count_30_days = record_sum
            evc.save()
        #print str(evs)
        return