from django.conf import settings
from django.utils import simplejson as json
from django.contrib.auth.models import User
from datetime import datetime, timedelta, date
import datetime as ad

from django.template.loader import get_template
from django.template import Context
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.db.models import Q
from django.utils.timezone import utc

from website.models import Jurisdiction, UserFavorite
from website.utils.timeShowUtil import TimeShow

from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil

class NotificationHelper():
    strMsg = ''
    objDateTimeNow = None
    type = ''
    
    def __init__(self, type = 'D'):
        #self.jurisdictions = jurisdictions
        self.objDateTimeNow = datetime.utcnow()
        #self.objDateTimeNow = datetime.now()
        self.type = type
        #self.strMsg += self.type + '<br><br>'
        self.sent_users_notification()
        #self
    
    def sent_users_notification(self):
        users = self.get_all_user()
        for user in users:
            data = {}
            data['user'] = user
            fh = FavoriteHelper()
            jurisdictions = fh.get_user_favorite_jurisdiction(user)
            if user.get_profile().notification_preference == self.type:  
                if self.type == 'I':
                    updates, j_list = self.get_immediate_updates(jurisdictions)
                    data['subject'] = 'Favorite Jurisdiction Recently Updates'                   
                if self.type == 'D':            
                    updates, j_list = self.get_daily_updates(jurisdictions)
                    data['subject'] = 'Favorite Jurisdiction Daily Updates'
                if self.type == 'W': 
                    updates, j_list = self.get_week_updates(jurisdictions) 
                    data['subject'] = 'Favorite Jurisdiction Weekly Updates'
                if self.type == 'M':
                    updates, j_list = self.get_month_updates(jurisdictions)
                    data['subject'] = 'Favorite Jurisdiction Monthly Updates'
                data['jurisdictions'] = j_list
                data['site_url'] = django_settings.SITE_URL
                data['updates'] = updates
                data['type'] =  self.type
                if len(updates) > 0:
                    self.send_mail(data)
    
    def get_all_user(self):
        return User.objects.all()
    
    def get_immediate_updates(self, jurisdictions):
        return self.get_updates(jurisdictions, 60, 'seconds')
        
    def get_daily_updates(self, jurisdictions):
        return self.get_updates(jurisdictions, 1)
    
    def get_week_updates(self, jurisdictions):
        return self.get_updates(jurisdictions, 7)
    
    def get_month_updates(self, jurisdictions):
        return self.get_updates(jurisdictions, 30)
    
    def get_updates(self, jurisdictions, num, type="days"):
        if type == "days":
            obj3monthsbefore = self.objDateTimeNow - timedelta(days = num)
        else:
            obj3monthsbefore = self.objDateTimeNow - timedelta(seconds = num)
        
        print str(obj3monthsbefore.replace(tzinfo=utc))
        updates = []
        jurisdiction_list = []
        for jurisdiction in jurisdictions:
            jurisdiction_list.append(jurisdiction.id)
            
            jups = jurisdiction.getLatestUpdates()
            
            jups = jups.filter(modify_datetime__gt = obj3monthsbefore.replace(tzinfo=utc))
            
            jups = jups.filter(Q(approval_status = 'P')| Q(approval_status = 'A'))
            
            aaa = []
            old_jurisdiction_id = 0
            for up in jups:
                update_map = {}
                if old_jurisdiction_id != up.jurisdiction.id:
                    update_map['title_flag'] = True 
                    old_jurisdiction_id = up.jurisdiction.id
                else:
                     update_map['title_flag'] = False
                if up.approval_status == 'P':
                    time_obj = TimeShow(up.create_datetime)
                    creator= up.creator.get_profile().get_display_name()
                else:
                    time_obj = TimeShow(up.status_datetime)
                    creator = ''
                update_map['time'] = time_obj.get_show_time()
                update_map['creator'] = creator
                update_map['question'] = up.question.question
                validation_util_obj = FieldValidationCycleUtil()
                answer = validation_util_obj.get_formatted_value(up.value, up.question)
                update_map['answer'] = answer
                update_map['question_type'] = up.question.form_type
                update_map['jurisdiction'] = up.jurisdiction
                update_map['jurisdiction_name'] = up.jurisdiction.show_jurisdiction('short')
                if up.question.form_type  == 'CF':
                    if up.approval_status == 'P':
                        update_map['type'] = 'Custom field suggested by ' + creator + ' '+ update_map['time']
                    else:
                        update_map['type'] = 'Custom field suggested verified '+ update_map['time']
                else:
                    if up.approval_status == 'P':
                        update_map['type'] = 'New suggestion for ' + up.question.question + ' by '+ creator + ' '+ update_map['time']
                    else:
                        update_map['type'] = up.question.question +' verified '+ update_map['time']
                
                updates.append(update_map)
            #updates[jurisdiction.id] = aaa
            #updates[jurisdiction.id] = jurisdiction.getLatestUpdates().filter(modify_datetime__lt = obj3monthsbefore)
  
        return updates, jurisdiction_list
    
    def send_mail(self, data):
        from jinja2 import FileSystemLoader, Environment
        template_dirs = settings.TEMPLATE_DIRS
        env = Environment(loader=FileSystemLoader(template_dirs))
        template = env.get_template('website/emails/notification.html')
        body = template.render(**data) 
           
        subject = data['subject']
        '''
        tp = get_template('website/emails/notification.html')
        c = Context(data)
        body = tp.render(c)
        '''    
  
        #self.strMsg += body
        #self.strMsg += str(body)
        
        from_mail = django_settings.DEFAULT_FROM_EMAIL        
        msg = EmailMessage( subject, body, from_mail, [data['user'].email])
        msg.content_subtype = "html"   
        msg.send()     
    
class FavoriteHelper():
    
    def get_user_favorite_jurisdiction(self, user):
        ufs = UserFavorite.objects.filter(user = user, entity_name = 'Jurisdiction')
        jids = []
        for uf in ufs:
            jids.append(uf.entity_id)
        jurisdictions = Jurisdiction.objects.filter(id__in = jids)
        
        return jurisdictions
    
    