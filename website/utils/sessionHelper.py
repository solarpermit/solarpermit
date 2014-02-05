from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
#from server.website.models import *
from website.utils.httpUtil import HttpRequestProcessor

class SessionHelper():
    message = ''
    error = False
    uuid = None
    
    def checkSession(self, sid):
        self.error = False
        self.message = ''
        self.uuid = None
        #look up session from db
        try:
            sObject = Session.objects.get(pk=sid) #session object from db
        except:
            self.error = True
            self.message = 'Invalid session.'
            return None
        
        #see if session expired
        if sObject.expire_date < datetime.now():
            self.error = True
            self.message = 'Invalid session.'
            return None
    
    def getUserUuidBySession(self, sid):
        self.error = False
        self.message = ''
        self.uuid = None
        #look up session from db
        try:
            sObject = Session.objects.get(pk=sid) #session object from db
        except:
            self.error = True
            self.message = 'Session does not exist.'
            return None
        
        #see if session expired
        if sObject.expire_date < datetime.now():
            self.error = True
            self.message = 'Session expired.'
            return None
        
        self.message += 'Expire: ' + str(sObject.expire_date)
            
        #get user uuid from session
        try:
            s = SessionStore(session_key=sid) #the session itself
            #print '-----'+str(s['uuid']);
            self.uuid = s['uuid']
        except:
            self.error = True
            self.message = 'Session is missing user uuid.'
            return None
        
        return self.uuid
    '''
    def getUserDetailBySession(self, sid):
        self.getUserUuidBySession(sid)
        if self.error:
            return None
        try:
            userDetail = UserDetail.objects.get(user_uuid=self.uuid)
        except:
            self.error = True
            self.message = 'Cannot find the user detail for this session.'
            return None
        
        return userDetail
     '''   
        
    