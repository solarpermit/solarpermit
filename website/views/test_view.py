from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import get_template
from django.template import Context, RequestContext
from website.utils.httpUtil import HttpRequestProcessor
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render

from django.shortcuts import render_to_response
from website.utils.mathUtil import MathUtil

from website.utils.datetimeUtil import DatetimeHelper
from website.models import Jurisdiction, Organization, OrganizationMember, AnswerReference, Question

from website.utils.messageUtil import MessageUtil
#import pytz
from website.utils.miscUtil import UrlUtil
from website.utils.datetimeUtil import DatetimeHelper
import json
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil



def jurisdiction_browse_by_states(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    
    message_key = requestProcessor.getParameter('message_key')
    messageUtil = MessageUtil(message_key)
    data['system_message_type'] = messageUtil.get_system_message_type()   # optional
    data['system_message_text'] = messageUtil.get_system_message_text()   
            
    data['page_title'] = "Browse Jurisdictions"
      
    #data['state_list'] = US_STATES
    return requestProcessor.render_to_response(request,'website/jurisdictions/jurisdiction_state_browse.html', data, '')
    #return render(request, 'website/jurisdictions/jurisdiction_state_browse.html', data)
    
@csrf.csrf_protect    
def test_newsite(request):
    requestProcessor = HttpRequestProcessor(request)
    dajax = Dajax()
    data = {}
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        if (ajax == 'editmode'):
            formtype = requestProcessor.getParameter('formtype')
            name = requestProcessor.getParameter('name')
            value = requestProcessor.getParameter('value')
            div = requestProcessor.getParameter('div')
            help = requestProcessor.getParameter('help')
            data['formtype'] = formtype
            data['name'] = name
            data['help'] = help
            
            tp = get_template('website/blocks/form_field.html')
            c = Context(data)
            aa = tp.render(c)
            #aa = '<div class="input"><input type="text" id="id_'+name+'" name="'+name+'"></div>'
            #aa += '<label class="helptext">'+help+'</label>'
            dajax.assign('#'+div+'','innerHTML', aa)
            #dajax.script('alert("'+formtype+'")')
            return HttpResponse(dajax.json())
    return render_to_response('website/test_newsite.html', data, context_instance=RequestContext(request))

def test_search(request):
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    
    return requestProcessor.render_to_response(request, 'website/test/test_search.html', data, '')

def test_org(request):
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    
    organizations = Organization.objects.all().order_by('name')[:10]
    data['organizations'] = organizations
    
    return requestProcessor.render_to_response(request, 'website/test/test_organization.html', data, '')

def test_ie(request):
    requestProcessor = HttpRequestProcessor(request)
    dajax = Dajax()
    data = {}
    
    ajax = requestProcessor.getParameter('ajax')
    if ajax != None:    
        if ajax == 'action1':
            dajax.assign('#test_div','innerHTML', ajax)
            return HttpResponse(dajax.json())
            
    return requestProcessor.render_to_response(request, 'website/test/test_ie.html', data, '')

def test_timezone(request):
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    #from django.utils.timezone import localtime
    #bb = pytz.timezone('Asia/Shanghai')
    
    
    omr = Organization.objects.get(id = 43)
    dh = DatetimeHelper(omr.create_datetime, 'Asia/Shanghai')
    data['omr'] = dh.showTimeFormat()
    dh1 = DatetimeHelper(omr.create_datetime)
    data['omr1'] = dh1.showTimeFormat()
    data['omr2'] = dh.showStateTimeFormat('DC')
    
    return requestProcessor.render_to_response(request, 'website/test/test_timezone.html', data, '')

def test_add(request):
    requestProcessor = HttpRequestProcessor(request)
    jurisdiction_id = 131168   
    dajax = Dajax()
    data = {}
    data['jurisdiction_id'] = jurisdiction_id
    answer_reference_class_obj = AnswerReference()
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):    
        if (ajax == 'jurisdiction_website_submit'):     
            data['website'] = requestProcessor.getParameter('website')        

            jurisdiction_website_div = requestProcessor.getParameter('jurisdiction_website_div')   
            
            form_id = 'form_website'                
            question_text = 'website'       
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')             
            process_answer(data, question_text, jurisdiction_id, request.user)                
                
            question_text = "website"
               
            body = get_website_html(form_id, question_text, jurisdiction_id, request)
            dajax.assign('#'+str(jurisdiction_website_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'jurisdiction_email_submit'):     
            data['email'] = requestProcessor.getParameter('email')        

            jurisdiction_website_div = requestProcessor.getParameter('jurisdiction_email_div')   
            
            form_id = 'form_email'                
            question_text = 'website'       
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')             
            process_answer(data, question_text, jurisdiction_id, request.user)                
                
            question_text = "website"
               
            body = get_email_html(form_id, question_text, jurisdiction_id, request)
            dajax.assign('#'+str(jurisdiction_website_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())         
        
        
        
        return HttpResponse(dajax.json())              
    ############### website - start #####################
    data['jurisdiction_website_div'] = 'jurisdiction_website_div'   
    data['form_website'] = 'form_website'   
    question_text = "website"
       
    body = get_website_html(data['form_website'], question_text, jurisdiction_id, request)
     

    
    data['body_website'] = body
    ############# email - start ############################
    data['jurisdiction_phone_div'] = 'jurisdiction_phone_div'   
    data['form_email'] = 'form_email'  
    question_text = "email"
       
    body = get_email_html(data['form_email'], question_text, jurisdiction_id, request)     
        
    
    
    data['body_email'] = body
        
    return requestProcessor.render_to_response(request,'website/test/test_add.html', data, '')    

def test_edit(request):
    requestProcessor = HttpRequestProcessor(request)
    jurisdiction_id = 130732   
    dajax = Dajax()    
    data = {}
    data['jurisdiction_id'] = jurisdiction_id
    answer_reference_class_obj = AnswerReference()
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):    
        if (ajax == 'jurisdiction_website_submit'):     
            data['website'] = requestProcessor.getParameter('website')        

            jurisdiction_website_div = requestProcessor.getParameter('jurisdiction_website_div')   
            
            form_id = 'form_website'                
            question_text = 'website'       
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')             
            process_answer(data, question_text, jurisdiction_id, request.user)                
                
            question_text = "website"
               
            body = get_website_html(form_id, question_text, jurisdiction_id, request, 'edit')
            dajax.assign('#'+str(jurisdiction_website_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'jurisdiction_email_submit'):     
            data['email'] = requestProcessor.getParameter('email')        

            jurisdiction_website_div = requestProcessor.getParameter('jurisdiction_email_div')   
            
            form_id = 'form_email'                
            question_text = 'website'       
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')             
            process_answer(data, question_text, jurisdiction_id, request.user)                
                
            question_text = "website"
               
            body = get_email_html(form_id, question_text, jurisdiction_id, request, 'edit')
            dajax.assign('#'+str(jurisdiction_website_div),'innerHTML', body)
            
            return HttpResponse(dajax.json())         
        
        
        
        return HttpResponse(dajax.json())              
    ############### website - start #####################
    data['jurisdiction_website_div'] = 'jurisdiction_website_div'   
    data['form_website'] = 'form_website'   
    question_text = "website"
       
    body = get_website_html(data['form_website'], question_text, jurisdiction_id, request, 'edit')
     

    
    data['body_website'] = body

        
    return requestProcessor.render_to_response(request,'website/test/test_edit.html', data, '')    

def get_website_html(form_id, question_text, jurisdiction_id, request, mode="add"):
    requestProcessor = HttpRequestProcessor(request)
        
    data_website = {}
    data_website['value_existed'] = 'no'    
    value = ''

    #jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')
    answer_reference_class_obj = AnswerReference()    
    # get current answer.  qa: u don't edit; u add a new record.
    answer = answer_reference_class_obj.get_jurisdiction_data(jurisdiction_id, question_text)
    if answer:
        data_website['value_existed'] = 'yes'        
        for answer_key in answer.keys():
            data_website[answer_key] = answer.get(answer_key)
                       
        urlUtil = UrlUtil(data_website['website'])
        value = "<a href='"+urlUtil.get_href()+"' target='_blank' >"+urlUtil.get_display_website()+"</a>"

    # info for the base_add.html
    data_website['value'] = value  # value to display
    data_website['question_label'] = 'Website'  # field label
    data_website['question_name'] = 'website'    # name used in name and id of form field
    data_website['mode'] = 'individual'         # not sure yet.
       
    # information need to configure the field, this case, a text field.
    data_form = {}               
    data_form['name'] = data_website['question_name']
    if mode == 'edit':
        data_form['value'] = data_website['website']   
    else:
        data_form['value'] = '' 
    data_form['id'] = form_id+'_field_'+ data_form['name'] 
    data_form['class'] = 'required' # for jquery validation
    data_form['style'] = 'width:210px'  # for additional styling
    data_form['attributes'] =  "maxLength='200'"   # may be needed for jquery validation
    data_form['help_text'] = 'Enter the URL of the website'       
    data_form['msg_error'] = ''     # for error msg coming back from server.
    
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/text_field.html', data_form, '') 
    data_website['form_fields'] = form_field
    
    if mode == 'edit':
        body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_edit.html', data_website, '')    
    else:
        body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_add.html', data_website, '')          
    
    return body

def get_email_html(form_id, question_text, jurisdiction_id, request, mode="add"):
    requestProcessor = HttpRequestProcessor(request)
        
    data_email = {}
    data_email['value_existed'] = 'no'    
    value = ''

    #jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')
    answer_reference_class_obj = AnswerReference()    
    # get current answer.  qa: u don't edit; u add a new record.
    answer = answer_reference_class_obj.get_jurisdiction_data(jurisdiction_id, question_text)
    if answer:
        data_email['value_existed'] = 'yes'        
        for answer_key in answer.keys():
            data_email[answer_key] = answer.get(answer_key)
                       
        value = data_email['email']   # can do formatting here

    data_email['value'] = value  # value to display
    data_email['question_label'] = 'Email'  # field label
    data_email['question_name'] = 'email'    # name used in name and id of form field
    data_email['mode'] = 'individual'         # not sure yet.
       
    # information need to configure the field, this case, a text field.
    data_form = {}                
    data_form['name'] = data_email['question_name']
    if mode == 'edit':
        data_form['value'] = data_email['email']   
    else:
        data_form['value'] = ''
    data_form['id'] = form_id+'_field_'+ data_form['name'] 
    data_form['class'] = 'required' # for jquery validation
    data_form['style'] = 'width:210px'
    data_form['attributes'] =  "maxLength='200'"   
    data_form['help_text'] = 'Valid email address please'       
    data_form['msg_error'] = ''
    
    form_field = requestProcessor.decode_jinga_template(request,'website/form_fields/text_field.html', data_form, '') 
    data_email['form_fields'] = form_field
    body = requestProcessor.decode_jinga_template(request,'website/form_fields/base_add.html', data_email, '') 
    
    return body    

    
def process_answer(data, question_text, jurisdiction_id, user):    
    answer = json.dumps(data)   # to convert to json
            
    questions = Question.objects.filter(question__iexact= question_text)
    if questions:
        question = questions[0]    
    else:
        print "no question '' has been set up"
                
    is_callout=0

    jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)            
    answer_reference_class_obj = AnswerReference()
    arcf = answer_reference_class_obj.save_answer(question.id, answer, jurisdiction_id, 'AddRequirement', user, is_callout)

    #contributionHelper = ContributionHelper()  
    #contributionHelper.save_action(category_name, answer, arcf.id, entity_name, request.user.id, jurisdiction_id)         
    
def test_cron_validate_answers(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    field_validation_cycle_util = FieldValidationCycleUtil()      
    field_validation_cycle_util.cron_validate_answers()           
    data = {}
    return requestProcessor.render_to_response(request,'website/test/test_cron_validate_answers.html', data, '')   
     