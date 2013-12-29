from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor#, decode_jinga_template
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect

from website.utils.mathUtil import MathUtil
#from website.models import Jurisdiction

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from website.models import UserDetail, OrganizationMember, UserFavorite, Jurisdiction, AnswerReference, ViewOrgs
from jinja2 import FileSystemLoader, Environment
import hashlib
from django.conf import settings
import datetime
from datetime import timedelta, date
from django.db.models import Q
from website.utils.messageUtil import MessageUtil,add_system_message, get_system_message
from website.utils.timeShowUtil import TimeShow

from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil

from website.utils.miscUtil import UrlUtil


RECENT_UPDATES_PAGE_SIZE = 25


def log_out(request):
    url = request.META.get('HTTP_REFERER')
    logout(request)
    if url == None:
        url = '/'
    return redirect(url)

def sign_in_shell(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)  
    next = requestProcessor.getParameter('next') 
    if next == None:
        next = ''
    
    username = requestProcessor.getParameter('username') 
    action_key = requestProcessor.getParameter('action_key')
    if username != None:
        if request.user.username == username and request.user.is_authenticated():
            if action_key != None and action_key != '':
                if action_key == 'request_org':
                    orgid = requestProcessor.getParameter('orgid')
                    return redirect('/profile/?action_key='+action_key+'&orgid='+str(orgid)+'')
                else:
                    return redirect('/profile/')
            else:
                return redirect('/profile/')
        
    if action_key != None and action_key != '': 
        if action_key == 'request_org':   
            orgid = requestProcessor.getParameter('orgid')
            data['orgid'] = orgid
            data['action_key'] = action_key
    data['next'] = next       
    data['caller'] = 'sign_in_shell'        
    return requestProcessor.render_to_response(request,'website/accounts/sign_in_shell.html', data, '')    

def change_password(request):
    data = {}
    data['password'] = ''
    data['verify_password'] = ''
            
    form_id = 'form_change_password'            
    data['form_change_password_id'] = form_id
    

    requestProcessor = HttpRequestProcessor(request)  

    dajax = Dajax()
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):    
    
    
        if (ajax == 'change_password_submit'):
            data = {}
            form_id = 'form_change_password'

            data['form_change_password_id'] = form_id
            data['password'] = requestProcessor.getParameter('password')
            data['verify_password'] = requestProcessor.getParameter('verify_password')
          
            error_message = validate_change_password_form_data(data, form_id)  

            if len(error_message) == 0:           
                user = request.user
                if user is not None and user.id > 0:
                    
                    user = User.objects.get(id=user.id)
                    if user:
                        
                        user.set_password(data['password'])                      
                        user.save()
                        
                    else:
                        error_message[form_id+'_fail_reason'] = 'Please log in.'                          
                else:
                    error_message[form_id+'_fail_reason'] = 'Please log in'                      
                        
            
            if len(error_message) > 0:

                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
                             
                body = requestProcessor.decode_jinga_template(request,'website/accounts/change_password.html', data, '') 
                dajax.assign('#main_content','innerHTML', body)                    
            else:
                dajax.assign('#change_password_content','innerHTML', 'Your password was successfully changed.')   
            
         
            return HttpResponse(dajax.json())      
    
    return requestProcessor.render_to_response(request,'website/accounts/change_password.html', data, '')                           


