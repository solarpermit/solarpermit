from django.conf import settings
from datetime import *
from django.utils.timezone import localtime
import pytz

class DatetimeHelper:
    default_timezone = settings.TIME_ZONE
    time_zone = ''
    state = ''
    time_formate = '%b %d, %Y, %I:%M %p %Z'
    date_formate = '%b %d, %Y'
    dt = None
    states_timezone ={
                     'WA': 'US/Pacific', 'OR': 'US/Pacific', 'CA': 'US/Pacific', 'NV': 'US/Pacific',
                     'MT': 'US/Mountain', 'ID': 'US/Mountain', 'WY': 'US/Mountain', 'UT': 'US/Mountain', 'CO': 'US/Mountain', 'AZ': 'US/Mountain', 'NM': 'US/Mountain',
                     'ND': 'US/Central', 'SD': 'US/Central', 'NE': 'US/Central', 'KS': 'US/Central', 'OK': 'US/Central', 'TX':'US/Central',
                     'MN': 'US/Central', 'IA': 'US/Central', 'MO': 'US/Central', 'AR': 'US/Central', 'LA': 'US/Central',
                     'WI': 'US/Central', 'IL': 'US/Central', 'KY': 'US/Central', 'TN': 'US/Central', 'MS': 'US/Central', 'AL': 'US/Central',
                     'MI': 'US/Eastern', 'IN': 'US/Eastern', 'OH': 'US/Eastern', 'WV': 'US/Eastern', 'GA': 'US/Eastern', 'FL': 'US/Eastern',
                     'NY': 'US/Eastern', 'PA': 'US/Eastern', 'VA': 'US/Eastern', 'NC': 'US/Eastern', 'SC': 'US/Eastern',
                     'ME': 'US/Eastern', 'VT': 'US/Eastern', 'NH': 'US/Eastern', 'MA': 'US/Eastern', 'RI': 'US/Eastern', 'CT': 'US/Eastern',
                     'NJ': 'US/Eastern', 'DE': 'US/Eastern', 'MD': 'US/Eastern', 'DC': 'US/Eastern', 'HI': 'US/Hawaii', 'AK': 'US/Alaska'
                     }
    
    def __init__(self, dt, time_zone = ''):
        self.time_zone = time_zone
        self.dt = dt
    
    def get_timezone(self):
        if self.time_zone != '':
            timezone = pytz.timezone(self.time_zone)
        else:
            timezone = pytz.timezone(self.default_timezone)
        return timezone 
        
    def showTimeFormat(self):
        timezone = self.get_timezone()
        if self.dt != None:
            return self.dt.astimezone(timezone).strftime(self.time_formate)
        else:
            return ''
    
    def showDateFormat(self):
        timezone = self.get_timezone()
        return self.dt.astimezone(timezone).strftime(self.time_formate)
    
    def showStateTimeFormat(self, state):
        state_timezone = self.states_timezone[state]
        self.time_zone = state_timezone
        return self.showTimeFormat()
        
        
        
        