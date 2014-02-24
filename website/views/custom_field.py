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
#from django.template import Context, RequestContext, Template
from website.models import UserDetail, OrganizationMember, Jurisdiction, Question, AnswerReference, QuestionCategory, Template, TemplateQuestion, ActionCategory
from jinja2 import FileSystemLoader, Environment
import hashlib
from django.conf import settings
import datetime
import json
from website.utils.datetimeUtil import DatetimeHelper

from website.utils.messageUtil import MessageUtil

from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from django.db.models import Max

from website.views.AHJ import get_question_data, get_ahj_top_contributors

def custom_field(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)  
    dajax = Dajax()
    
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        if (ajax == 'create_custom_field'):
            data['form_id'] = 'create_custom_field'      

            data['field_title'] = requestProcessor.getParameter('field_title') 
            data['field_value'] = requestProcessor.getParameter('field_value') 
            data['jurisdiction_id'] = requestProcessor.getParameter('jurisdiction_id') 
            data['category_id'] = requestProcessor.getParameter('category_id')   
            data['current_category'] = requestProcessor.getParameter('current_category')      
            
            if data['field_title'] == None:
                data['field_title'] = ''   
            if data['field_value'] == None:
                data['field_value'] = ''                      
                
            data['jurisdiction'] = Jurisdiction.objects.get(id=data['jurisdiction_id'])

            body = requestProcessor.decode_jinga_template(request,'website/blocks/create_custom_field.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/blocks/create_custom_field.js', data, '')
            dajax.script(script)        
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')

            return HttpResponse(dajax.json())  
        
        if (ajax == 'create_custom_field_submit'):  
            data = {}       
            data['form_id'] = 'create_custom_field'     
            data['field_title'] = requestProcessor.getParameter('field_title') 
            data['field_value'] = requestProcessor.getParameter('field_value') 
            data['jurisdiction_id'] = requestProcessor.getParameter('jurisdiction_id') 
            data['category_id'] = requestProcessor.getParameter('category_id')     
            current_category = requestProcessor.getParameter('current_category')   
            current_questions = requestProcessor.getParameter('current_questions') 
                                                               
            error_message = {}        
            error_message = validate_create_custom_field_form_data(data, data['form_id'])

            if len(error_message) == 0:
                msg_key = data['form_id']+ '_fail_reason'               
                try:
                    jurisdiction = Jurisdiction.objects.get(id=data['jurisdiction_id'])
                    
                    # look up template CF for this jurisdiction
                    templates = Template.objects.filter(jurisdiction=jurisdiction, template_type__iexact='CF', accepted = 1)
                    if len(templates) > 0:
                        template = templates[0]
                    else:
                        template = Template()
                        template.template_type = 'CF'
                        template.name = 'Jurisdiction Custom Field Template'
                        template.jurisdiction_id = data['jurisdiction_id']
                        #template.create_datetime = datetime.datetime.now()
                        template.accepted = 1
                        template.save()
                    # create the question

                    category_obj = QuestionCategory.objects.get(id=data['category_id'])
                    '''
                    questions = Question.objects.filter(category=category_obj, accepted=1).order_by('-display_order')
                    last_question = questions[0]
                    if last_question.display_order == None or last_question.display_order == '':
                        display_order = 0
                    else:
                        display_order = last_question.display_order
                    '''    
                    highest_display_order_obj = Question.objects.filter(category=category_obj, accepted=1).aggregate(Max('display_order'))
                    #print highest_display_order_obj
                    if highest_display_order_obj == None:
                        highest_display_order = 0
                    else:
                        highest_display_order = highest_display_order_obj['display_order__max']
                        
                    question_obj = Question();
                    question_obj.category_id = data['category_id']
                    question_obj.question = data['field_title']
                    question_obj.label = data['field_title']
                    question_obj.form_type = 'CF'
                    question_obj.qtemplate_id = template.id
                    question_obj.accepted = 1
                    question_obj.display_order = int(highest_display_order) + 5
                    #question_obj.create_datetime = datetime.datetime.now()
                    question_obj.creator_id = request.user.id
                    question_obj.save()
                    
                    template_question = TemplateQuestion()
                    template_question.template_id = template.id
                    template_question.question_id = question_obj.id
                    #template_question.create_datetime = datetime.datetime.now()
                    template_question.save()
                    # save the answer
                    data_answer = {}
                    data_answer['value'] = data['field_value']
                    answer = json.dumps(data_answer)   # to convert to json                    
                    is_callout=0           
                    answer_reference_class_obj = AnswerReference()
                    
                    #action_category_objs = ActionCategory.objects.filter(name__iexact='AddRequirement')
                    #action_category_obj = action_category_objs[0]   
                    validation_util_obj = FieldValidationCycleUtil()                    
                    arcf = validation_util_obj.save_answer(question_obj, answer, jurisdiction, 'AddRequirement', request.user, is_callout)
                    
                except Exception, e:
                    data[msg_key] = e.message
                    print e.message
        
            #else:
            if len(error_message) > 0:
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
                    
                    body = requestProcessor.decode_jinga_template(request,'website/blocks/create_custom_field.html', data, '')
                    dajax.assign('#fancyboxformDiv','innerHTML', body)
                    script = requestProcessor.decode_jinga_template(request, 'website/blocks/create_custom_field.js', data, '')
                    dajax.script(script)
            else:
                data_cf = {}
                jurisdiction = Jurisdiction.objects.get(id=data['jurisdiction_id'])
                data_cf['jurisdiction'] = jurisdiction
                template_obj = Template()
                jurisdiction_templates = template_obj.get_jurisdiction_question_templates(jurisdiction)
               
                    
                data_cf['action'] = '/jurisdiction_id/'+str(jurisdiction.id)+'/'+current_category+'/'
                  
                data_cf = get_question_data(request, jurisdiction, question_obj, data)
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_cqa_qa.html', data_cf, '')
                script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_cqa_qa.js' , data, '')
                dajax.script(script)                                                   
            
                dajax.assign('#div_custom_question_content_'+str(data['category_id']),'innerHTML', body)    
                        
                        ######################################################               
                      
                #data['custom_questions'] = custom_questions
                #data['custom_questions'] = {}
                #data['custom_questions'][question_category_obj.id] = custom_questions
                
                #body = requestProcessor.decode_jinga_template(request,'website/blocks/custom_fields.html', data, '')                                   
                #dajax.assign('#custom_fields_'+str(question_category_obj.id),'innerHTML', body)
                dajax.script('jQuery.fancybox.close();')  
                dajax.script("controller.showMessage('Custom field created.', 'success')") 
                dajax.script('controller.updateUrlAnchor("#create_custom_field");')
                
                data = {}
                if current_category == 'all_info':
                    question_categories = QuestionCategory.objects.filter(accepted=1)
                    data['category'] = 'All categories'
                else:
                    question_categories = QuestionCategory.objects.filter(name__iexact=category_obj.name)
                    data['category'] = category_obj.name

                #data['category'] = question_obj.category.name
                data['jurisdiction'] = jurisdiction
                
                data['top_contributors'] = get_ahj_top_contributors(jurisdiction, current_category)  
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_top_contributors.html', data, '')   
                dajax.assign('#top-contributor','innerHTML', body)                           
                
            return HttpResponse(dajax.json())  

    #note: this non-ajax case will not work since we have not included create_account.js, but it is not used
    return requestProcessor.render_to_response(request,'website/blocks/create_custom_field.html', data, '')      
    
def validate_create_custom_field_form_data(data, form_id):
    message = {}
    return message