def account(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)  
    data['accept_tou'] = '' 
    dajax = Dajax()
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        if (ajax == 'create_account'):
            
            data = {}
            data['email'] = None
            form_id = 'form_create_account'      
            data['form_create_account_id'] = form_id            
            invitation_key = requestProcessor.getParameter('invitation_key')
            
            if invitation_key != None:
                org_members = OrganizationMember.objects.filter(invitation_key__exact=invitation_key)
                if org_members:
                    data['invitation_key'] = invitation_key 
                    data['email'] = str(org_members[0].email)                    
                else:
                    data[form_name+'_fail_reason'] = 'The invitation is no longer valid.  You are still welcome to sign up with SolarPermit.org.'   
                    data['invitation_key'] = ''   
            else:
                print "normal create account"
            
            data['firstname'] = requestProcessor.getParameter('firstname') 
            data['lastname'] = requestProcessor.getParameter('lastname') 
            data['title'] = requestProcessor.getParameter('title') 
            data['display_as'] = requestProcessor.getParameter('display_as')             
                                                
            data['username'] = requestProcessor.getParameter('username')    
            if data['email'] == None:  # this is to avoid overide the email of the invited nonmember
                data['email'] = requestProcessor.getParameter('email')  
            #data['password'] = requestProcessor.getParameter('password')  
            #data['verify_password'] = requestProcessor.getParameter('verify_password')  
            #data['accept_tou'] = requestProcessor.getParameter('accept_tou')      
                        
            if data['username'] == None:
                data['username'] = ''   
            if data['email'] == None:
                data['email'] = ''   
            if data['firstname'] == None:
                data['firstname'] = '' 
            if data['lastname'] == None:
                data['lastname'] = ''  
                
            if data['display_as'] == None:
                data['display_as'] = 'realname' 
                                                               
            #if data['accept_tou'] == None:
            #    data['accept_tou'] = ''                                                      
            #body = decode_template('website/accounts/create_account.html', data) 
        
            body = requestProcessor.decode_jinga_template(request,'website/accounts/create_account.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/accounts/create_account.js', data, '')
            dajax.script(script)        
  
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            #dajax.script('$.fancybox("#fancyboxformDiv",{"autoDimensions": false,"width": "auto","height": "auto", "transitionIn": "none", "transitionOut": "none"})')
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'create_account_submit'):  
            data = {}       
            user_created = False
            form_id = 'form_create_account'
            data['form_create_account_id'] = form_id

            data['firstname'] = requestProcessor.getParameter('firstname')    
            data['lastname'] = requestProcessor.getParameter('lastname')    
            data['title'] = requestProcessor.getParameter('title')       
            data['display_as'] = requestProcessor.getParameter('display_as') 
            '''if data['display_as'] == 'username':                                   
                data['username'] = requestProcessor.getParameter('username')
            else:
                data['username'] =  requestProcessor.getParameter('email')  
            '''
            data['username'] = requestProcessor.getParameter('username') #username is now required
            data['email'] = requestProcessor.getParameter('email')  
            data['password'] = requestProcessor.getParameter('password')  
            data['verify_password'] = requestProcessor.getParameter('verify_password')  
            #data['accept_tou'] = requestProcessor.getParameter('accept_tou') 
            
            invitation_key = requestProcessor.getParameter('invitation_key') 
            if invitation_key == None:
                data['invitation_key'] = ''
            else:
                data['invitation_key'] = invitation_key
                        

            #if data['accept_tou'] == None:
            #    data['accept_tou'] = ''                
                    
            error_message = {}        
            error_message = validate_create_account_form_data(data, form_id)

            if len(error_message) == 0:
                msg_key = form_id + '_fail_reason'     
                        
                try:
                    
                    user = User.objects.create_user(data['username'], data['email'], data['password'])
                    user_created = True
                  
                    user = authenticate(username=data['username'], password=data['password'])
         
                    if user is not None:
                        user.first_name = data['firstname']
                        user.last_name = data['lastname']
                        user.save()
                        
                        user_detail = UserDetail()
                        user_detail.user_id = user.id
                        user_detail.display_preference = data['display_as']
                        user_detail.title = data['title']
                        user_detail.notification_preference = 'W'
                        user_detail.save()
                        
                        if user.is_active:
                            login(request, user)
                       
                            data['message'] = 'Success'
                            if request.user.is_authenticated():
                                view_org_obj = ViewOrgs()
                                request.session['accessible_views'] = view_org_obj.get_user_accessible_views(request.user)
                                data['site_url'] = settings.SITE_URL
                                send_new_account_confirmation(data)
                                dajax.script('jQuery.fancybox.close();')  
                                if data['invitation_key'] != '' :
                                    org_members = OrganizationMember.objects.filter(invitation_key = invitation_key)
                                    if org_members: 
                                        org_member = org_members[0]               
                                        org_member.user_id = request.user.id
                                        org_member.invitation_key = ''
                                        org_member.save()  
                                        add_system_message(request, 'success_create_account')
                                        dajax.script("location.href='" + settings.SITE_URL + "/profile/?action=user_profile';")           
                                else:
                                 
                                    add_system_message(request, 'success_create_account')
                                    url = request.META.get('HTTP_REFERER') or ''
                                    if '?' in url:
                                        url = url + '&reload=true#registered'                                        
                                    else:
                                        url = url + '?reload=true#registered'
                                    dajax.script("location.href='"+url+"'")
                                    #dajax.script("controller.showMessage('Account created. Thank you for joining the National Solar Permitting Database.', 'success')")

                                #dajax.script('location.reload();')
                                return HttpResponse(dajax.json())                                                        
                            else:
                         
                                data[msg_key] = "Something bad happened while the user was being logged in and authenticated."
 
                        else:
                            data[msg_key] =  "disabled account"
           
                    else:
                        data[msg_key] =  "invalid login"

                except Exception, e:
                    data[msg_key] = e.message
        
            #else:
            for msg_key in error_message.keys():
                data[msg_key] = error_message.get(msg_key)  
                    
            #body = decode_template(request,'website/accounts/create_account.html', data, '')                       
            #body = decode_template('website/accounts/create_account.html', data) 
            body = requestProcessor.decode_jinga_template(request,'website/accounts/create_account.html', data, '')             
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/accounts/create_account.js', data, '')
            dajax.script(script)        
            return HttpResponse(dajax.json())  
        
        if (ajax == 'user_profile'):
                              
            user = request.user
            user = User.objects.get(id=user.id)
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite      
                              
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'

            data['caller'] = 'user_profile'

            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)    
            return HttpResponse(dajax.json())   
        
        if (ajax == 'user_profile_short'):
            caller = requestProcessor.getParameter('caller')
            user_id = requestProcessor.getParameter('user_id')
            unique_list_id = requestProcessor.getParameter('unique_list_id')             
            user = User.objects.get(id=user_id)
            orgmembers = OrganizationMember.objects.filter(user = user, status='A', organization__status = 'A')
            data['user'] = user               
            data['orgmembers'] = orgmembers
            
            if caller == None:
                #div = 'simple_popup_div_on_page'
                params = 'zIndex: 8000'
            elif caller == 'dialog':
                #div = 'simple_popup_div_on_dialog'
                params = 'zIndex: 12000'
        
            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile_short.html', data, '') 
            dajax.assign('.info_content','innerHTML', body) 
            '''
            print 'oooooooooooooooo'
            dajax.assign('#' + div,'innerHTML', body)  
            print 'yyyyyyyyyyyy'
            dajax.script("open_simple_popup('"+str(unique_list_id)+"', '"+str(div)+"');")  
            print 'sssssssssssssssssss'
            '''
            dajax.script("controller.showInfo({target: '#id_"+unique_list_id+"', "+params+"});")
            return HttpResponse(dajax.json())                  
        
        if (ajax == 'user_profile_submit'):
            form_id = 'form_user_profile'      
            data['form_id'] = form_id
            error_message = {}
            
            data['userid'] = requestProcessor.getParameter('userid')            
            data['field_name'] = requestProcessor.getParameter('name')    
            data['mode'] = requestProcessor.getParameter('mode')  
            data['field_value'] = requestProcessor.getParameter(data['field_name'])    


            error_message = validate_create_account_form_data(data, form_id)
 
            if len(error_message) == 0:            
                user = User.objects.get(id=data['userid'])
                if data['field_name'] == 'username':
                    user.username = data['field_value']
                elif data['field_name'] == 'email':
                    user.email = data['field_value']
                    
                user.save()
                
                data['username'] = user.username    
                data['email'] = user.email          
                

            
            else:
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
                                
            user = request.user
            user = User.objects.get(id=user.id)
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite   
                            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)

            return HttpResponse(dajax.json())  
        
        if (ajax == 'terms_of_use'):
            body = requestProcessor.decode_jinga_template(request,'website/info/terms_of_use_second.html', data, '') 
            dajax.assign('#secondDialogDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/info/second_dialog.js', data, '')
            dajax.script(script)              
            
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
            return HttpResponse(dajax.json())             

        if (ajax == 'privacy_policy'):
            body = requestProcessor.decode_jinga_template(request,'website/info/privacy_policy_second.html', data, '') 
            dajax.assign('#secondDialogDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/info/second_dialog.js', data, '')
            dajax.script(script)    
                        
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'disclaimer'):
            body = requestProcessor.decode_jinga_template(request,'website/info/disclaimer_second.html', data, '') 
            dajax.assign('#secondDialogDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/info/second_dialog.js', data, '')
            dajax.script(script)    
                        
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
            return HttpResponse(dajax.json())         
                
        if (ajax == 'login'):
            data = {}
            form_name = "form_sign_in"
            data['username'] = requestProcessor.getParameter('username')  
            data['password'] = requestProcessor.getParameter('password') 
            data['keep_me_signed_in'] = requestProcessor.getParameter('keep_me_signed_in') 
            if data['keep_me_signed_in'] == None:
                data['keep_me_signed_in'] = 0
                
            data['unauthenticated_page_message'] = requestProcessor.getParameter('unauthenticated_page_message') 
            if data['unauthenticated_page_message'] == None:
                data['unauthenticated_page_message'] = ''
            
            
            data['caller'] = requestProcessor.getParameter('caller') 
            next = requestProcessor.getParameter('next')    
            if next == None:
                next = ''
            data['next'] = next                 

            error_message = validate_log_in_form_data(data, form_name)
           
            if request.method == 'POST' and len(error_message) == 0:
           
                try:
                    user = authenticate(username=data['username'], password=data['password'])
                except:
                    user = None
                    
                if user != None:
                    if user.is_active:
                        login(request, user)
                    else:
                        error_message[form_name+'_fail_reason'] = 'Disabled Account!'
                else:
                    status = ''
                    users = User.objects.filter(email__exact=str(data['username']))
                    if users:
                        user = users[0] # assumption is unique email in table users
                        user = authenticate(username=user.username, password=data['password'])            
                        if user is not None:
                            if user.is_active:
                                login(request, user)
                                reset_failed_login_attemps(request)
                            else:
                                error_message[form_name+'_fail_reason'] = 'Disabled Account!'
                                status = manage_failed_login(request, user)
                        else:
                            error_message[form_name+'_fail_reason'] = 'Invalid credentials.  Please try again.'
                            status = manage_failed_login(request, user)
                    else:
                        error_message[form_name+'_fail_reason'] = 'Invalid credentials.  Please try again.'                        
                        users = User.objects.filter(username__exact=str(data['username']))
                        if users:
                            user = users[0]
                            status = manage_failed_login(request, user)
                        else:
                            status = manage_failed_login(request)
           
                    if status == 'account_locked' or status == 'trouble_signing_in':
                        data['login_status'] = status
                        body = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.html', data, '') 
                        script = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.js', data, '')
                        '''
                        if data['caller'] == "sign_in_home":                        
                            dajax.assign('#signincontainer','innerHTML', body)    
                        else:
                            dajax.assign('#sign_in_block','innerHTML', body) 
                        '''
                        dajax.assign('#fancyboxformDiv','innerHTML', body)
                        dajax.script('controller.showModalDialog("#fancyboxformDiv");')   
                        dajax.script(script)
                                                                    
                        return HttpResponse(dajax.json())        
                    
            
            if len(error_message) == 0:
                if request.user.is_authenticated():
                    view_org_obj = ViewOrgs()
                    request.session['accessible_views'] = view_org_obj.get_user_accessible_views(request.user)
                    if int(data['keep_me_signed_in']) == 1:
                        request.session.set_expiry(None)
                    else:
                        request.session.set_expiry(0)                        
                   
                    #dajax.script("location.reload();")
                    
                    if data['caller'] == 'sign_in_shell':
                        if next == '':
                            dajax.script("location.href='" + settings.SITE_URL + "';")
                        else:
                            action_key = requestProcessor.getParameter('action_key')
                            if action_key == 'request_org':
                                orgid = requestProcessor.getParameter('orgid')
                                next_url = settings.SITE_URL + next + '?action_key='+action_key+'&orgid='+str(orgid)
                            
                                dajax.script("location.href='" + next_url + "';")
                            else:
                                dajax.script("location.href='" + settings.SITE_URL + next + "';")
                            
                    else:
                        #dajax.script("alert('" + request.META['HTTP_REFERER'] + "');");
                        #print request.META['HTTP_REFERER'] + 'xxx'
                        #dajax.script("window.location ='" + request.META['HTTP_REFERER'] + "';")
                        dajax.script("reload_page();")
                        #print request.META['HTTP_REFERER'] + 'yyy'
                        #return redirect(request.META['HTTP_REFERER'])
                        
                    #print 'zzzzzzzzzzzzzzzzzz'
                    return HttpResponse(dajax.json()) 
                    
                else:
                    error_message[form_name+'_fail_reason'] = 'Logged out.  Please try again.'            
        
            for msg_key in error_message.keys():
                data[msg_key] = error_message.get(msg_key) 
 
            if data['caller'] == "sign_in_home":
                body = requestProcessor.decode_jinga_template(request,'website/accounts/sign_in_home.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/sign_in_home.js', data, '')
                dajax.assign('#signincontainer','innerHTML', body) 
                dajax.script(script) 
            elif data['caller'] == 'sign_in_shell':
                body = requestProcessor.decode_jinga_template(request,'website/accounts/sign_in_home.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/sign_in_home.js', data, '')
                dajax.assign('#sign_in_shell_container','innerHTML', body)   
                dajax.script(script)                  
            else:
                body = requestProcessor.decode_jinga_template(request,'website/accounts/sign_in.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/sign_in.js', data, '')
                dajax.assign('#sign_in_block','innerHTML', body)     
                dajax.script(script) 

            #print 'aaaaaaaaaaaaaaaaaaaaaaa'
            dajax.script("set_error_class()")            
                   
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'change_password'):
            data['password'] = ''
            data['verify_password'] = ''
            
            form_id = 'form_change_password'            
            data['form_change_password_id'] = form_id
                        
            body = requestProcessor.decode_jinga_template(request,'website/accounts/change_password.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)    
            return HttpResponse(dajax.json())   
        
        if (ajax == 'change_password_submit'):
            data = {}
            form_id = 'form_change_password'

            data['form_change_password_id'] = form_id
            data['password'] = requestProcessor.getParameter('password')
            data['verify_password'] = requestProcessor.getParameter('verify_password')
          
            error_message = validate_change_password_form_data(data, form_id)  

            if len(error_message) == 0:           
                user = request.user
                if user is not None and user.id > 0:
                    user = User.objects.get(id=user.id)
                    if user:
                        user.set_password(data['password'])                      
                        user.save()
                        
                    else:
                        error_message[form_id+'_fail_reason'] = 'Please log in.'                          
                else:
                    error_message[form_id+'_fail_reason'] = 'Please log in'                      
                        
            
            if len(error_message) > 0:
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
       
                body = requestProcessor.decode_jinga_template(request,'website/accounts/change_password.html', data, '') 
                dajax.assign('#main_content','innerHTML', body)                    
            else:
                dajax.assign('#change_password_content','innerHTML', 'Your password was successfully changed.')   
            
         
            return HttpResponse(dajax.json())                        
        
        if (ajax == 'sign_in_home'):
            data['email'] = ''
            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/sign_in_home.html', data, '') 
            dajax.assign('#signincontainer','innerHTML', body)    
            return HttpResponse(dajax.json())         
        
        if (ajax == 'trouble_signing_in'):
            data = {}
            data['email'] = ''
            data['trouble_signing_in_message'] = {}
            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.html', data, '') 
            script = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.js', data, '')
            #dajax.assign('#signincontainer','innerHTML', body)    
            #dajax.script("controller.showMessage('This is to protect your account.', '');")
            
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            dajax.script(script)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')            
            return HttpResponse(dajax.json())    
        
        if (ajax == 'trouble_signing_in_submit'):
            data = {}
            error_message = {}
            form_name = 'form_trouble_signing_in'
            email = requestProcessor.getParameter('email')
            if email == None or email == '':
                error_message[form_name+'_email'] = 'Email address is required.'
            else:
                data['email'] = email
                users = User.objects.filter(email__exact=email)
                if users:
                    user = users[0]
                    user_details = UserDetail.objects.filter(user__exact=user)
                    salt = datetime.datetime.now()
                    salt_key = email + ':' + str(salt)
                    md5_key = hashlib.md5(salt_key).hexdigest()
                    if user_details:
                        user_detail = user_details[0]
                        user_detail.reset_password_key = md5_key
                        user_detail.save()
                    else:
                        user_detail = UserDetail()
                        user_detail.user_id = user.id
                        user_detail.reset_password_key = md5_key
                        user_detail.save()
                        
                    data['user'] = user
                    data['site_url'] = settings.SITE_URL
                    data['reset_password_key'] = user_detail.reset_password_key
                    send_email_password_reset(data)
                   
                else:
                    error_message[form_name+'_fail_reason'] = 'This email address does not exist in our records.'
                    
            if len(error_message) > 0:
         
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
                        
                body = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                script = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.js', data, '')
                dajax.script(script)
            else:
                body = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in_result.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                script = requestProcessor.decode_jinga_template(request,'website/accounts/trouble_signing_in.js', data, '')
                dajax.script(script)                
     
            #dajax.script("controller.showMessage('Please check your email.', 'success')")    example
                
            return HttpResponse(dajax.json())        
        
    #note: this non-ajax case will not work since we have not included create_account.js, but it is not used
    return requestProcessor.render_to_response(request,'website/accounts/create_account.html', data, '')      
    
def user_profile(request, id):
    data = {}
    requestProcessor = HttpRequestProcessor(request)      
    if not request.user.is_authenticated(): 
        return redirect(settings.SITE_URL)
    else:              
        user = User.objects.get(id=id)
        orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
        data['orgmembers'] = orgmembers            
        orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
        data['orgmembers_invite'] = orgmembers_invite      
                              
        data['userid'] = user.id                
        data['username'] = user.username    
        data['email'] = user.email
        data['mode'] = 'individual'

        data['caller'] = 'user_profile'

        data['form_id'] = 'form_user_profile'

           
    return requestProcessor.render_to_response(request,'website/accounts/user_profile_page.html', data, '')           
    
def validate_create_account_form_data(data, form_id):
    message = {}
    for item in data.keys():
        msg_key = form_id + '_field_' + item
        if item == 'username':
            if data[item] == '':
                message[msg_key] = 'Username is required.'
            elif len(data[item]) > 20:
                    message[msg_key] = 'A maximum of 20 characters is allowed.'
            else:
                users = User.objects.filter(username__iexact=data[item])
                if users:
                    message[msg_key] = 'This username is not available.'
                        
        if item == 'email':
            if data[item] == '':
                message[msg_key] = 'Email is required.'
            elif len(data[item]) > 75:
                message[msg_key] = 'Email can only be 75 characters maximum.'
            else:
                users = User.objects.filter(email__exact=data[item])
                if users:
                    message[msg_key] = 'An account with this email address already exists in the system.'
                                    
        if item == 'password':
            if data[item] == '':
                message[msg_key] = 'Password is required.'
            elif len(data[item]) < 8:
                message[msg_key] = 'Your password must be a minimum of 8 characters.'
            elif len(data[item]) > 128:
                message[msg_key] = 'Password cannot be longer than 128 characters'
            
 
        if item == 'verify_password':
            if data['password'] != data[item]:
                message[msg_key] = 'The password fields must be exactly the same.'
                
        if item == 'display_as':
            if data[item] =='realname':
                if data['firstname'] == '' or data['lastname'] == '':
                    message['firstname'] = 'Fist name is required.'
                    message['lastname'] = 'Last name is required'
        '''        
        if item == 'accept_tou':
            if data[item] == '':
                message[msg_key] = 'Terms of Use must be read and accepted.'
        '''    
    return message


def validate_reset_password_form_data(data, form_name):  
    message = {}
    for item in data.keys():
        msg_key = form_name + '_' + item
        if item == 'password':
            if data[item] == '':
                message[msg_key] = 'Password is required.'
            elif len(data[item]) < 8:
                message[msg_key] = 'Your password must be a minimum of 8 characters.'
            elif len(data[item]) > 128:
                message[msg_key] = 'Password cannot be longer than 128 characters'
            
 
        if item == 'verify_password':
            if data['password'] != data[item]:
                message[msg_key] = 'The password fields must be exactly the same.'
                 
    return message 

def validate_log_in_form_data(data, form_name):   
    message = {}
    for item in data.keys():
        msg_key = form_name + '_' + item
        if item == 'username':
            if data[item] == '':
                message[msg_key] = 'Required.'
                                    
        if item == 'password':
            if data[item] == '':
                message[msg_key] = 'Required.'
                 
    return message

def validate_change_password_form_data(data, form_id):  
    message = {}
    for item in data.keys():
        msg_key = form_id + '_field_' + item
        if item == 'password':
            if data[item] == '':
                message[msg_key] = 'Password is required.'
            elif len(data[item]) < 8:
                message[msg_key] = 'Your password must be a minimum of 8 characters.'
            elif len(data[item]) > 128:
                message[msg_key] = 'Password cannot be longer than 128 characters'
            
 
        if item == 'verify_password':
            if data['password'] != data[item]:
                message[msg_key] = 'The password fields must be exactly the same.'
                 
    return message 

def send_email_password_reset(data): 
    subject = 'Request to reset password'
    tp = get_template('website/emails/request_reset_password.html')
    c = Context(data)
    body = tp.render(c)
    from_mail = django_settings.DEFAULT_FROM_EMAIL
    to_mail = [data['email']]
    
    msg = EmailMessage( subject, body, from_mail, to_mail)
    msg.content_subtype = "html"   
    msg.send()

def send_new_account_confirmation(data):
    subject = 'Thank you for registering for the National Solar Permitting Database'
    tp = get_template('website/emails/new_account_confirmation.html')
    c = Context(data)
    body = tp.render(c)
    from_mail = django_settings.DEFAULT_FROM_EMAIL
    to_mail = [data['email']]
    
    msg = EmailMessage( subject, body, from_mail, to_mail)
    msg.content_subtype = "html"   
    msg.send()   
    
def manage_failed_login(request, user=None):
    format = "%Y-%m-%d %H:%M:%S"
    status = ''
    
    if user != None:
        if user.is_active == 0:
            status = 'account_locked'
            return status
    
    if 'failed_login_attempts' in request.session:
        num_failed_attempts = request.session['failed_login_attempts']
    else:
        num_failed_attempts = 0

    now_time_obj = datetime.datetime.now()   
    five_minutes_ago = datetime.timedelta(minutes=settings.TIME_PERIOD_FOR_FAILED_LOGIN_ATTEMPTS)      
    time_five_minutes_ago = now_time_obj - five_minutes_ago         
            
    if 'time_of_first_failed_login_attempt' in request.session:
        time_of_first_failed_login_attempt = request.session['time_of_first_failed_login_attempt']
        time_obj_of_first_failed_login_attempt = datetime.datetime.strptime(time_of_first_failed_login_attempt, format)   
    else:
        time_obj_of_first_failed_login_attempt = now_time_obj      #???                      
        
    if 'time_of_last_failed_login_attempt' in request.session:
        time_of_last_failed_login_attempt = request.session['time_of_last_failed_login_attempt']
        time_obj_of_last_failed_login_attempt = datetime.datetime.strptime(time_of_last_failed_login_attempt, format)    
    else:
        time_obj_of_last_failed_login_attempt = now_time_obj        #???
             



    
    
    if time_five_minutes_ago >  time_obj_of_last_failed_login_attempt:
        # 5 min has elasped since last failed attempt
        reset_failed_login_attemps(request, now_time_obj)
        num_failed_attempts = 1
    else:
        # still within 5 min since the last failed attempt
        # need to check if still within 5 min since the first failed attempt
        if time_five_minutes_ago <= time_obj_of_first_failed_login_attempt:
            # still within 5 min of first failed login.
            num_failed_attempts = num_failed_attempts + 1
        else:
            # 5 min has elapsed since the first failed attempt
            reset_failed_login_attemps(request, now_time_obj)
            num_failed_attempts = 1
            

    
    if int(num_failed_attempts) <= int(settings.SECOND_MAX_FAILED_LOGIN_ATTEMPTS):
        request.session['failed_login_attempts'] = num_failed_attempts
        request.session['time_of_last_failed_login_attempt'] = time_obj_of_last_failed_login_attempt.strftime(format) 
                    
    if int(num_failed_attempts) >= int(settings.SECOND_MAX_FAILED_LOGIN_ATTEMPTS):
        # lock account
        status = 'account_locked'
        if user != None:
            user.is_active = False
            user.save()        
    elif int(num_failed_attempts) >= int(settings.FIRST_MAX_FAILED_LOGIN_ATTEMPTS):
        # suggest trouble signing in
        status = 'trouble_signing_in'   
        
            

    
    return status # account_locked or trouble_signing_in

def reset_failed_login_attemps(request, now_time_obj=None):
    format = "%Y-%m-%d %H:%M:%S"    
    if 'time_of_first_failed_login_attempt' in request.session:
        del request.session['time_of_first_failed_login_attempt']
    if 'failed_login_attempts' in request.session:        
        del request.session['failed_login_attempts']
    if now_time_obj != None:
        request.session['time_of_first_failed_login_attempt']  = now_time_obj.strftime(format)
        request.session['time_of_last_failed_login_attempt']  = now_time_obj.strftime(format)        
    else:
        if 'time_of_last_failed_login_attempt' in request.session:             
            del request.session['time_of_last_failed_login_attempt']
            
            
def user_profile_full(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    dajax = Dajax()    
    data = {}
    if user.is_authenticated() == False:
        return redirect('/')

    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):   
        if (ajax == 'user_profile_first_name_submit'):     
            data['first_name'] = requestProcessor.getParameter('field_first_name')        
            data['form_first_name'] = 'form_first_name'   
            user_profile_first_name_div = requestProcessor.getParameter('user_profile_first_name_div')   
            user_obj = User.objects.get(id=user.id)                           
            user_obj.first_name = data['first_name']
            user_obj.save()             
            body = get_text_field_entity_html(data['form_first_name'], 'First name', 'first_name', user_obj.first_name, 'width:210px', 'required', "maxLength='30'", '' , request, "edit")
            dajax.assign('#'+str(user_profile_first_name_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'user_profile_last_name_submit'):     
            data['last_name'] = requestProcessor.getParameter('field_last_name')        
            data['form_last_name'] = 'form_last_name'   
            user_profile_last_name_div = requestProcessor.getParameter('user_profile_last_name_div')   
            user_obj = User.objects.get(id=user.id)                               
            user_obj.last_name = data['last_name']
            user_obj.save()             
            body = get_text_field_entity_html(data['form_last_name'], 'Last name', 'last_name', user_obj.last_name, 'width:210px', 'required', "maxLength='30'", '' , request, "edit")
            dajax.assign('#'+str(user_profile_last_name_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())  
                         
        if (ajax == 'user_profile_email_submit'):     
            data['email'] = requestProcessor.getParameter('field_email')        
            data['form_email'] = 'form_email'   
            user_profile_email_div = requestProcessor.getParameter('user_profile_email_div')   
            user_obj = User.objects.get(id=user.id)                             
            user_obj.email = data['email']
            user_obj.save()             
            body = get_text_field_entity_html(data['form_email'], 'Email', 'email', user_obj.email, 'width:210px', 'required email', "maxLength='75'", 'Valid email address please' , request, "edit")
            dajax.assign('#'+str(user_profile_email_div),'innerHTML', body)
            
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'user_profile_title_submit'):     
            data['title'] = requestProcessor.getParameter('title')        
            data['form_title'] = 'form_title'   
            user_profile_title_div = requestProcessor.getParameter('user_profile_title_div')   
            user_detail = UserDetail.objects.get(user_id=user.id)                             
            user_detail.title = data['title']
            user_detail.save()         
            dropdown = UserDetail.TITLES    
            #body = get_text_field_entity_html(data['form_title'], 'Title', 'title', user_detail.title, 'width:210px', 'required', "maxLength='200'", '' , request, "edit")
            body = get_dropdown_field_entity_html(data['form_title'], 'Title', 'title', dropdown, user_detail.title, 'width:210px', 'required', "", '' , request, "edit")            
            dajax.assign('#'+str(user_profile_title_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())                  
        
        if (ajax == 'user_profile_password_submit'):     
            data['password'] = requestProcessor.getParameter('password') 
            data['verify_password'] = requestProcessor.getParameter('verify_password')                           
            data['form_password'] = 'form_password'   
            user_profile_password_div = requestProcessor.getParameter('user_profile_password_div')   
            user_obj = User.objects.get(id=user.id)
            user_obj.set_password(data['password'])     
            user_obj.save()             
            body = get_password_field_entity_html(data['form_password'], 'Password', 'password', request, "edit")
            dajax.assign('#'+str(user_profile_password_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())  
        
        
        if (ajax == 'user_profile_display_as_submit'):     
            data['display_as'] = requestProcessor.getParameter('display_as')

            user_profile_display_as_div = requestProcessor.getParameter('user_profile_display_as_div')   
            user_detail = UserDetail.objects.get(user_id=user.id)
            user_detail.display_preference = data['display_as']
            user_detail.save()             
            user_obj = User.objects.get(id=user.id)
            
            message = {}
            msg_key = 'form_display_as' + '_field_username'
            #message[msg_key] = ''
            if data['display_as'] == 'username':
                data['username'] = requestProcessor.getParameter('username')     
                if data['username'] == '':
                    message[msg_key] = 'Username is required.'
                elif len(data['username']) > 20:
                        message[msg_key] = 'A maximum of 20 characters is allowed.'
                else:
                    users = User.objects.filter(username__iexact=data['username']).exclude(id=user.id) #exclude himself
                    if users:
                        message[msg_key] = 'This username is not available.'
                        
                if len(message) == 0:
                    user_obj.username = data['username']
                    user_obj.save()
                              

            body = get_display_as_field_entity_html(request, user.id, message)
            dajax.assign('#'+str(user_profile_display_as_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())     
        
        if (ajax == 'user_profile_username_submit'):     
            data['username'] = requestProcessor.getParameter('username')        
            data['form_username'] = 'form_username'   
            user_profile_username_div = requestProcessor.getParameter('user_profile_username_div')   
            user_obj = User.objects.get(id=user.id)                               
            user_obj.username = data['username']    # need to do validation
            user_obj.save()             
            body = get_text_field_entity_html(data['form_username'], 'Username', 'username', user_obj.username, 'width:210px', 'required', "maxLength='20'", '20 characters maximum' , request, "edit")
            dajax.assign('#'+str(user_profile_username_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())                          
        
        return HttpResponse(dajax.json()) 
    
    ############### firstname - start #####################
    data['user_profile_first_name_div'] = 'user_profile_first_name_div'   
    data['form_first_name'] = 'form_first_name'   
    user_obj = User.objects.get(id=user.id)
    body = get_text_field_entity_html(data['form_first_name'], 'First name', 'first_name', user_obj.first_name, 'width:210px', 'required', "maxLength='30'", '' , request, "edit")
    data['body_first_name'] = body
    
    ############### lastname - start #####################
    data['user_profile_last_name_div'] = 'user_profile_last_name_div'   
    data['form_last_name'] = 'form_last_name'   
    user_obj = User.objects.get(id=user.id)
    body = get_text_field_entity_html(data['form_last_name'], 'Last name', 'last_name', user_obj.last_name, 'width:210px', 'required', "maxLength='30'", '' , request, "edit")
    data['body_last_name'] = body        
                 
    ############### email - start #####################
    data['user_profile_email_div'] = 'user_profile_email_div'   
    data['form_email'] = 'form_email'   
    user_obj = User.objects.get(id=user.id)
    body = get_text_field_entity_html(data['form_email'], 'Email', 'email', user_obj.email, 'width:210px', 'required email', "maxLength='75'", 'Valid email address please' , request, "edit")
    data['body_email'] = body

    ############### title - start #####################
    data['user_profile_title_div'] = 'user_profile_title_div'   
    data['form_title'] = 'form_title'   
    user_obj = User.objects.get(id=user.id)
    dropdown = UserDetail.TITLES
    body = get_dropdown_field_entity_html(data['form_title'], 'Title', 'title', dropdown, user_obj.get_profile().title, 'width:210px', 'required', "", '' , request, "edit")
    data['body_title'] = body
    
    ############### password - start #####################
    data['user_profile_password_div'] = 'user_profile_password_div'   
    data['form_password'] = 'form_password'   
    body = get_password_field_entity_html(data['form_password'], 'Password', 'password', request, "edit")
    data['body_password'] = body    
    
    ############### display preference - start #####################
    data['user_profile_display_as_div'] = 'user_profile_display_as_div'   
    data['form_display_as'] = 'form_display_as'   

    message={}
    body = get_display_as_field_entity_html(request, user.id, message)
    data['body_display_as'] = body   
    #data['display_as'] = display_preference 
    
    ############### username - start #####################
    data['user_profile_username_div'] = 'user_profile_username_div'   
    data['form_username'] = 'form_username'   
    user_obj = User.objects.get(id=user.id)
    body = get_text_field_entity_html(data['form_username'], 'Username', 'username', user_obj.username, 'width:210px', 'required', "maxLength='20'", '20 characters maximum' , request, "edit")

    data['body_username'] = body        

    '''
    orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
    data['orgmembers'] = orgmembers            
    orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
    data['orgmembers_invite'] = orgmembers_invite      
    '''
    
    org_member_obj = OrganizationMember()
    data_org_members =  org_member_obj.get_user_orgs(user)                          
    data['orgmembers'] = data_org_members['orgmembers'] 
    data['orgmembers_invite'] = data_org_members['orgmembers_invite'] 
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    action_key = requestProcessor.getParameter('action_key')  
    if  action_key == 'request_org':
        orgid = requestProcessor.getParameter('orgid')
        data['action_key']= action_key
        data['orgid']= orgid                     
    return requestProcessor.render_to_response(request,'website/accounts/user_profile_full.html', data, '')    

def get_dropdown_field_entity_html(form_id, label, name, dropdown, value, style, class_name, attribute, help_text, request, mode="add"):
    
    requestProcessor = HttpRequestProcessor(request)
            
    data_entity = {}
    data_entity['value_existed'] = 'no'    
    
    if value != '':
        data_entity['value_existed'] = 'yes'        
    
    data_entity['value'] = value  # value to display
    data_entity['label'] = label  # field label
    data_entity['name'] = name    # name used in name and id of form field
    data_entity['mode'] = 'individual'         # not sure yet.
    data_entity['message_count'] = 0    
           
    # information need to configure the field, this case, a text field.
    data_form = {}                
    data_form['name'] = data_entity['name']
    if mode == 'edit':
        data_form['value'] = value 
    else:
        data_form['value'] = ''
    data_form['id'] = form_id+'_field_'+ data_form['name'] 
    data_form['class'] = class_name # for jquery validation
    data_form['style'] = style
    data_form['attributes'] =  attribute 
    data_form['help_text'] = help_text      
    data_form['msg_error'] = ''
    data_form['dropdown'] = dropdown
            
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/dropdown_field.html', data_form, '') 
    data_entity['form_fields'] = form_field
    body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_edit.html', data_entity, '') 
        
    return body       
     
     

def get_text_field_entity_html(form_id, label, name, value, style, class_name, attribute, help_text, request, mode="add"):
    requestProcessor = HttpRequestProcessor(request)
        
    data_entity = {}
    data_entity['value_existed'] = 'no'    

    if value != '':
        data_entity['value_existed'] = 'yes'        

    data_entity['value'] = value  # value to display
    data_entity['label'] = label  # field label
    data_entity['name'] = name    # name used in name and id of form field
    data_entity['mode'] = 'individual'         # not sure yet.
    data_entity['message_count'] = 0    
       
    # information need to configure the field, this case, a text field.
    data_form = {}                
    data_form['name'] = data_entity['name']
    if mode == 'edit':
        data_form['value'] = value 
    else:
        data_form['value'] = ''
    data_form['id'] = form_id+'_field_'+ data_form['name'] 
    data_form['class'] = class_name # for jquery validation
    data_form['style'] = style
    data_form['attributes'] =  attribute 
    data_form['help_text'] = help_text      
    data_form['msg_error'] = ''
    
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/text_field.html', data_form, '') 
    data_entity['form_fields'] = form_field
    body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_edit.html', data_entity, '') 
    
    return body  
   
def get_password_field_entity_html(form_id, label, name, request, mode="add"):
    requestProcessor = HttpRequestProcessor(request)
        
    data_entity = {}
    data_entity['value_existed'] = 'no'    

    if mode == 'edit':
        value = '********'
        
    if value != '':
        data_entity['value_existed'] = 'yes'        

    data_entity['value'] = value  # value to display
    data_entity['label'] = label  # field label    
    data_entity['name'] = name  # field label       
    data_entity['mode'] = 'individual'         # not sure yet.
    data_entity['message_count'] = 0
       
    # information need to configure the field, this case, a text field.
    data_form = {}           
    data_form['name'] = data_entity['name']         
    if mode == 'edit':
        data_form['value'] = value 
    else:
        data_form['value'] = ''
    data_form['id'] = form_id+'_field_'+ data_form['name'] 
    
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/password.html', data_form, '') 
    data_entity['form_fields'] = form_field
    body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_edit.html', data_entity, '') 
    
    return body  

def get_display_as_field_entity_html(request, user_id, message):
    requestProcessor = HttpRequestProcessor(request)
 
    user_obj = User.objects.get(id=user_id)
    display_preference = user_obj.get_profile().display_preference
    if display_preference == 'realname':
        display_value = 'Display my real first and last name'
        value = 'realname'
    else:
        display_value = 'Display as ' + user_obj.username
        value = 'username'
        
    
    data_entity = {}
    data_entity['value_existed'] = 'no'    

    if value != '':
        data_entity['value_existed'] = 'yes'        

    data_entity['value'] = display_value  # value to display
    data_entity['label'] = 'Display as'  # field label
    data_entity['name'] = 'display_as'    # name used in name and id of form field
    data_entity['mode'] = 'individual'         # not sure yet.
    data_entity['message_count'] = len(message) 

       
    # information need to configure the field, this case, a text field.
    data_form = {}                
    data_form['display_as'] = value
    data_form['username'] = user_obj.username
    data_form['message'] = message
            
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/user_profile_display_as.html', data_form, '') 
    data_entity['form_fields'] = form_field
    body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_edit.html', data_entity, '') 
    
    return body 

def user_favorite(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    if user.is_authenticated() == False:
        return redirect('/')
    data = {}
    data['current_nav'] = 'fj'
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    
    if (ajax != None):
        if ajax == 'add_favorite':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            
            uf = UserFavorite()
            uf.user = user
            uf.entity_id = entity_id
            uf.entity_name = entity_name
            uf.save()
            
            if entity_name == 'Jurisdiction':
                try:
                    jurisdiction = Jurisdiction.objects.get(id = entity_id)
                    dajax.script("controller.showMessage('"+jurisdiction.show_jurisdiction('long')+" added to favorites.', 'success', 3)")
                except:
                    jurisdiction = None
                    dajax.script("controller.showMessage('Save success.', 'success', 3)")
                dajax.assign('#favorite-a', 'innerHTML', 'Remove from favorites')
                dajax.assign('#favorite-a-image', 'innerHTML', '<img width="12" height="12" src="/media/images/add-to-favorites.png" alt="Remove From Favorites">')
                #dajax.script('("#favorite-a-'+entity_id+'").attr("title","Remove '+jurisdiction.show_jurisdiction('long')+' to your favorite jurisdictions");')
                dajax.script('$("#favorite-a").tooltip("option", "content", "Remove '+jurisdiction.show_jurisdiction('long')+' from your favorite jurisdictions");')
                dajax.script('$("#favorite-a").unbind("click");')
                dajax.script('$("#favorite-a").bind("click", function (){controller.postRequest("/user_favorite/", {ajax:"remove_favorite", entity_id:'+entity_id+',  entity_name:"Jurisdiction"});return false;});')
                #dajax.script('$("#favorite-a-image").attr("scr", "/media/images/add-to-favorites.png");')
            else:
                dajax.script("controller.showMessage('Save success.', 'success', 3)")   
            
            #dajax.script('alert('+jurisdiction_id+')')
        if ajax == 'remove_favorite' or ajax =='remove_favorite_jurisdiction':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            
            ufs = UserFavorite.objects.filter(entity_id = entity_id, entity_name = entity_name, user = user)
            ufs.delete()
            
            if entity_name == 'Jurisdiction':
                try:
                    jurisdiction = Jurisdiction.objects.get(id = entity_id)
                    dajax.script("controller.showMessage('"+jurisdiction.show_jurisdiction('long')+" removed from favorites.', 'success', 3)")
                except:
                    jurisdiction = None
                    dajax.script("controller.showMessage('Remove success.', 'success', 3)")
                if ajax == 'remove_favorite':
                    #dajax.script('$("#favorite-a-image").attr("scr", "/media/images/add-to-favorites-hollow.png");')
                    dajax.assign('#favorite-a-image', 'innerHTML', '<img width="12" height="12" src="/media/images/add-to-favorites-hollow.png" alt="Add to Favorites">')
                    dajax.assign('#favorite-a', 'innerHTML', 'Add to favorites')
                    dajax.script('$("#favorite-a").tooltip("option", "content", "Add '+jurisdiction.show_jurisdiction('long')+' to your favorite jurisdictions");')
                    dajax.script('$("#favorite-a").unbind("click");')
                    dajax.script('$("#favorite-a").bind("click", function (){controller.postRequest("/user_favorite/", {ajax:"add_favorite", entity_id:'+entity_id+',  entity_name:"Jurisdiction"});return false;});')
                if ajax == 'remove_favorite_jurisdiction':
                    dajax.script('$("#favorite-'+entity_id+'").remove();')
                    
            else:
                dajax.script("controller.showMessage('Remove success.', 'success', 3)")
        
        if ajax == 'show_jurisdiction_updates':
            jid = requestProcessor.getParameter('jurisdiction_id')
            
            if jid == '0':
                ufs = UserFavorite.objects.filter(user = user)
                jids = []
                for uf in ufs:
                    jids.append(uf.entity_id)
                jurisdictions = Jurisdiction.objects.filter(id__in = jids)
            else:
                jurisdictions = Jurisdiction.objects.filter(id__in = [jid] )
            
            recent_updates = get_all_updates(jurisdictions)
            recent_updates = recent_updates[0:RECENT_UPDATES_PAGE_SIZE]
            updates = get_recent_updates(request, recent_updates)
         
            data['updates'] = updates
            data['next_page_param'] = 'page=2'
            data['next_page_num'] = 2
            data['search_param'] = '&jid='+jid
            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/recent_update_list.html', data, '') 
            dajax.assign('#updates-list','innerHTML', body)
        
        if ajax == 'open_notification_setting':
            data['options'] =[['I', 'Immediately'], ['D', 'Daily'], ['W', 'Weekly'], ['M', 'Monthly'], ['N', 'Never']] 
            data['name'] = 'notifcations'
            data['id'] = 'notifcation'
            notification_preference = user.get_profile().notification_preference
            if notification_preference == '' or notification_preference == None:
                data['value']  = 'N'
            else:
                data['value']  = user.get_profile().notification_preference
            
            body = requestProcessor.decode_jinga_template(request,'website/accounts/notification_setting.html', data, '') 
            script = requestProcessor.decode_jinga_template(request, 'website/accounts/notification_setting.js', data, '')
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            dajax.script(script) 
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
        
        if ajax == 'notification_setting_submit':
            data = []
            notification = requestProcessor.getParameter('notifcations')
            if notification != None or notification != '':
                user_detail = UserDetail.objects.get(user_id=user.id)  
                user_detail.notification_preference = notification
                user_detail.save()
                
                dajax.script("controller.showMessage('Setting saved.', 'success')")
                dajax.script('controller.updateUrlAnchor("#notification_updated");')
                
            dajax.script('jQuery.fancybox.close();') 
            
        
        return HttpResponse(dajax.json())
    
    ufs = UserFavorite.objects.filter(user = user)
    jids = []
    for uf in ufs:
        jids.append(uf.entity_id)
    jurisdictions = Jurisdiction.objects.filter(id__in = jids)
    #recent_updates = AnswerReference.objects.filter( jurisdiction__in = jurisdictions )
    #recent_updates = recent_updates.filter(Q(approval_status = 'P')| Q(approval_status = 'A')).order_by('-modify_datetime')[0:RECENT_UPDATES_PAGE_SIZE]
    recent_updates = get_all_updates(jurisdictions)
    recent_updates = recent_updates[0:RECENT_UPDATES_PAGE_SIZE]
    updates = get_recent_updates(request, recent_updates)
    
    data['jurisdictions'] = jurisdictions.order_by('name')
    name_list = []
    for j in jurisdictions:
        aa ={}
        aa['name'] = j.show_jurisdiction('short')
        aa['id'] = j.id
        aa['name_for_url'] = j.name_for_url
        name_list.append(aa)
    from operator import itemgetter, attrgetter 
    #sorted(students, key=itemgetter(2))      
    data['jurisdiction_name_list'] = sorted(name_list,key=itemgetter('name'), reverse=False)
    data['updates'] = updates
    data['user'] = user
    
    data['next_page_param'] = 'page=2'
    data['search_param'] = '&jid=0'
    data['next_page_num'] = 2
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    return requestProcessor.render_to_response(request,'website/accounts/user_favorite.html', data, '') 

def get_all_updates(jurisdictions):
    objDateTimeNow = date.today()
    obj3monthsbefore = objDateTimeNow - timedelta(days=31)
    recent_updates = AnswerReference.objects.filter( jurisdiction__in = jurisdictions, create_datetime__gt = obj3monthsbefore )
    recent_updates = recent_updates.filter(Q(approval_status = 'P')| Q(approval_status = 'A')).order_by('-modify_datetime')[0:100]
    all_updates = []
    temp_list = {}
    jurisdiction_list = []
    
    for update in recent_updates:
        if jurisdiction_list.count(update.jurisdiction.id) == 0:
            jurisdiction_list.append(update.jurisdiction.id)
            temp_list[update.jurisdiction.id] = []
            temp_list[update.jurisdiction.id].append(update)
        else:
            temp_list[update.jurisdiction.id].append(update)
      
    for jurisdiction_id in jurisdiction_list:
        temp = temp_list[jurisdiction_id]
        for update1 in temp:
            all_updates.append(update1)
            
    return all_updates

def get_recent_updates(request, recent_updates):
    updates = []
    data = {}
    validation_util_obj = FieldValidationCycleUtil() 
    requestProcessor = HttpRequestProcessor(request)
    old_jurisdiction_id = 0
    for update in recent_updates:
        update_map = {}
        if old_jurisdiction_id != update.jurisdiction.id:
            update_map['title_flag'] = True 
            old_jurisdiction_id = update.jurisdiction.id
        else:
             update_map['title_flag'] = False
        if update.approval_status == 'P':
            time_obj = TimeShow(update.create_datetime)
            creator= update.creator.get_profile().get_display_name()
            creator_link = '<a href="#" id="id_a_' + str(update.id) + '" onmouseover="controller.postRequest(\'/account/\', {ajax: \'user_profile_short\', user_id: \'' + str(update.creator.id) + '\',  unique_list_id: \'a_' + str(update.id) + '\'  });"  >' + creator + '</a>'
        else:
            time_obj = TimeShow(update.status_datetime)
            creator = ''
            creator_link = ''
        update_map['time'] = time_obj.get_show_time()
        update_map['creator'] = creator
        update_map['question'] = update.question.question
        data['action'] = 'refresh_ahj_qa'
        data['jurisdiction_type'] = update.jurisdiction.get_jurisdiction_type()              
        data['jurisdiction_id'] = update.jurisdiction.id   
        data['jurisdiction'] = update.jurisdiction 
        data['this_question'] = update.question
        
        category_name = 'VoteRequirement' 
        vote_info = validation_util_obj.get_jurisdiction_voting_info_by_category(category_name, update.jurisdiction, update.question.category, update.question)
        terminology = validation_util_obj.get_terminology(update.question)  
        #question_content = validation_util_obj.get_AHJ_question_data(request, update.jurisdiction, update.question, data)  
        question_content = validation_util_obj.get_authenticated_displayed_content(request, update.jurisdiction, update.question, vote_info, [update], terminology)
        for key in question_content.keys():
            data[key] = question_content.get(key) 
        
        body1 = requestProcessor.decode_jinga_template(request,'website/accounts/favorite_items_answer.html', data, '')
        
        #validation_util_obj = FieldValidationCycleUtil()
        #answer = validation_util_obj.get_formatted_value(update.value, update.question)
        update_map['answer'] = body1
        update_map['question_type'] = update.question.form_type
        update_map['jurisdiction'] = update.jurisdiction
        if update.question.form_type  == 'CF':
            if update.approval_status == 'P':
                update_map['type'] = 'Custom field suggested by ' + creator_link + ' - <span class="time">'+ update_map['time'] + '</span>'
            else:
                update_map['type'] = 'Custom field suggested verified - <span class="time">'+ update_map['time'] + '</span>'
        else:
            if update.approval_status == 'P':
                update_map['type'] = 'New suggestion for <b>' + update.question.question + '</b> by '+ creator_link + ' - <span class="time">'+ update_map['time'] + '</span>'
            else:
                update_map['type'] = '<b>' + update.question.question +'</b> verified - <span class="time">'+ update_map['time'] + '</span>'
        
        
        updates.append(update_map)
        
    return updates
    
def updates_search(request):
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    
    page = requestProcessor.getParameter('page')
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
    range_start = (page_number - 1) * RECENT_UPDATES_PAGE_SIZE
    range_end = page_number * RECENT_UPDATES_PAGE_SIZE
    
    jid = requestProcessor.getParameter('page')
    if jid == '0':
        ufs = UserFavorite.objects.filter(user = user)
        jids = []
        for uf in ufs:
            jids.append(uf.entity_id)
        jurisdictions = Jurisdiction.objects.filter(id__in = jids)
    else:
        jurisdictions = Jurisdiction.objects.filter(id__in = [jid] )
    
    recent_updates = get_all_updates(jurisdictions)
    recent_updates = recent_updates[range_start:range_end]
    updates = get_recent_updates(request, recent_updates)
    data['updates'] = updates
    search_param = '&jid='+jid
    data['next_page_param'] = 'page='+str(page_number + 1)
    data['next_page_num'] = page_number + 1
    data['search_param'] = search_param
    
    return requestProcessor.render_to_response(request,'website/accounts/recent_update_list.html', data, '')  
    
        
        
        
        
        
        
