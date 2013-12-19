from datetime import datetime, timedelta
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.contrib.auth import authenticate, logout
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from website.utils.httpUtil import HttpRequestProcessor
from website.utils.sessionHelper import SessionHelper
from website.models import UserDetail

def get_user(request):
    requestProcessor = HttpRequestProcessor(request)
    
    output = {}
    output['users'] = []
    
    text = requestProcessor.getParameter('text')
    if text == None: 
       return HttpResponse(json.dumps(output))
    
    #only if text is at least 3 chars
    if len(text) > 2:
        users = User.objects.filter(Q(username__icontains=text) | Q(first_name__icontains=text) | Q(last_name__icontains=text)).order_by('username')[0:20]
        for user in users:
            user_item = {}
            user_item['id'] = user.id
            user_item['username'] = user.username
            user_item['name'] = ''
            if user.first_name != None:
                user_item['name'] += user.first_name + ' '
            if user.last_name != None:
                user_item['name'] += user.last_name
            output['users'].append(user_item)
        
    return HttpResponse(json.dumps(output))
    