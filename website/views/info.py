from datetime import datetime
import math
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.views.decorators import csrf
from django.contrib.localflavor.us.us_states import US_STATES
from dajax.core import Dajax
from django.conf import settings 
from django.core.mail.message import EmailMessage
from django.shortcuts import render
from django.shortcuts import render_to_response
from website.utils.httpUtil import HttpRequestProcessor
from website.utils.mathUtil import MathUtil

from website.utils.messageUtil import MessageUtil

from website.models import Jurisdiction, UserDetail, OrganizationMember
from website.models import UserDetail, OrganizationMember, news
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message

def states(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    
    state_all = US_STATES
    items_per_column = math.ceil(float(len(state_all)) / settings.PAGE_COLUMNS)
    
    columns = []
    count = 0
    column = []
    for state_obj in state_all:
        column.append(state_obj)
        count += 1
        if count >= items_per_column:
            columns.append(column)
            column = []
            count = 0
    if count > 0: #if there's remaining items in last column
        columns.append(column)
    data['columns'] = columns
    
    return requestProcessor.render_to_response(request,'website/states.html', data, '') 

def state_jurisdictions(request, abbreviation):
    data = { 'groups': [],
             'state_name': dict(US_STATES)[abbreviation] }
    requestProcessor = HttpRequestProcessor(request)
    jurisdiction_type_groups = [{ 'name': 'State',
                                  'ids': ['S'],
                                  'label': 'State Locations' },
                                { 'name': 'County',
                                  'ids': ['CO', 'SC', 'CONP', 'CC'],
                                  'label': 'County Locations' },
                                { 'name': 'County Field Offices',
                                  'ids': ['SCFO'],
                                  'label': 'County Field Offices' },
                                { 'name': 'Cities',
                                  'ids': ['CI', 'CINP', 'IC'],
                                  'label': 'City Locations'},
                                { 'name': 'Unincorporated',
                                  'ids': ['U'],
                                  'label': 'Unincorporated Locations' }]
    any_exist = False
    for group in jurisdiction_type_groups:
        jurisdictions = Jurisdiction.objects.filter(state = abbreviation,
                                                    jurisdiction_type__in = group['ids']).order_by('name')
        if len(jurisdictions) > 0:
            any_exist = True
            items_per_column = int(math.ceil(float(len(jurisdictions)) / settings.PAGE_COLUMNS))
            group['columns'] = [jurisdictions[i:i+items_per_column] for i in xrange(0, len(jurisdictions), items_per_column)]
            data['groups'].append(group)
    data['any_exist'] = any_exist
    return requestProcessor.render_to_response(request, 'website/site_map_state.html', data, '')

def site_map(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request, 'website/site_map.html', {}, '') 

def get_info(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    dajax = Dajax()
          
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        if (ajax == 'privacy_policy'):
            body = requestProcessor.decode_jinga_template(request,'website/info/privacy_policy_modal.html', data, '') 
            #dajax.assign('#main_content','innerHTML', body)    
            dajax.assign('#fancyboxformDiv','innerHTML', body)  
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            return HttpResponse(dajax.json())  
        
    
        if (ajax == 'terms_of_use'):
            body = requestProcessor.decode_jinga_template(request,'website/blocks/text_terms_of_use.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)
            #dajax.assign('#fancyboxformDiv','innerHTML', body)  
            #dajax.script('controller.showModalDialog("#fancyboxformDiv");')    
            return HttpResponse(dajax.json())  
        
        if (ajax == 'doe_grant'):
            body = requestProcessor.decode_jinga_template(request,'website/blocks/text_doe_grant.html', data, '') 
            #dajax.assign('#main_content','innerHTML', body)    
            dajax.assign('#fancyboxformDiv','innerHTML', body)  
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'send_feedback'):
            data = {}     
            data['form_id'] = 'form_send_feedback'            
            
            data['feedback'] = requestProcessor.getParameter('feedback')    
            if data['feedback'] == None:
                data['feedback'] = ''                                                       
             
                body = requestProcessor.decode_jinga_template(request,'website/info/feedback.html', data, '') 
                script = requestProcessor.decode_jinga_template(request, 'website/info/feedback.js', data, '')   
                dajax.assign('#fancyboxformDiv','innerHTML', body)                   
                dajax.script('controller.showModalDialog("#fancyboxformDiv");')
                dajax.script(script)                  

                return HttpResponse(dajax.json())  
            else:           
                data['email'] = settings.FEEDBACK_EMAIL
                data['user'] = request.user
                data['feedback'] = data['feedback'].lstrip('')
                if request.user.is_authenticated():
                    orgmembers = OrganizationMember.objects.filter(user = data['user'], status = 'A')   
                    user_orgs = ''
                    if len(orgmembers) > 0:
                        for orgmember in orgmembers:
                            user_orgs += "," + orgmember.organization.name 
                            
                        user_orgs.lstrip(',')
                        
                    data['user_orgs'] = user_orgs;
                    user_details = UserDetail.objects.filter(user=data['user'])
                    data['user_detail'] = user_details[0]

                    data['first_name'] = data['user'].first_name     
                    data['last_name'] = data['user'].last_name
                    data['username'] = data['user'].username
                    data['title'] = data['user_detail'].title    
                    data['user_email'] = data['user'].email     
                                        
                else:
                    data['first_name'] = requestProcessor.getParameter('first_name')        # required
                    data['last_name'] = requestProcessor.getParameter('last_name')          # required
                    data['user_email'] = requestProcessor.getParameter('email')        # required
                    data['title'] = requestProcessor.getParameter('title')      
                    data['user_orgs'] = requestProcessor.getParameter('org')          # required
                    data['username'] = ''
                
                                                
                email_feedback(data)
                dajax.script('jQuery.fancybox.close();')  
                dajax.script("controller.showMessage('Your feedback has been sent and will be carefully reviewed.', 'success');")                                                        
        
        return HttpResponse(dajax.json())              
    data['current_nav'] = 'home'
    return requestProcessor.render_to_response(request,'website/home.html', data, '')
    
def email_feedback(data): 
    subject = 'SolarPermit feedback from '+ data['user'].username
    tp = get_template('website/emails/feedback.html')
    c = Context(data)
    body = tp.render(c)
    from_mail = data['user_email']
    #print from_mail
    to_mail = [data['email']]
    
    msg = EmailMessage( subject, body, from_mail, to_mail)
    msg.content_subtype = "html"   
    #msg.send()

def news_static(request):
    data = {}
    data['current_nav'] = 'news'

    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data

    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/news.html', data, '')

def news_dynamic(request):
    data = {}
    data['current_nav'] = 'news'
    data['pressreleases'] = news.PressRelease.objects.all().order_by('published')
    data['articles'] = news.Article.objects.all().order_by('published')
    data['events'] = news.Event.objects.all().filter(expiration__gte=datetime.now()).order_by('published')

    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data

    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/news_dynamic.html', data, '')

def about(request):
    data = {}
    data['current_nav'] = 'about'
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/about.html', data, '')

def getting_started_page(request):
    data = {}
    data['current_nav'] = ''
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/getting_started_page.html', data, '')

def privacy_policy(request):
    data = {}
    data['current_nav'] = 'home'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/privacy_policy.html', data, '')

def grant_info(request):
    data = {}
    data['current_nav'] = 'home'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/grant_info.html', data, '')

def information_accuracy_disclaimer(request):
    data = {}
    data['current_nav'] = 'home'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/information_accuracy_disclaimer.html', data, '')

def terms_of_use(request):
    data = {}
    data['current_nav'] = 'home'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/terms_of_use.html', data, '')

def contributions(request):
    data = {}
    data['current_nav'] = 'home'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/contribution.html', data, '')

def upload(request):
    data = {}
    data['current_nav'] = 'upload'
    
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/info/upload.html', data, '')

def page_404(request):
    data = {}
    
    requestProcessor = HttpRequestProcessor(request)
    #return HttpResponseNotFound('<h1>Page not found</h1>')
    print 8898999999999999999999999999
    return requestProcessor.render_to_response(request,'website/info/404.html', data, '')


