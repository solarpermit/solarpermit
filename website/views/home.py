from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor
#from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect
from django.template.loader import get_template
from django.template import Context, RequestContext, Template

from django.core.mail.message import EmailMessage

#from django.contrib.jinja import render_to_response, render_to_string

#from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.conf import settings
#from django.contrib.auth.hashers import make_password
from jinja2 import FileSystemLoader, Environment
from compressor.contrib.jinja2ext import CompressorExtension
from website.models import UserDetail, JurisdictionRating, Jurisdiction
import hashlib

from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from django.contrib.auth import authenticate, login, logout

def home(request):
    user = request.user
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    data['accept_tou'] = '' 
    data['home'] = 'True' 
    dajax = Dajax()
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
              
        
        #default response for all ajax
        return HttpResponse(dajax.json())  

    data['login'] = 'False'

    if user.is_authenticated():
        data['login'] = 'True'
    elif user.is_active == False:
        data['login_status'] = 'account_locked'
        
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    
    data['recently_updated_jurs'] = JurisdictionRating.recently_updated()
    
    data['popular_jurs'] = JurisdictionRating.most_popular()
    
    
        
    
    
    invitation_key = requestProcessor.getParameter('invitation_key')    
    if invitation_key != '' and invitation_key != None:
        data['action_key'] = 'create_account'
        data['invitation_key'] = invitation_key
        if user.is_authenticated():
            logout(request) 
                       
        return requestProcessor.render_to_response(request,'website/home.html', data, '')        
        
        
    action = requestProcessor.getParameter('action')    
    if action != '' and action != None:
        data['action_key'] = action       
    next_url = requestProcessor.getParameter('next')    
    data['caller'] = 'sign_in_home'
    data['current_nav'] = 'home'
    
    if user.is_authenticated() and (next_url != None and next_url != ''):
        return redirect(next_url)
    else:
        return requestProcessor.render_to_response(request,'website/home.html', data, '')
    #return render_to_response('website/home.html', data, context_instance=RequestContext(request))
    
    
def reset_password(request, reset_password_key=''):
    data = {}
    error_message = {}    
    requestProcessor = HttpRequestProcessor(request)  
        
    dajax = Dajax()
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        if (ajax == 'launch_reset_password'):
            data = {}
            form_name = 'form_reset_password'
            reset_password_key = requestProcessor.getParameter('reset_password_key')
            data['reset_password_key'] = reset_password_key
            user_details = UserDetail.objects.filter(reset_password_key__exact=reset_password_key)
            if user_details:
                body = requestProcessor.decode_jinga_template(request,'website/accounts/reset_password.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/reset_password.js', data, '')                
            else:
                data[form_name+'_fail_reason'] = 'The reset password key is no longer valid'   
                data['site_url'] = settings.SITE_URL               
                body = requestProcessor.decode_jinga_template(request,'website/accounts/expired_reset_password_key.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/expired_reset_password_key.js', data, '')
                        
                                
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            dajax.script(script)    
            
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'reset_password_submit'):
            data = {}
            form_name = 'form_reset_password'
            
            reset_password_key = requestProcessor.getParameter('reset_password_key')
            data['password'] = requestProcessor.getParameter('password')
            data['verify_password'] = requestProcessor.getParameter('verify_password')
            data['reset_password_key'] = reset_password_key            
            error_message = validate_reset_password_form_data(data, form_name)  

            if len(error_message) == 0:           
                user_details = UserDetail.objects.filter(reset_password_key__exact=reset_password_key)
                if user_details:
                    user_detail = user_details[0]
                    user = User.objects.get(id=user_detail.user_id)
                    if user:
                        user.set_password(data['password'])
                        user.is_active = 1                        
                        user.save()
                        
                        user_detail.reset_password_key = ''
                        user_detail.save()
                        
                        user = authenticate(username=user.username, password=data['password'])
                        if user is not None:
                            if user.is_active:
                                login(request, user)
                                dajax.script('jQuery.fancybox.close();')  
                                add_system_message(request, 'success_reset_password')
                                dajax.script("window.location.href='"+settings.SITE_URL+"';")
                                return HttpResponse(dajax.json()) 
                            else:
                                error_message[form_name+'_fail_reason'] = 'Disabled account'  
                        else:
                            error_message[form_name+'_fail_reason'] = 'Invalid login'  
                    else:
                        error_message[form_name+'_fail_reason'] = 'The reset password key is no longer valid'                          
                else:
                    error_message[form_name+'_fail_reason'] = 'The reset password key is no longer valid'                      
                        
            
            if len(error_message) > 0:
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
               
                body = requestProcessor.decode_jinga_template(request,'website/accounts/reset_password.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/accounts/reset_password.js', data, '')                         
            
            dajax.assign('#fancyboxformDiv','innerHTML', body)            
            dajax.script(script)                
            return HttpResponse(dajax.json())   
        
        #default response for all ajax
        return HttpResponse(dajax.json()) 
     
    data['reset_password_key'] = reset_password_key
    data['action_key'] = 'reset_password'
    return requestProcessor.render_to_response(request,'website/home.html', data, '')        

        

def decode_template(t, data):
    tp = get_template(t)
    c = Context(data)
    body = tp.render(c)
    return body
    

def decode_jinga_template(self, request, filename, context={},mimetype=''):
    template_dirs = settings.TEMPLATE_DIRS
    if mimetype == '':
        mimetype = settings.DEFAULT_CONTENT_TYPE
    env = Environment(loader=FileSystemLoader(template_dirs),
                      extensions=[CompressorExtension])
        
    request_context = RequestContext(request, context)
    csrf = request_context.get('csrf_token')

    context['csrf_token'] = csrf
    template = env.get_template(filename)
    rendered = template.render(**context)        
        
    return rendered


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




