from django.conf import settings
from django.utils import simplejson as json
from datetime import datetime, timedelta, date
import datetime as ad
from website.models import UserCommentView

class CleanCommentViews():
    strMsg = ''
    days = 91
    objDateTimeNow = None
    
    def __init__(self):
        self.strMsg += '---------- Clean Start ----------<br />'
        self.clean_comment_views()
        self.strMsg += '<br />---------- Clean End ----------<br /><br />'
        
    def clean_comment_views(self):
        self.objDateTimeNow = date.today()
        obj3monthsbefore = self.objDateTimeNow - timedelta(days=self.days)
        self.strMsg += 'Delete the records before '+ str(obj3monthsbefore)+ '<br /><br />'
        #self.strMsg += 'Clean Records:<br /><br />'
        views = UserCommentView.objects.filter(view_datetime__lt = obj3monthsbefore)
        #self.strMsg += str(views) + '<br /><br />'
        views.delete()