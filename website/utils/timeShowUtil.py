from django.conf import settings
from datetime import datetime, timedelta, date


class TimeShow():
    time = None
    
    def __init__(self, dt):
        self.time = dt
        
    def get_show_time(self):
        now = datetime.utcnow()
        now1 = datetime.now()
        #print self.time
        try:
            diff = now - self.time.replace(tzinfo=None)
        except:
            return ''
        
        second_diff = diff.seconds
        day_diff = diff.days
        
        if day_diff < 0:
            return ''
        #print second_diff
        if day_diff == 0:
            if second_diff < 60: 
                return 'just now'
            if second_diff < 300: 
                return 'one minute ago'
            if second_diff < 600:
                return 'five minutes ago'
            if second_diff < 15*60:
                return 'ten minutes ago'
            if second_diff < 30*60:
                return 'fifteen minutes ago'
            if second_diff < 60*60:
                return 'half an hour ago'
            if second_diff > 60*60:
                return str( second_diff / 3600 ) + " hours ago"
            
        if day_diff == 1:
            return "yesterday"
        if day_diff < 7:
            return str(day_diff) + " days ago"      
        if day_diff == 7:
            return "1 week ago"
        if day_diff < 14:
            return str(day_diff) + " days ago"         
        if day_diff < 31:
            return str(day_diff/7) + " weeks ago"
        if day_diff < 365:
            return str(day_diff/30) + " months ago"
        return str(day_diff/365) + " years ago" 
            
            
            
            
            
            