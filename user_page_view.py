
from django.conf import settings as django_settings
from django.contrib.auth.models import User
#from website.models import UserDetail
from website.utils.httpUtil import HttpRequestProcessor
from django.db import models
import datetime
from website.models import UserPageView

class UserPageViewMiddleWare(object):

    def process_request(self, request):
        requestProcessor = HttpRequestProcessor(request)      
        user_id = request.user.id
        path_info = ''
        if user_id != None:
            today = datetime.date.today().strftime("%Y-%m-%d")
            '''
            if 'last_page_view_date' in request.session:
                
                if today != request.session['last_page_view_date']:
                    request.session['last_page_view_date'] = today  
                    self.store_db(path_info, today, user_id)  
            else:
                request.session['last_page_view_date'] = today
                self.store_db(path_info, today, user_id)                
            '''                
            #print request
            
            path_info = request.META['PATH_INFO']
            if '/media' not in path_info and '/siteadmin' not in path_info:
                if 'ajax' not in request.POST:
                    if request.META['QUERY_STRING'] != '' and request.META['QUERY_STRING'] != None:
                        path_info = path_info + "?" + request.META['QUERY_STRING']
                        
                    user_page_view = UserPageView()       
                    user_page_view.user_id = user_id
                    user_page_view.url = path_info
                    user_page_view.last_page_view_date = datetime.datetime.now()
                    user_page_view.save()
        
                
    def store_db(self, path_info, last_page_view_date, user_id):
        
        
        
        '''
        user = User.objects.get(id=user_id)
        user_page_views = UserPageView.objects.filter(user = user)
        if len(user_page_views) > 0:
            user_page_view = user_page_views[0]
            user_page_view.last_page_view_date = last_page_view_date
            user_page_view.save()
        else:
            user_page_view = UserPageView()       
            user_page_view.user_id = user_id
            user_page_view.last_page_view_date = last_page_view_date
            user_page_view.save()
        '''