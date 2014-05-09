"""middleware that allows anonymous users
receive messages using the now deprecated `message_set()`
interface of the user objects.

To allow anonymous users accept messages, a special
message manager is defined here, and :meth:`__deepcopy__()` method
added to the :class:`AnonymousUser` so that user could be pickled.

Secondly, it sends greeting message to anonymous users.
"""
#from askbot.models import BadgeData, Award, User
from django.conf import settings as django_settings
#from askbot.conf import settings as askbot_settings
from django.contrib.auth.models import User
from website.models import UserDetail
from website.utils.httpUtil import HttpRequestProcessor
import hashlib
from django.db import models


class ProcessPasswordMiddleWare(object):
    """Middleware that attaches messages to anonymous users, and
    makes sure that anonymous user greeting is shown just once.
    Middleware does not do anything if the anonymous user greeting
    is disabled.
    """
    def process_request(self, request):
        """Enables anonymous users to receive messages
        the same way as authenticated users, and sets
        the anonymous user greeting, if it should be shown"""
        requestProcessor = HttpRequestProcessor(request)      
        username = requestProcessor.getParameter('username')
        if username == None:
            username = ''
        password = requestProcessor.getParameter('password')  
        if password == None:
            password = ''
        #print "username :: " + str(username)
        #print "password :: " + str(password)
        
        authentication = True
        if username != '' and password != '':
            users_by_username = User.objects.filter(username__exact=username)
            users_by_email = User.objects.filter(email__exact=username)
            if users_by_username:
                user = users_by_username[0]
            elif users_by_email:
                user = users_by_email[0]
            else:
                authentication = False
                
            if authentication:
                if user.password == '':
                    user_details = UserDetail.objects.filter(user__exact=user)
                    if user_details:
                        user_detail = user_details[0]
                        if user_detail.old_password != '':
                            print "old_password :: " + str(user_detail.old_password)
                            salt = 'W3yZmDNLeykU2GHmPS4K3Rx40T2Q7VlC7Y5P7wi5McL5YvfzGNOahshX2lta1PbP'
                            
                            #print "set_password :: " + password
                            salt_password = password + ':' + salt
                            md5_password = hashlib.md5(salt_password).hexdigest()
            
                            print "md5_password :: " + str(md5_password)
                            if md5_password == user_detail.old_password:
                                #print "validated against md5.  ok!. save the sha1 version."
                                user.set_password(password)
                                user.save()
                                user_detail.old_password = ''
                                user_detail.save()
                            else:
                                print "validated against md5.  NOT OK!  not save the sha1 version"
                
        


