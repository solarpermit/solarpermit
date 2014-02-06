import re
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.localflavor.us.us_states import US_STATES
from django.contrib import messages
from django.template.loader import get_template as django_get_template
from django.template import Context, RequestContext
from website.utils.httpUtil import HttpRequestProcessor
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render

from django.shortcuts import render_to_response, redirect
from website.utils.mathUtil import MathUtil
from website.utils.geoHelper import GeoHelper
from website.models import Jurisdiction, Zipcode, UserSearch, Question, AnswerReference, AnswerAttachment, OrganizationMember, QuestionCategory, Comment, UserCommentView, Template, TemplateQuestion, ActionCategory, JurisdictionContributor, Action, UserDetail, OrganizationMember
from website.models import View, ViewQuestions, ViewOrgs
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from website.utils.miscUtil import UrlUtil
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.datetimeUtil import DatetimeHelper
from django.contrib.auth.models import User
import json
import datetime
import operator
from django.db import connections, transaction

from BeautifulSoup import BeautifulSoup
from website.utils.fileUploader import qqFileUploader

JURISDICTION_PAGE_SIZE = 30 #page size for endless scroll
    
def jurisdiction_comment(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    data = {}
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    comments_changed = requestProcessor.getParameter('comments_changed')
    if comments_changed == 'yes':
        data['comments_changed'] = 'yes'
    else:
        data['comments_changed'] = 'no'
    if (ajax != None):
        if ajax == 'open_jurisdiction_comment':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            jid = requestProcessor.getParameter('jurisdiction_id')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jid)
            except:
                jurisdiction = None
            comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, parent_comment__isnull = True).order_by('-create_datetime')
            
           
            userviews = UserCommentView.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, user = user)
            
            temp_comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).order_by('-create_datetime')
            last_comment = None
            if len(temp_comments) > 0 :
                last_comment = temp_comments[0]
            
            has_userview = False
            if len(userviews) > 0:
                userview = userviews[0]
                if userview.last_comment != None:
                    data['userview_last_comment'] = userview.last_comment.id
                    data['userview'] = userviews[0]
                    userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                    userview.last_comment = last_comment
                    userview.view_datetime = datetime.datetime.now()
                    userview.save()
                    has_userview = True
            if has_userview == False:
                userview = None
                data['userview'] = userview
                data['userview_last_comment'] = 0
                userview = UserCommentView()
                userview.user = user
                userview.jurisdiction = jurisdiction
                userview.entity_name = entity_name
                userview.entity_id = entity_id
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            
            af = AnswerReference.objects.get(id = entity_id)
            validation_util_obj = FieldValidationCycleUtil()
            old_data = {}
            old_data['jurisdiction_type'] = data['jurisdiction_type'] = af.jurisdiction.get_jurisdiction_type()              
            old_data['jurisdiction_id'] = data['jurisdiction_id'] = af.jurisdiction.id   
            old_data['jurisdiction'] = data['jurisdiction'] = af.jurisdiction 
            old_data['this_question'] = data['this_question'] = af.question
            
            category_name = 'VoteRequirement' 
            vote_info = validation_util_obj.get_jurisdiction_voting_info_by_category(category_name, af.jurisdiction, af.question.category, af.question)
            terminology = validation_util_obj.get_terminology(af.question)  
            #question_content = validation_util_obj.get_AHJ_question_data(request, update.jurisdiction, update.question, data)  
            question_content = validation_util_obj.get_authenticated_displayed_content(request, af.jurisdiction, af.question, vote_info, [af], terminology)
            for key in question_content.keys():
                data[key] = question_content.get(key) 
            
            data['answer'] = af
            #data['answer_text'] = aa.get_formatted_value(af.value, af.question)
            answer_text = requestProcessor.decode_jinga_template(request,'website/blocks/display_answer.html', data, '')
            data['answer_text'] = answer_text            
            data['jurisdiction'] = jurisdiction
            label = af.question.question
            if len(af.question.question) > 75:
                label = af.question.question[:78]+ '...'
            data['label'] = label
            
            data['commnets'] = comments
            
            others_afs = AnswerReference.objects.filter(jurisdiction = jurisdiction, question = af.question, approval_status='A').exclude(id = entity_id).order_by('-create_datetime')
            if len(others_afs) > 0 :
                old_answer = others_afs[0]
                if old_answer.id < af.id:
                    data['old_answer'] = old_answer
                    old_question_content = validation_util_obj.get_authenticated_displayed_content(request, old_answer.jurisdiction, old_answer.question, vote_info, [old_answer], terminology)
                    for key in old_question_content.keys():
                        old_data[key] = old_question_content.get(key)
                    #data['old_answer_text'] = aa.get_formatted_value(old_answer.value, old_answer.question)
                    old_answer_text = requestProcessor.decode_jinga_template(request,'website/blocks/display_answer.html', old_data, '')
                    data['old_answer_text'] = old_answer_text
                else:
                    data['old_answer'] = None
                    data['old_answer_text'] = ''
            else:
                data['old_answer'] = None
                data['old_answer_text'] = ''
  
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js' , data, '')
            dajax.script(script)
            script = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.js' , data, '')
            dajax.script(script)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            dajax.script('controller.updateUrlAnchor("#view_comment");')
        
        if ajax =='create_jurisdiction_comment':
            answer_id = requestProcessor.getParameter('answer_id')
            jid = requestProcessor.getParameter('jurisdiction_id')
            comment_type = 'JC'
            
            data['answer_id'] = answer_id
            data['jurisdiction_id'] = jid
            data['comment_type'] = comment_type
            data['parent_comment'] = ''
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/create_comment.html', data, '')
            script =  requestProcessor.decode_jinga_template(request,'website/jurisdictions/create_comment.js' , data, '')
            dajax.assign('#secondDialogDiv','innerHTML', body) 
            dajax.script(script)
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
        
        if ajax =='comment_create_submit':
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')
            comment_type = requestProcessor.getParameter('comment_type')
            comment_text = requestProcessor.getParameter('comment')
            parent_comment = requestProcessor.getParameter('parent_comment')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jurisdiction_id)
            except:
                jurisdiction = None
                
            comment = Comment()
            comment.jurisdiction = jurisdiction
            if entity_name != 'None': 
                comment.entity_name = entity_name
            else:
                entity_name = None
            if entity_id != 'None':
                comment.entity_id = entity_id
            else:
                entity_id = None
            comment.user = user
            comment.comment_type = comment_type
            comment.comment = comment_text
            if parent_comment != '':
                parent = Comment.objects.get(id = parent_comment)
                comment.parent_comment = parent
            comment.save()
            
            userviews = UserCommentView.objects.filter(user = user, jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id)
            if userviews:
                userview = userviews[0]
                userview.last_comment = comment
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            
            
            dajax.script('controller.closeSecondDialog();')
            dajax.script('controller.postRequest("/jurisdiction_comment/", {ajax: "open_jurisdiction_comment", jurisdiction_id:'+str(jurisdiction_id)+', entity_id: "'+str(entity_id)+'", entity_name: "'+str(entity_name)+'", comments_changed: "yes"});')

            data = {}
            answers = AnswerReference.objects.filter(id=entity_id)
            data['answers_comments'] = get_answers_comments( jurisdiction, answers, user)

            dajax.add_data(data, 'process_ahj_comments')
            dajax.script('controller.updateUrlAnchor("#add_comment");')               
                
        if ajax =='reply_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid)            
            data['comment'] = comment
            body = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.html', data, '')
            script = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.js' , data, '')
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            dajax.script(script)
            
        
        if ajax == 'cancel_reply':
            cid = requestProcessor.getParameter('cid')
            body = '<a class="smallbutton commentReplayBtn" data-cid="'+cid+'" href="#">Reply</a><a class="smallbutton commentFlagBtn" data-cid="'+cid+'" href="#">Flag</a>'
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            script = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.js' , data, '')
            dajax.script(script)
        if ajax == 'flag_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid) 
            comment.approval_status = 'F'
            comment.save()
            
            af = AnswerReference.objects.get(id = comment.entity_id)
            to_mail = [django_settings.ADMIN_EMAIL_ADDRESS]
            data['comment'] = comment
            data['user'] = user
            data['question'] = af.question.question
            
            data['site_url'] = django_settings.SITE_URL
            data['requestProcessor'] = requestProcessor
            data['request'] = request
            send_email(data, to_mail)
            
            dajax.assign('#comment_'+str(cid), 'innerHTML', '<p>This comment had been flagged as inappropriate and is hidden pending review.</p>')
        
        if ajax == 'show_old_comments':
            entity_id = requestProcessor.getParameter('answer_id')
            entity_name = 'AnswerReference'
            jid = requestProcessor.getParameter('jurisdiction_id')
            try:
                jurisdiction = Jurisdiction.objects.get(id = jid)
            except:
                jurisdiction = None
            data['jurisdiction'] = jurisdiction
            comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, parent_comment__isnull = True).order_by('-create_datetime')
            
            userviews = UserCommentView.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id, user = user)
            
            temp_comments = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).order_by('-create_datetime')
            last_comment = None
            if len(temp_comments) > 0 :
                last_comment = temp_comments[0]
            if len(userviews) > 0:
                userview = userviews[0]
                data['userview'] = userview
                data['userview_last_comment'] = userview.last_comment.id
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            else:
                userview = None
                data['userview'] = userview
                data['userview_last_comment'] = 0
                userview = UserCommentView()
                userview.user = user
                userview.jurisdiction = jurisdiction
                userview.entity_name = entity_name
                userview.entity_id = entity_id
                userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
                userview.last_comment = last_comment
                userview.view_datetime = datetime.datetime.now()
                userview.save()
            data['commnets'] = comments
            
            body = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.html', data, '')
            dajax.assign('#old_list ul', 'innerHTML', body)
            scripts = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.js' , data, '')
            dajax.script(script)
            dajax.assign('#show_commnet_div', 'innerHTML', '<a id="id_a_hide" href="#"><img src="/media/images/arrow_down.png" style="vertical-align:middle;" alt="Hide old comments"> Hide old comments </a>')
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js' , data, '')
            dajax.script(script)
            
        return HttpResponse(dajax.json())
    return

def send_email(data, to_mail, subject='Flag Comment', template='flag_comment.html'): 
    #tp = django_get_template('website/emails/' + template)
    #c = Context(data)
    #body = tp.render(c)
    
    requestProcessor = data['requestProcessor']
    request = data['request']
    body = requestProcessor.decode_jinga_template(request, 'website/emails/' + template, data, '')

    from_mail = django_settings.DEFAULT_FROM_EMAIL

    msg = EmailMessage( subject, body, from_mail, to_mail)
    msg.content_subtype = "html"   
    msg.send()
    
def view_sc_AHJ(request, jurisdiction):
    requestProcessor = HttpRequestProcessor(request)   
             
    data = {}
    data['home'] = '/'     
    data['state'] = jurisdiction.state
    data['state_long_name'] = dict(US_STATES)[data['state']]  
    
    data['city'] = jurisdiction.city   
    data['jurisdiction_type'] = jurisdiction.get_jurisdiction_type()              
    data['jurisdiction_id'] = jurisdiction.id   
    data['jurisdiction'] = jurisdiction      
    
          
  
    data['jurisdiction'] = jurisdiction
    scfo_jurisdictions = Jurisdiction.objects.filter(parent=jurisdiction, jurisdiction_type__iexact='SCFO')
    data['scfo_jurisdictions'] = scfo_jurisdictions
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_sc.html', data, '')     
    
def view_unincorporated_AHJ(request, jurisdiction):
    requestProcessor = HttpRequestProcessor(request)   
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    user = request.user
             
    data = {}
    data['authenticated_page_message'] = ''
    data['unauthenticated_page_message']= "Please log in to add or view comments."
    
    data['home'] = '/'     
    data['state'] = jurisdiction.state
    data['state_long_name'] = dict(US_STATES)[data['state']]  
    
    data['city'] = jurisdiction.city   
    data['jurisdiction_type'] = jurisdiction.get_jurisdiction_type()              
    data['jurisdiction_id'] = jurisdiction.id   
    data['jurisdiction'] = jurisdiction      
    data['user'] = user    
    parent_jurisdiction = None
    try:
        parent_jurisdiction = jurisdiction.parent
        if parent_jurisdiction != None:
            if parent_jurisdiction.jurisdiction_type == 'CINP' or parent_jurisdiction.jurisdiction_type == 'CONP':
                parent_jurisdiction = parent_jurisdiction.parent
    except:
        parent_jurisdiction = None
        
    data['parent_jurisdiction'] = parent_jurisdiction
    comments = comments = Comment.objects.filter(jurisdiction = jurisdiction, parent_comment__isnull = True).order_by('-create_datetime')
    data['commnets'] = comments
    data['userview_last_comment'] = 0
    if ajax != None:
        if ajax == 'create_jurisdiction_ucomment':
            data['comment_type'] = 'JC'
            data['parent_comment'] = ''
            body = requestProcessor.decode_jinga_template(request,'website/blocks/create_ucomment.html', data, '') 
            dajax.assign('#secondDialogDiv','innerHTML', body) 
            script = requestProcessor.decode_jinga_template(request,'website/blocks/create_ucomment.js' , data, '')
            dajax.script(script)
            dajax.script('controller.showSecondDialog("#secondDialogDiv", {top: 185});')
            
        if ajax == 'ucomment_create_submit':
            comment_text = requestProcessor.getParameter('comment')
            parent_comment = requestProcessor.getParameter('parent_comment')
            comment = Comment()
            comment.jurisdiction = jurisdiction
            comment.user = user
            comment.comment_type = 'JC'
            comment.comment = comment_text        
            if parent_comment != '':
                parent = Comment.objects.get(id = parent_comment)
                comment.parent_comment = parent
            comment.save()
            dajax.script('controller.closeSecondDialog();')
            comments = comments = Comment.objects.filter(jurisdiction = jurisdiction, parent_comment__isnull = True).order_by('-create_datetime')
            data['commnets'] = comments
            body = requestProcessor.decode_jinga_template(request,'website/blocks/ucomment_list.html', data, '') 
            script = requestProcessor.decode_jinga_template(request,'website/blocks/ucomment_list.js' , data, '')
            dajax.assign('.ul-level-1','innerHTML', body) 
            dajax.script(script)
        
        if ajax == 'cancel_reply':
            cid = requestProcessor.getParameter('cid')
            body = '<a class="smallbutton ucommentReplyBtn" data-cid="'+cid+'" href="#">Reply</a><a class="smallbutton ucommentDeleteBtn" data-cid="'+cid+'" href="#">Delete</a><a class="smallbutton ucommentFlagBtn" data-cid="'+cid+'" href="#">Flag</a>'
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            script = requestProcessor.decode_jinga_template(request,'website/blocks/ucomment_list.js' , data, '')
            dajax.script(script)
        
        if ajax =='reply_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid)            
            data['comment'] = comment
            body = requestProcessor.decode_jinga_template(request,'website/blocks/reply_ucomment_form.html', data, '')
            script = requestProcessor.decode_jinga_template(request,'website/blocks/reply_ucomment_form.js' , data, '')
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            dajax.script(script)

        if ajax == 'flag_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid) 
            comment.approval_status = 'F'
            comment.save()
            
            to_mail = [django_settings.ADMIN_EMAIL_ADDRESS]
            data['comment'] = comment
            data['user'] = user
 
            data['site_url'] = django_settings.SITE_URL
            data['requestProcessor'] = requestProcessor
            data['request'] = request
            send_email(data, to_mail, subject='Flag Comment', template='flag_ucomment.html')
            
            dajax.assign('#comment_'+str(cid), 'innerHTML', '<p>This comment had been flagged as inappropriate and is hidden pending review.</p>')
        if ajax == 'remove_comment':
            cid = requestProcessor.getParameter('cid')
            try:
                comment = Comment.objects.get(id = cid)
                cid = comment.id
            except:
                cid = 0
            if cid != 0:
                try:
                    for i in range(0, 4):
                        delete_comment(comment)
                except:
                    pass
            dajax.script('$("#li-'+str(cid)+'").remove();')
            dajax.script("controller.showMessage('The comment(s) have been deleted.', 'success');") 
        return HttpResponse(dajax.json())
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_unincorporated.html', data, '')     
    
def delete_comment(comment):
    comments = Comment.objects.filter(parent_comment = comment)
    if len(comments) > 0:
        for c in comments:
            delete_comment(c)
    else:
        comment.delete()

    
def view_AHJ_by_name(request, name, category='all_info'):

    mathUtil = MathUtil()
    if mathUtil.is_number(name):
        try:
            jurisdictions = Jurisdiction.objects.filter(id=name)
        except:
            raise Http404
    else:
        jurisdictions = Jurisdiction.objects.filter(name_for_url__iexact=name)

    if len(jurisdictions) >= 1:
        jurisdiction = jurisdictions[0]
        id = jurisdiction.id
        
        if jurisdiction.jurisdiction_type == 'U' or jurisdiction.jurisdiction_type == 'CONP' or jurisdiction.jurisdiction_type == 'CINP':
            return view_unincorporated_AHJ(request, jurisdiction)
        elif jurisdiction.jurisdiction_type == 'SC':
            return view_sc_AHJ(request, jurisdiction)
        else:
            user = request.user
            ## the following to make sure the user has access to the view from the url
            if category != 'all_info':
                question_categories = QuestionCategory.objects.filter(name__iexact=category, accepted=1)    
                if len(question_categories) == 0: # not a question category, could be a view or a favorites or a quirks
                    if category == 'favorite_fields':
                        if user.is_authenticated():
                            pass    
                        else:   
                            return redirect('/')   # faorite fields needs login => home
                    elif category == 'quirks':
                        pass
                    elif category == 'attachments':
                        pass                    
                    else:   # views
                        if user.is_authenticated():
                            login_user = User.objects.get(id=user.id)
                            if login_user.is_staff or login_user.is_superuser or ('accessible_views' in request.session and category in request.session['accessible_views']):
                                pass  # logged in user, he is either a staff or superuser, or this user has access to the view per his organization membership
                            else:
                                return redirect('/jurisdiction/'+str(jurisdiction.name_for_url)+'/')   # in the case of a non-question category, dump him at the general category    
                        else:
                            return redirect('/') 
                        
            requestProcessor = HttpRequestProcessor(request)  
            layout = requestProcessor.getParameter('layout')       
            if layout == 'print':
                return view_AHJ_cqa_print(request, jurisdiction, category)   
            else:
                return view_AHJ_cqa(request, jurisdiction, category)
    else:
        raise Http404
    
    return redirect('/')

def view_AHJ_cqa_print(request, jurisdiction, category='all_info'):
    data= {}
    user = request.user
    requestProcessor = HttpRequestProcessor(request)  
    validation_util_obj = FieldValidationCycleUtil()
    show_google_map = False
    
    if category != 'favorite_fields' and category != 'quirks':
        if 'empty_data_fields_hidden' not in request.session:
            empty_data_fields_hidden = 1
        else:
            empty_data_fields_hidden = request.session['empty_data_fields_hidden']
    else:
        empty_data_fields_hidden = 0
    
    (question_ids, view) = get_questions_in_category(user, jurisdiction, category)
    data['view'] = view
    records = get_ahj_data(jurisdiction, category, empty_data_fields_hidden, user, question_ids)

    answers_contents = {}
    questions_have_answers = {}
    questions_terminology = {}
    for rec in records:
        if rec['question_id'] not in questions_have_answers:
            questions_have_answers[rec['question_id']] = False
                
        if rec['question_id'] not in questions_terminology:
            questions_terminology[rec['question_id']] = Question().get_question_terminology(rec['question_id'])
                 
        if rec['question_id'] == 4:
            show_google_map = True
            
        if rec['id'] != None:                            
            if rec['question_id'] == 16:
                fee_info = validation_util_obj.process_fee_structure(json.loads(rec['value']) )                   
                for key in fee_info.keys():
                    data[key] = fee_info.get(key)               
        
            answer_content = json.loads(rec['value'])    
            answers_contents[rec['id']] = answer_content                  
              
            questions_have_answers[rec['question_id']] = True 
                    
    if category == 'all_info' or show_google_map == True:
        data['show_google_map'] = show_google_map
        ################# get the correct address for google map #################### 
        question = Question.objects.get(id=4)      
        data['str_address'] = question.get_addresses_for_map(jurisdiction)  
        data['google_api_key'] = django_settings.GOOGLE_API_KEY    
        
    data['cqa'] = records
    data['questions_terminology'] = questions_terminology
    data['questions_have_answers'] = questions_have_answers
    data['answers_contents'] = answers_contents
    data['user'] = user    
    data['jurisdiction'] = jurisdiction        
                
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_cqa_print.html', data, '')     

def view_AHJ_cqa(request, jurisdiction, category='all_info'):
    #print "at beginning of view view_AHJ_data :: " + str(datetime.datetime.now().strftime("%d %b %Y %I:%M:%S .%f %p")) 
    dajax = Dajax()   
    validation_util_obj = FieldValidationCycleUtil()      
    requestProcessor = HttpRequestProcessor(request)    
    user = request.user
         
    data = {}
    data['time'] = []

    data['category'] = category
    if category == 'all_info':
        data['category_name'] = 'All Categories'
    else:
        data['category_name'] = category

    empty_data_fields_hidden = True
    if category != 'favorite_fields' and category != 'quirks':
        if jurisdiction.last_contributed_by == None:
            empty_data_fields_hidden = False
        else:
            if 'empty_data_fields_hidden' in request.session:
                empty_data_fields_hidden = request.session['empty_data_fields_hidden']
    else:
        empty_data_fields_hidden = False
    param = requestProcessor.getParameter('empty_data_fields_hidden')
    if param != None:
        empty_data_fields_hidden = param == "1"
    data['empty_data_fields_hidden'] = 1 if empty_data_fields_hidden else 0

    ajax = requestProcessor.getParameter('ajax')
    if ajax != None and ajax != '':
        if (ajax == 'get_ahj_answers_headings'):
            questions_answers = {}
            jurisdiction_templates = get_jurisdiction_templates(jurisdiction)        
            jurisdiction_questions = get_jurisdiction_questions(jurisdiction, jurisdiction_templates, user, category)
            for question in jurisdiction_questions:
                questions_answers[question.id] = []        
            jurisdiction_answers = get_jurisdiction_answers(jurisdiction, jurisdiction_templates, jurisdiction_questions) 
            for answer in jurisdiction_answers:
                questions_answers[answer.question.id].append(answer)
                
            data['answers_headings'] = get_questions_answers_headings(questions_answers, user)
            print data['answers_headings']
            dajax.add_data(data, 'process_ahj_answers_headings')
            return HttpResponse(dajax.json())   
        
        if (ajax == 'get_ahj_questions_actions'):
            data['questions_actions'] = get_ahj_actions( jurisdiction, user)
             
            dajax.add_data(data, 'process_ahj_actions')
            return HttpResponse(dajax.json())  
            
        if (ajax == 'get_ahj_questions_messages'):
            jurisdiction_templates = get_jurisdiction_templates(jurisdiction)
            jurisdiction_questions = get_jurisdiction_questions(jurisdiction, jurisdiction_templates, user, category)        
            jurisdiction_answers = get_jurisdiction_answers(jurisdiction, jurisdiction_templates, jurisdiction_questions) 
            answer_question_ids = jurisdiction_answers.values_list('question_id').distinct()
            questions_with_answers = jurisdiction_questions.filter(id__in=answer_question_ids)  
            
            data['questions_messages'] = get_ahj_questions_messages(questions_with_answers, jurisdiction_answers, user)      
    
            dajax.add_data(data, 'process_ahj_questions_messages')
            return HttpResponse(dajax.json())  
        
        if (ajax == 'get_ahj_answers_validation_history_and_comments'):
            jurisdiction_templates = get_jurisdiction_templates(jurisdiction)        
            jurisdiction_questions = get_jurisdiction_questions(jurisdiction, jurisdiction_templates, user, category)        
            jurisdiction_answers = get_jurisdiction_answers(jurisdiction, jurisdiction_templates, jurisdiction_questions) 
    
            data['answers_comments'] = get_answers_comments( jurisdiction, jurisdiction_answers, user)
    
            dajax.add_data(data, 'process_ahj_comments')
            return HttpResponse(dajax.json())      
        
        if (ajax == 'get_ahj_ahj_top_contributors'):              
                    
            data_top_contributors = {}          
            data_top_contributors['top_contributors'] = get_ahj_top_contributors(jurisdiction, category)
            data['top_contributors'] = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_top_contributors.html', data_top_contributors, '')  
             
            dajax.add_data(data, 'process_ahj_top_contributors')
            return HttpResponse(dajax.json())      
        
        
        if (ajax == 'get_ahj_answers_attachments'):    
            data['answers_attachments'] = get_ahj_answers_attachments(jurisdiction)
    
            dajax.add_data(data, 'process_ahj_answers_attachments')
            return HttpResponse(dajax.json())      
    
        if (ajax == 'get_ahj_num_quirks_favorites'):        
            view_questions_obj = ViewQuestions()
            quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)
            
            data['quirk_number_of_questions'] = 0    
            if 'view_id' in quirks:
                data['quirk_number_of_questions'] = len(quirks['view_questions']) 
                
            data['user_number_of_favorite_fields'] = 0    
            user_obj = User.objects.get(id=user.id)
            if user_obj != None:
                user_favorite_fields = view_questions_obj.get_user_favorite_fields(user_obj)
                if 'view_id' in user_favorite_fields:
                    data['view_id'] = user_favorite_fields['view_id']
                    data['user_number_of_favorite_fields'] = len(user_favorite_fields['view_questions'])               
                    
            dajax.add_data(data, 'process_ahj_qirks_user_favorites')
         
            return HttpResponse(dajax.json())
        
        if (ajax == 'get_ahj_answers_votes'):
            jurisdiction_templates = get_jurisdiction_templates(jurisdiction)     
            #print 'xxxxxxxx'   
            jurisdiction_questions = get_jurisdiction_questions(jurisdiction, jurisdiction_templates, user, category)        
            #print 'yyyyyyyyy'
            jurisdiction_answers = get_jurisdiction_answers(jurisdiction, jurisdiction_templates, jurisdiction_questions) 
            #print 'zzzzzzzzz'
            category_name = 'VoteRequirement'          
            answer_ids = []
            for answer in jurisdiction_answers:
                answer_ids.append(answer.id)
            data['answers_votes'] = get_answer_voting_info(category_name, jurisdiction, user, answer_ids)
            #print 'aaaaaaaaaaaa'
            dajax.add_data(data, 'process_ahj_answers_votes')
            return HttpResponse(dajax.json())  
        
        if (ajax == 'get_add_form'):  
            data['mode'] = 'add'
            data['user'] = user        
            data['jurisdiction'] = jurisdiction         
            question_id = requestProcessor.getParameter('question_id')               
            data['unique_key'] = data['mode'] + str(question_id)
            data['form_field'] = {}
            question = Question.objects.get(id=question_id)
            form_field_data = validation_util_obj.get_form_field_data(jurisdiction, question)
                
            for key in form_field_data:
                data[key] = form_field_data[key]        
    
            data['default_values'] = {}
            if question.default_value != None and question.default_value != '':
                answer = json.loads(question.default_value) 
                for key in answer:
                    data[key] = str(answer[key])     
                    
            data['city'] =  jurisdiction.city
            data['state'] = jurisdiction.state           
            if 'question_template' in data and data['question_template'] != None and data['question_template'] != '':
                if form_field_data['question_id'] == 16:
                    data['fee_answer'] = answer
                    fee_info = validation_util_obj.process_fee_structure(answer)
                    for key in fee_info.keys():
                        data[key] = fee_info.get(key)    
                                      
                
                body = requestProcessor.decode_jinga_template(request,'website/form_fields/'+data['question_template'], data, '')    
            else:
                body = ''
     
            dajax.assign('#qa_'+str(question_id) + '_fields','innerHTML', body)
    
            #if 'js' in data and data['js'] != None and data['js'] != '':
            for js in data['js']:
                script ="var disable_pre_validation = false;" #set open pre validation by default, we can overwrite it under each field js file. 
                script += requestProcessor.decode_jinga_template(request, "website/form_fields/"+js, data, '')
                script +=";if ((!disable_pre_validation)&&!$('#form_"+question_id+"').checkValidWithNoError({formValidCallback:function(el){$('#save_"+question_id+"').removeAttr('disabled').removeClass('disabled');},formNotValidCallback:function(el){$('#save_"+question_id+"').attr('disabled','disabled').addClass('disabled');;}})){$('#save_"+question_id+"').attr('disabled','disabled').addClass('disabled');};"
                dajax.script(script)
    
            if question.support_attachments == 1:
                script = requestProcessor.decode_jinga_template(request, "website/form_fields/file_uploading.js", data, '')
                dajax.script(script)
                                    
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'get_edit_form'):
            data['mode'] = 'edit'
            answer_id = requestProcessor.getParameter('answer_id')    
            data['unique_key'] = data['mode'] + str(answer_id)       
            answer_for_edit = AnswerReference.objects.get(id=answer_id)       
            question = answer_for_edit.question
            data['jurisdiction'] = answer_for_edit.jurisdiction
            
            data['values'] = {} 
            form_field_data = validation_util_obj.get_form_field_data(jurisdiction, question)
            for key in form_field_data:
                data[key] = form_field_data[key]    
                    
            data['values'] = {}                
            answer = json.loads(answer_for_edit.value) 
            for key in answer:
                data[key] = answer[key]  
                             
            data['answer_id'] = answer_id   
            if 'question_template' in data and data['question_template'] != None and data['question_template'] != '':
                if form_field_data['question_id'] == 16:
                    data['fee_answer'] = answer
                    fee_info = validation_util_obj.process_fee_structure(answer)
                    for key in fee_info.keys():
                        data[key] = fee_info.get(key) 
                                        
                body = requestProcessor.decode_jinga_template(request,'website/form_fields/'+data['question_template'], data, '')    
            else:
                body = ''
    
            dajax.assign('#qa_'+str(answer_id) + '_edit_fields','innerHTML', body)
    
            for js in data['js']:
                script = requestProcessor.decode_jinga_template(request, "website/form_fields/"+js, data, '')
                dajax.script(script)         
                    
            if question.support_attachments == 1:
                script = requestProcessor.decode_jinga_template(request, "website/form_fields/file_uploading.js", data, '')
                dajax.script(script)                
       
            return HttpResponse(dajax.json())         
                
        if (ajax == 'suggestion_submit'):     
            answers = {} 
            data['user'] = user      
            data['jurisdiction'] = jurisdiction           
            field_prefix = 'field_'
            question_id = requestProcessor.getParameter('question_id')        
            question = Question.objects.get(id=question_id)                  
            answers = requestProcessor.get_form_field_values(field_prefix)
    
            for key, answer in answers.items():
                if answer == '':
                    del answers[key]
     
            acrf = process_answer(answers, question, jurisdiction, request.user)
                
            file_names = requestProcessor.getParameter('filename') 
            file_store_names = requestProcessor.getParameter('file_store_name') 
            if (file_names != '' and file_names != None) and (file_store_names != '' and file_store_names != None):
                file_name_list = file_names.split(',')
                file_store_name_list = file_store_names.split(',')
                for i in range(0, len(file_name_list)):
                    aac = AnswerAttachment()
                    aac.answer_reference = acrf
                    aac.file_name = file_name_list[i]
                    store_file = '/upfiles/answer_ref_attaches/'+file_store_name_list[i]
                    aac.file_upload = store_file
                    aac.creator = user
                    aac.save()
                        
                    view_question_obj = ViewQuestions()
                    view_question_obj.add_question_to_view('a', question, jurisdiction)
                            
            dajax = get_question_answers_dajax(request, jurisdiction, question, data)
                    
            return HttpResponse(dajax.json())      
        
        if (ajax == 'suggestion_edit_submit'):     
            answers = {} 
            data['user'] = user        
            answer_id = requestProcessor.getParameter('answer_id')
            field_prefix = 'field_'
            answer = AnswerReference.objects.get(id=answer_id)   
            questions = Question.objects.filter(id=answer.question.id)      # done on purpose.
            question = questions[0]          
            answers = requestProcessor.get_form_field_values(field_prefix)
    
            for key, answer in answers.items():
                if answer == '':
                    del answers[key]
                        
            acrf = process_answer(answers, question, jurisdiction, request.user, answer_id)
                
            file_names = requestProcessor.getParameter('filename') 
            file_store_names = requestProcessor.getParameter('file_store_name') 
            if (file_names != '' and file_names != None) and (file_store_names != '' and file_store_names != None):
                AnswerAttachment.objects.filter(answer_reference = acrf).delete()
                    
                file_name_list = file_names.split(',')
                file_store_name_list = file_store_names.split(',')
                for i in range(0, len(file_name_list)):
                    aac = AnswerAttachment()
                    aac.answer_reference = acrf
                    aac.file_name = file_name_list[i]
                    store_file = '/upfiles/answer_ref_attaches/'+file_store_name_list[i]
                    aac.file_upload = store_file
                    aac.creator = user
                    aac.save()
                        
                    view_question_obj = ViewQuestions()
                    view_question_obj.add_question_to_view('a', question, jurisdiction)
                                        
            dajax = get_question_answers_dajax(request, jurisdiction, question, data)
                    
            return HttpResponse(dajax.json())      
            
        if (ajax == 'add_to_views'):
            view_obj = None
            user = request.user
            if not user.is_authenticated():
                raise Http401
            entity_name = requestProcessor.getParameter('entity_name') 
            question_id = requestProcessor.getParameter('question_id') 

            if entity_name == 'quirks':
                view_objs = View.objects.filter(view_type = 'q', jurisdiction = jurisdiction)
                if len(view_objs) > 0:
                        view_obj = view_objs[0]
                else:
                    view_obj = View()
                    view_obj.name = 'quirks'
                    view_obj.description = 'Quirks'
                    view_obj.view_type = 'q'
                    view_obj.jurisdiction_id = jurisdiction.id
                    view_obj.save()

            elif entity_name == 'favorites':
                view_objs = View.objects.filter(view_type = 'f', user = request.user)
                if len(view_objs) > 0:
                    view_obj = view_objs[0]
                else:
                    view_obj = View()
                    view_obj.name = 'Favorite Fields'
                    view_obj.description = 'Favorite Fields'
                    view_obj.view_type = 'f'
                    view_obj.user_id = request.user.id
                    view_obj.save()

            if view_obj != None:
                view_questions_objs = ViewQuestions.objects.filter(view = view_obj).order_by('-display_order')
                if len(view_questions_objs) > 0:
                    highest_display_order = view_questions_objs[0].display_order
                else:
                    highest_display_order = 0
                if not question_id in [vq.question.id for vq in view_questions_objs]:
                    view_questions_obj = ViewQuestions()
                    view_questions_obj.view_id = view_obj.id
                    view_questions_obj.question_id = question_id
                    view_questions_obj.display_order = int(highest_display_order) + 5
                    view_questions_obj.save()

            view_questions_obj = ViewQuestions()
            if entity_name == 'quirks':
                quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)

                data['quirk_number_of_questions'] = 0
                if 'view_questions' in quirks:
                    data['quirk_number_of_questions'] = len(quirks['view_questions'])

                # update the quirks or the favorite fields count
                dajax.assign('#quirkcount','innerHTML', data['quirk_number_of_questions'])
                dajax.assign('#quirk_'+str(question_id),'innerHTML', 'Added to quirks')

            elif entity_name == 'favorites':
                data['user_number_of_favorite_fields'] = 0
                if request.user.is_authenticated():
                    user_obj = User.objects.get(id=request.user.id)
                    if user_obj != None:
                        user_favorite_fields = view_questions_obj.get_user_favorite_fields(user_obj)
                        if 'view_questions' in user_favorite_fields:
                            data['user_number_of_favorite_fields'] = len(user_favorite_fields['view_questions'])

                    # update the quirks or the favorite fields count
                    dajax.assign('#favfieldscount','innerHTML', data['user_number_of_favorite_fields'])
                    dajax.assign('#favorite_field_'+str(question_id),'innerHTML', 'Added to favorite fields')

            return HttpResponse(dajax.json())
            
        if (ajax == 'remove_from_views'):
            view_obj = None
            user = request.user
            if not user.is_authenticated():
                raise Http401
            entity_name = requestProcessor.getParameter('entity_name') 
            question_id = requestProcessor.getParameter('question_id') 
                  
            if entity_name == 'quirks':
                view_objs = View.objects.filter(view_type = 'q', jurisdiction = jurisdiction)
                if len(view_objs) > 0:
                    view_obj = view_objs[0]
                        
            elif entity_name == 'favorites':
                view_objs = View.objects.filter(view_type = 'f', user = request.user)
                if len(view_objs) > 0:
                    view_obj = view_objs[0]          
                
            if view_obj != None:
                question = Question.objects.get(id=question_id)
                view_questions_objs = ViewQuestions.objects.filter(view = view_obj, question = question)
                if len(view_questions_objs) > 0:
                    for view_questions_obj in view_questions_objs:
                        view_questions_obj.delete()
                
                view_questions_obj = ViewQuestions()
                if entity_name == 'quirks':
                    quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)
                        
                    data['quirk_number_of_questions'] = 0    
                    if 'view_questions' in quirks:
                        data['quirk_number_of_questions'] = len(quirks['view_questions'])    
                            
                    # update the quirks or the favorite fields count
                    dajax.assign('#quirkcount','innerHTML', data['quirk_number_of_questions'])                    
                                
                elif entity_name == 'favorites':        
                    data['user_number_of_favorite_fields'] = 0    
                    if request.user.is_authenticated():
                        user_obj = User.objects.get(id=request.user.id)
                        if user_obj != None:
                            user_favorite_fields = view_questions_obj.get_user_favorite_fields(user_obj)
                            if 'view_questions' in user_favorite_fields:
                                data['user_number_of_favorite_fields'] = len(user_favorite_fields['view_questions'])             
                                   
                        # update the quirks or the favorite fields count
                        dajax.assign('#favfieldscount','innerHTML', data['user_number_of_favorite_fields']) 
                            
                dajax.assign('#div_question_content_'+str(question_id),'innerHTML', '') 
                
            return HttpResponse(dajax.json())
        
        if (ajax == 'validation_history'):
            caller = requestProcessor.getParameter('caller')
            entity_name = requestProcessor.getParameter('entity_name')              
            entity_id = requestProcessor.getParameter('entity_id')   
            data = validation_util_obj.get_validation_history(entity_name, entity_id)
            data['destination'] = requestProcessor.getParameter('destination')   
            print entity_id
            if caller == None:
                params = 'zIndex: 8000'
            elif caller == 'dialog':
                params = 'zIndex: 12000'
                    
            if data['destination'] == None:
                data['destination']  = ''
                                
            if data['destination'] == 'dialog':
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/validation_history_dialog.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                dajax.script('$("#fancybox_close").click(function(){$.fancybox.close();return false;});')       
                dajax.script('controller.showModalDialog("#fancyboxformDiv");')                
            else:
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/validation_history.html', data, '')             
                print body    
                dajax.assign('#validation_history_div_'+entity_id,'innerHTML', body)
                #dajax.assign('.info_content','innerHTML', body)
                #dajax.script("controller.showInfo({target: '#validation_history_"+entity_id+"', "+params+"});")          
                            
            return HttpResponse(dajax.json())     
            
        
        if (ajax == 'cancel_suggestion'):
            user = request.user
            data['user'] = user        
            entity_id = requestProcessor.getParameter('entity_id') 
    
            answer = AnswerReference.objects.get(id=entity_id) 
            answer_prev_status = answer.approval_status        
            answer.approval_status = 'C'
            answer.status_datetime = datetime.datetime.now()
            answer.save()
            
            jurisdiction = answer.jurisdiction
            question = answer.question
            dajax = get_question_answers_dajax(request, jurisdiction, question, data)
            
            if answer_prev_status == 'A':        
                data['top_contributors'] = get_ahj_top_contributors(jurisdiction, category)  
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_top_contributors.html', data, '')   
                dajax.assign('#top-contributor','innerHTML', body)                
                
                    
            if question.support_attachments == 1:
                view_question_obj = ViewQuestions()
                view_question_obj.remmove_question_from_view('a', question, jurisdiction)                    
                
            return HttpResponse(dajax.json())           
        
        if (ajax == 'approve_suggestion'):
            
            user = request.user
            data['user'] = user
            entity_id = requestProcessor.getParameter('entity_id') 
            print ajax + str(entity_id)
            answer = AnswerReference.objects.get(id=entity_id) 
            answer.approval_status = 'A'
            answer.status_datetime = datetime.datetime.now()
            answer.save()
       
            validation_util_obj.on_approving_a_suggestion(answer)
            jurisdiction = answer.jurisdiction
            question = answer.question
            dajax = get_question_answers_dajax(request, jurisdiction, question, data)
            
            data['top_contributors'] = get_ahj_top_contributors(jurisdiction, category)  
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_top_contributors.html', data, '')   
            dajax.assign('#top-contributor','innerHTML', body)                
        
                               
            return HttpResponse(dajax.json())         
        
        if (ajax == 'vote'):
            requestProcessor = HttpRequestProcessor(request)
            dajax = Dajax()
            ajax = requestProcessor.getParameter('ajax')
            user = request.user
            entity_id = requestProcessor.getParameter('entity_id')
            entity_name = requestProcessor.getParameter('entity_name')
            vote = requestProcessor.getParameter('vote')
            confirmed = requestProcessor.getParameter('confirmed')
            if confirmed == None:
                confirmed = 'not_yet'

            feedback = validation_util_obj.process_vote(user, vote, entity_name, entity_id, confirmed)

            if feedback == 'registered':
                if entity_name == 'requirement':
                    answer = AnswerReference.objects.get(id=entity_id)
                    question = answer.question
                    answer_ids = [answer.id]
                    category_name = 'VoteRequirement'
                    data['answers_votes'] = get_answer_voting_info(category_name, answer.jurisdiction, user, answer_ids)
                    dajax.add_data(data, 'process_ahj_answers_votes')
                    dajax.script("show_hide_vote_confirmation('"+entity_id+"');")
            elif feedback == 'registered_with_changed_status':
                if entity_name == 'requirement':
                    answer = AnswerReference.objects.get(id=entity_id)
                    question = answer.question
                    dajax = get_question_answers_dajax(request, jurisdiction, question, data)
                    terminology = question.get_terminology()

                    if answer.approval_status == 'A':
                        dajax.script("controller.showMessage('"+str(terminology)+" approved.  Thanks for voting.', 'success');")
                    elif answer.approval_status == 'R':
                        dajax.script("controller.showMessage('"+str(terminology)+" rejected. Thanks for voting.', 'success');")
                    dajax.script("show_hide_vote_confirmation('"+entity_id+"');")

                    if answer.approval_status == 'A':
                        category_obj = question.category
                        category = category_obj.name
                        data['top_contributors'] = get_ahj_top_contributors(data['jurisdiction'], category)
                        body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_top_contributors.html', data, '')
                        dajax.assign('#top-contributor','innerHTML', body)
            elif feedback == 'will_approve':
                # prompt confirmation
                answer = AnswerReference.objects.get(id=entity_id)
                answers = AnswerReference.objects.filter(question=answer.question, jurisdiction=answer.jurisdiction)
                if len(answers) > 1 and answer.question.has_multivalues == 0:
                    dajax.script("confirm_approved('yes');")
                else:
                    dajax.script("confirm_approved('no');")
            elif feedback == 'will_reject':
                # prompt confirmation
                answer = AnswerReference.objects.get(id=entity_id)
                question = answer.question
                question_terminology = question.get_terminology()
                dajax.script("confirm_rejected("+str(entity_id)+",'"+question_terminology+"');")
            #dajax.script("controller.showMessage('Your feedback has been sent and will be carefully reviewed.', 'success');")
            return HttpResponse(dajax.json())
    
    ######################################### END OF AJAX #######################################################    
    ############## to determine the last contributor's organization
    organization = None
    try:
        contributor = jurisdiction.last_contributed_by
    except:
        contributor = None

    data['last_contributed_by']  = contributor       
    ###################################################

    data['jurisdiction'] = jurisdiction
    data['jurisdiction_id'] = jurisdiction.id

    data['nav'] = 'no'   
    data['current_nav'] = 'browse'    
    data['home'] = '/'       
    data['page'] = 'AHJ'
    data['unauthenticated_page_message'] = "The information on this page is available to all visitors of the National Solar Permitting Database.  If you would like to add information to the database and interact with the solar community, please sign in below or "
    data['authenticated_page_message'] = 'See missing or incorrect information? Mouse over a field and click the blue pencil to add or edit the information.'
    data[category] = ' active'      # to set the active category in the left nav     
    data['show_google_map'] = False    
    data['str_address'] = ''       
    ###############################################################################################################
    
    #jurisdiction_templates = get_jurisdiction_templates(jurisdiction)
        
    data['jurisdiction'] = jurisdiction
        
    if 'accessible_views' in request.session:
        data['accessible_views'] = request.session['accessible_views']
    else:
        data['accessible_views'] = []

    (question_ids, view) = get_questions_in_category(user, jurisdiction, category)
    data['view'] = view
    records = get_ahj_data(jurisdiction, category, empty_data_fields_hidden, user, question_ids = question_ids)

    answers_contents = {}
    #data_answer = {}
    #answers_html = {}
    show_google_map = False
    records_by_category = {}
    for rec in records:
        cid = rec['category_id']
        if not cid in records_by_category:
            records_by_category[cid] = { 'cat_description': rec['cat_description'],
                                         'sorted_question_ids': [],
                                         'questions': {} }
        qid = rec['question_id']
        if not rec['id']: # this is a question
            assert(rec['question_id'] not in records_by_category[cid]['questions']) # shouldn't get duplicate questions
            records_by_category[cid]['sorted_question_ids'].append(qid)
            rec['answers'] = []
            rec['logged_in_user_suggested_a_value'] = False
            rec['terminology'] = Question().get_question_terminology(qid)
            rec['pending_answer_ids'] = []
            records_by_category[cid]['questions'][qid] = rec
        else: # it's an answer
            assert(rec['question_id'] in records_by_category[cid]['questions'])
            question = records_by_category[cid]['questions'][qid]
            question['answers'].append(rec)
            if rec['creator_id'] == user.id and rec['approval_status'] == 'P':
                question['pending_answer_ids'].append(rec['id'])
            rec['content'] = json.loads(rec['value'])
            question['logged_in_user_suggested_a_value'] = rec['creator_id'] == user.id

        if rec['question_id'] == 4:
            show_google_map = True
                  
        if rec['id'] != None:
            if rec['question_id'] == 16:
                fee_info = validation_util_obj.process_fee_structure(json.loads(rec['value']) )                   
                for key in fee_info.keys():
                    data[key] = fee_info.get(key)               
    if category == 'all_info' or show_google_map == True:
        data['show_google_map'] = show_google_map
        ################# get the correct address for google map #################### 
        question = Question.objects.get(id=4)      
        data['str_address'] = question.get_addresses_for_map(jurisdiction)  
        data['google_api_key'] = django_settings.GOOGLE_API_KEY     

    data['cqa'] = records_by_category
    data['answers_contents'] = answers_contents   
        
    if category != 'favorite_fields' and category != 'quirks':           
        request.session['empty_data_fields_hidden'] = data['empty_data_fields_hidden']    
      
    ################# Show the message in the yellow box on top of the ahj page ####################         
    data['show_ahj_message'] = False     
    ################################################################################################             
                
    data['user'] = user
    ################# save_recent_search #################### 
    if user.is_authenticated():
        user_obj = User.objects.get(id=user.id)
        save_recent_search(user_obj, jurisdiction)                
                
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data  
    
    
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_cqa.html', data, '') 


def get_jurisdiction_templates(jurisdiction):
    cf_template_objs = Template.objects.filter(jurisdiction = jurisdiction, template_type__iexact='CF', accepted=1)
    rt_template_objs = Template.objects.filter(template_type__iexact='RT', accepted=1)
    
    template_objs = rt_template_objs | cf_template_objs    
    
    return template_objs
    
def get_jurisdiction_answers(jurisdiction, jurisdiction_templates, jurisdiction_questions, answer_status=None):

    if answer_status == None:
        jurisdiction_answer_objs = AnswerReference.objects.filter(jurisdiction = jurisdiction, approval_status__in=('A', 'P'), question__accepted__exact=1, question__qtemplate__in=jurisdiction_templates, question__in=jurisdiction_questions).order_by('question__category__name','question__display_order','approval_status','create_datetime') 
    elif answer_status == 'A':
        jurisdiction_answer_objs = AnswerReference.objects.filter(jurisdiction = jurisdiction, approval_status__in=('A'), question__accepted__exact=1, question__qtemplate__in=jurisdiction_templates, question__in=jurisdiction_questions).order_by('question__category__name','question__display_order','approval_status','create_datetime') 
    elif answer_status == 'P':
        jurisdiction_answer_objs = AnswerReference.objects.filter(jurisdiction = jurisdiction, approval_status__in=('P'), question__accepted__exact=1, question__qtemplate__in=jurisdiction_templates, question__in=jurisdiction_questions).order_by('question__category__name','question__display_order','approval_status','create_datetime') 
        
       
    return jurisdiction_answer_objs

def get_jurisdiction_questions(jurisdiction, jurisdiction_templates, user, category='all_info'):
    jurisdiction_question_objs = None
    if category == 'all_info':
        jurisdiction_question_objs = Question.objects.filter(accepted=1, qtemplate__in=jurisdiction_templates).order_by('display_order', '-modify_datetime')   
    else:
        category_objs = QuestionCategory.objects.filter(name__iexact=category, accepted=1)
        if len(category_objs) > 0:
            jurisdiction_question_objs = Question.objects.filter(category__in=category_objs, accepted=1, qtemplate__in=jurisdiction_templates).order_by('display_order', '-modify_datetime')             
        else:
            if category == 'favorite_fields':
                category_objs = View.objects.filter(user = user, view_type__exact='f')          
            elif category == 'quirks':
                category_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='q')
            elif category == 'attachments':
                category_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='a')         
            else:
                category_objs = View.objects.filter(name__iexact=category)  # we work with one view per ahj content, not like muliple categories in all_info 
                              
            question_ids = ViewQuestions.objects.filter(view__in=category_objs).order_by('display_order').values('question').distinct()
            jurisdiction_question_objs = Question.objects.filter(id__in=question_ids)
            
    return jurisdiction_question_objs

def get_questions_with_answers(self, jurisdiction, jurisdiction_questions):
    answer_question_ids = AnswerReference.objects.filter(jurisdiction = jurisdiction, approval_status__in=('A', 'P'), question__accepted__exact=1, question__qtemplate__in=jurisdiction_templates, question__in=jurisdiction_questions).values_list('question_id').distinct()
    questions_with_answers = jurisdiction_questions.filter(id__in=answer_question_ids)   
   
    return questions_with_answers 

def get_ahj_votes_html(request, jurisdiction, answers, login_user, category='all_info', questions=None):
    requestProcessor = HttpRequestProcessor(request)       
    data = {}
    data['jurisdiction_id'] = jurisdiction.id
    category_name = 'VoteRequirement'     
    answers_votes = get_jurisdiction_voting_info(category_name, jurisdiction, login_user)

   
    ahj_votes_html = {}
    for answer in answers:
        data['this_answer_id'] = answer.id
        if answer.id in answers_votes:
            data['total_up_votes'] = answers_votes[answer.id]['total_up_votes']
            data['total_down_votes'] = answers_votes[answer.id]['total_down_votes']
            data['num_consecutive_last_down_votes'] = answers_votes[answer.id]['num_consecutive_last_down_votes']
            data['can_vote_up'] = answers_votes[answer.id]['can_vote_up']
            data['can_vote_down'] = answers_votes[answer.id]['can_vote_down']
            data['last_down_vote_date'] = answers_votes[answer.id]['last_down_vote_date']
            data['up_vote_found'] = answers_votes[answer.id]['up_vote_found']
            data['login_user_last_vote'] = answers_votes[answer.id]['login_user_last_vote']    
        else:
            data['total_up_votes'] = 0
            data['total_down_votes'] = 0
            data['num_consecutive_last_down_votes'] = 0
            data['can_vote_up'] = True
            data['can_vote_down'] = True
            data['last_down_vote_date'] = ''
            data['up_vote_found'] = False 
            data['login_user_last_vote'] = ''   
            
        data['creator_id'] = answer.creator_id
        data['login_user_id'] = login_user.id                        
        ahj_votes_html[answer.id] = requestProcessor.decode_jinga_template(request,'website/jurisdictions/ahj_answer_votes.html', data, '')
        
    return ahj_votes_html

def get_jurisdiction_voting_info(category_name, jurisdiction, login_user, category = 'all_info', questions = None):
    action_category = ActionCategory.objects.filter(name__iexact=category_name)
    if category == 'all_info':
        category_objs = QuestionCategory.objects.filter(accepted=1)
    else:
        category_objs = QuestionCategory.objects.filter(name__iexact=category, accepted=1)
    
    if len(action_category) > 0:
        if questions == None:
            votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction, question_category__in=category_objs).order_by('question_category', 'entity_id', '-action_datetime')    
        else:
            answer_ids = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__in=questions).exclude(approval_status__exact='R').exclude(approval_status__exact='F').exclude(approval_status__exact='C').values_list('id', flat=True)
            if len(answer_ids) > 0:
                votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction, entity_id__in=answer_ids, question_category__in=category_objs).order_by('question_category', 'entity_id', '-action_datetime')    
            else:
                votes = None

        vote_info = {}
        if votes != None:
            for vote in votes:
                if vote.entity_id not in vote_info:
                    vote_info[vote.entity_id] = {}
                    vote_info[vote.entity_id]['total_up_votes'] = 0
                    vote_info[vote.entity_id]['total_down_votes'] = 0
                    vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                    vote_info[vote.entity_id]['can_vote_up'] = False
                    vote_info[vote.entity_id]['can_vote_down'] = False
                    vote_info[vote.entity_id]['last_down_vote_date'] = ''
                    vote_info[vote.entity_id]['up_vote_found'] = False
                    vote_info[vote.entity_id]['login_user_last_vote'] = ''
                                               
                if vote.data == 'Vote: Up':
                    vote_info[vote.entity_id]['total_up_votes'] = vote_info[vote.entity_id]['total_up_votes'] + 1   
                    vote_info[vote.entity_id]['up_vote_found'] = True
                    vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                    if vote_info[vote.entity_id]['login_user_last_vote'] == '':
                        vote_info[vote.entity_id]['login_user_last_vote'] = 'up'
                                                         
                elif vote.data == 'Vote: Down':
                    vote_info[vote.entity_id]['total_down_votes'] = vote_info[vote.entity_id]['total_down_votes'] + 1   
                        
                    if 'last_down_vote_date' not in vote_info[vote.entity_id]:
                        #vote_info[vote.entity_id]['last_down_vote'] = vote
                        datetime_util_obj = DatetimeHelper(vote.action_datetime)
                        last_down_vote_date = datetime_util_obj.showStateTimeFormat(jurisdiction.state)                    
                        vote_info[vote.entity_id]['last_down_vote_date'] = last_down_vote_date
                        
                    if vote_info[vote.entity_id]['login_user_last_vote'] == '':
                        vote_info[vote.entity_id]['login_user_last_vote'] = 'down'                        
                                                
                    if vote_info[vote.entity_id]['up_vote_found'] == False:
                        vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = vote_info[vote.entity_id]['num_consecutive_last_down_votes'] + 1
    
                    
            #if vote.user_id not in vote_info[vote.entity_id]['user_last_vote_on_this_item']:
            #    vote_info[vote.entity_id]['user_last_vote_on_this_item'][vote.user_id] = vote
                    
            # temp test data
            #vote_info[vote.entity_id]['can_vote_up'] = False
            #vote_info[vote.entity_id]['can_vote_down'] = False
                        
    return vote_info    

def get_ahj_action_html(request, jurisdiction, questions, login_user, category):
    requestProcessor = HttpRequestProcessor(request)       
    data = {}
    data['jurisdiction_id'] = jurisdiction.id
    questions_actions = get_ahj_actions(jurisdiction, login_user)
    data['quirk_questions' ] = questions_actions['quirk_questions']
    data['favorite_questions' ] = questions_actions['favorite_questions'] 
    data['category' ] = questions_actions['category']   
    ahj_action_html = {}
    for question in questions:
        data['this_question_id'] = question.id
        ahj_action_html[question.id] = requestProcessor.decode_jinga_template(request,'website/jurisdictions/ahj_actions.html', data, '')
        
    return ahj_action_html

def get_ahj_answers_attachments(jurisdiction):
    answers_attachments = {}
    attachments = AnswerAttachment.objects.filter(answer_reference__jurisdiction = jurisdiction)    # to gather all the attachments for all the answers.
    for attachment in attachments:
        answers_attachments[attachment.answer_reference.id] ={}
        answers_attachments[attachment.answer_reference.id]['file_name'] = str(attachment.file_name)    # to build dict of attachment per answer, for ease of retrival 
        answers_attachments[attachment.answer_reference.id]['file_upload'] = str(attachment.file_upload) 
            
    return answers_attachments
    
def get_ahj_actions(jurisdiction, login_user):
    questions_actions = {}
    
    view_questions_obj = ViewQuestions()
    quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)
        
    quirk_questions = []
    if len(quirks) > 0:
        if len(quirks['view_questions']) > 0:
            for quirk in quirks['view_questions']:
                quirk_questions.append(quirk.question_id)
            
    user_favorite_fields = view_questions_obj.get_user_favorite_fields(login_user)    
    
    favorite_questions = []
    if len(user_favorite_fields) > 0:
        if len(user_favorite_fields['view_questions']) > 0:
            for favorite_question in user_favorite_fields['view_questions']:
                favorite_questions.append(favorite_question.question_id)    
            
    questions_actions['quirk_questions'] = quirk_questions
    questions_actions['favorite_questions'] = favorite_questions
            
    return questions_actions 

def get_answers_comments(jurisdiction, answers, login_user):
    answers_comments = {}
    for answer in answers:
        answer_comment = {}
        comment_total = Comment.objects.filter(jurisdiction__exact=jurisdiction, entity_name = 'AnswerReference', entity_id = answer.id).count()
        answer_comment['comment_total'] = comment_total
        try:
            userviews = UserCommentView.objects.filter(jurisdiction__exact=jurisdiction, entity_name = 'AnswerReference', entity_id = answer.id, user = login_user)
            userview = userviews[0]
            answer_comment['new_comment_total'] = comment_total - userview.comments_count
        except:
            answer_comment['new_comment_total'] = comment_total - 0
                
        answers_comments[answer.id] = answer_comment
            
    return answers_comments   

def get_answer_comment_txt(jurisdiction, answer, login_user):
    comment = {}
    comment_total = Comment.objects.filter(jurisdiction__exact=jurisdiction, entity_name = 'AnswerReference', entity_id = answer.id).count()
    comment['comment_total'] = comment_total
    try:
        userviews = UserCommentView.objects.filter(jurisdiction__exact=jurisdiction, entity_name = 'AnswerReference', entity_id = answer.id, user = login_user)
        userview = userviews[0]
        comment['new_comment_total'] = comment_total - userview.comments_count
    except:
        comment['new_comment_total'] = comment_total - 0
                    
    if comment['comment_total'] == 0:
        comment['comment_text'] = "Add a comment"
    else:
        comment['comment_text'] = str(comment['comment_total']) + " comments" 
        if comment['new_comment_total'] != comment['comment_total']:
            comment['comment_text'] = comment['comment_text'] + " (* " + str(comment['new_comment_total']) + " new)" 
                    
    return comment   

def get_ahj_questions_messages(questions_with_answers, jurisdiction_answers, login_user):

    questions_messages = {}
    for question in questions_with_answers:
        answers = jurisdiction_answers.filter(question = question)   
        questions_messages[question.id] = get_question_messages(question, answers, login_user)
        
    return questions_messages
        
        
def get_question_messages(question, question_answers, login_user):
    question_terminology = question.get_terminology()    
    pending_answers = []
    approved_answers = []

    for answer in question_answers:
        if answer.approval_status == 'A':
            approved_answers.append(answer)
        elif answer.approval_status == 'P':
            pending_answers.append(answer)
    
    message = ''

    if len(question_answers) > 1:       
        message = message + "More than one "+question_terminology +" suggested.  Please vote.<br/>"
        
    if len(approved_answers) > 0 and len(pending_answers) > 0:
        message = message + 'The previous approved '+ question_terminology  + ' has been challenged.<br/>' 
        
    for answer in pending_answers:
        datetime_util_obj = DatetimeHelper(answer.create_datetime)
        answer_create_datetime= datetime_util_obj.showStateTimeFormat(answer.jurisdiction.state) 
        
        if answer.creator_id == login_user.id:      # your own suggestion. cannot vote on your own suggestion.                  
            message = message + 'You suggested a ' + question_terminology  + ' for this field on ' + answer_create_datetime + '.<br>The community must vote on its accuracy or it must remain unchallenged for one week before it is approved.<br/>'
        else:
            div_id="id_"+str(answer.id) 
            try:                                    # somebody else's suggestion.  u can vote on it
                user = User.objects.get(id=answer.creator_id)
                user_display_name = user.get_profile().get_display_name()
                user_id = user.id
            except:
                user_id = 0
                user_display_name = 'NA'        
                    
            onmouseover="controller.postRequest('/account/', {ajax: 'user_profile_short', user_id: '"+str(user_id)+"',  unique_list_id: '"+str(answer.id)+"'  });" 
            onmouseout = "document.getElementById('simple_popup_div_on_page').style.display='none';"
            temp_str = ''
            if approved_answers > 0:
                if pending_answers == 1: 
                    temp_str = "A new "
                else:
                    if pending_answers == 1: 
                        temp_str = 'This '               
            
            message = message + temp_str + question_terminology  + " was suggested by <a href='#' id='"+div_id+"' onmouseover=\""+onmouseover+"\" onmouseout=\""+onmouseout+"\" >"+user_display_name + "</a> on " + answer_create_datetime + ".  Please vote on its accuracy.<br/>"

    
    return message


def get_ahj_additional_display_data(questions, jurisdiction_answers, login_user):

    ahj_additional_display_data = {}
    for question in questions:
        answers = jurisdiction_answers.filter(question = question)   
        ahj_additional_display_data[question.id] = get_question_additional_display_data(question, answers, login_user)
        
    return ahj_additional_display_data
        
def get_questions_answers_headings(questions_with_answers, login_user):

    answers_headings = {}
    for question_id in questions_with_answers.keys():
        answers = questions_with_answers.get(question_id)
        if len(answers) > 0:
            question_answers_headings = get_answers_headings(answers, login_user)
            answers_headings.update(question_answers_headings)
        
    return answers_headings
        
def get_answers_headings(answers, login_user):
 
    approved_answers = []
    pending_answers = []   
    
    for answer in answers:
        if answer.approval_status == 'A':
            approved_answers.append(answer)
        if answer.approval_status == 'P':
            pending_answers.append(answer)
             
    answers_headings = {}

    count = 0
    suggestion_header = ''
    for answer in answers:
        question = answer.question
        if answer.approval_status == 'P':
            if question.has_multivalues != 1:
                if len(approved_answers) > 0:      # has approved answers   
                    if len(pending_answers) == 1:       # one approved answer and only one suggestion
                        suggestion_header = 'New suggestion'
                    else:                               # one approved answer and multiple suggestion (2 max)
                        count = count + 1
                        suggestion_header = 'New suggestion ' + str(count) 
                else:                                   # NO approved answer   
                    if len(pending_answers) == 1:       # NO approved answer and only one suggestion
                        suggestion_header = ''
                    else:                               # one approved answer and multiple suggestion (no max in num of suggestions)
                        count = count + 1
                        suggestion_header = 'Suggestion ' + str(count)  
            else:
                suggestion_header = ''    # no heading is needed for multivalues items
        else:            
            if question.has_multivalues != 1:
                if len(pending_answers) > 0:     # one approved answer and there are new suggestion
                    suggestion_header = 'Previously approved value'    
    
        answers_headings[answer.id] = suggestion_header

    return answers_headings

        
def process_answer(data, question, jurisdiction, user, answer_id=None):    
    answer = json.dumps(data)   # to convert to json

    if question:
        is_callout=0          

        validation_util_obj = FieldValidationCycleUtil() 
        arcf = validation_util_obj.save_answer(question, answer, jurisdiction, 'AddRequirement', user, is_callout, answer_id)
        return arcf
    else:
        print "no question '' has been set up" 
        return None

      
def save_recent_search(user, jurisdiction):
    try:
        user_search = UserSearch(user=user)
        user_search.entity_name = 'Jurisdiction'
        user_search.entity_id = jurisdiction.id
        user_search.label = jurisdiction.show_jurisdiction()
        user_search.save()
    except:
        pass
    
def get_ahj_top_contributors(jurisdiction, category):
    category_objs = []
    if category == 'all_info':
        category_objs = QuestionCategory.objects.filter(accepted__exact=1).order_by('display_order')
    else:
        category_objs = QuestionCategory.objects.filter(name__iexact=category, accepted__exact=1)

    top_contributors = []
    answers = AnswerReference.objects.filter(jurisdiction=jurisdiction, question__category__in=category_objs, approval_status ='A') 
  
    if len(answers)>0:
        contributors = {}
           
        for answer in answers:
            if answer.organization != None:
                if answer.organization.name != 'Clean Power Finance': # cpf not included.
                    if answer.organization.id in contributors:
                      
                        contributors[answer.organization] =  contributors[answer.organization] + 1
                    else:
                    
                        contributors[answer.organization] = 1    
                        
            else:
                #should include only status = 'A' since we want only 'active' org member, not 'AI' or 'MI'.  those are not approved yet.
                orgmembers = OrganizationMember.objects.filter(user = answer.creator, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R')
                if orgmembers != None and len(orgmembers) >  0:
                    org = orgmembers[0].organization
                    answer.organization = org
                    answer.save()
                            
                    if org.id in contributors:
                      
                        contributors[answer.organization] =  contributors[answer.organization] + 1
                    else:
                      
                        contributors[answer.organization] = 1                      
                        
                       
                
         
        if len(contributors) > 0:
            top_contributors = sorted(contributors.iteritems(), key=operator.itemgetter(1), reverse=True)                
       
    return top_contributors
        
def answer_uploadfile(request):

    allowedExtension = ('.pdf')
    sizeLimit = django_settings.MAX_UPLOAD_FILE_SIZE
    uploader = qqFileUploader(allowedExtension, sizeLimit)
    #print 11111111111111111111111
    #print sizeLimit
    result = uploader.handleUpload(request, django_settings.MEDIA_ROOT + "/upfiles/answer_ref_attaches/")

    return_array = result["json"]
    from django.utils import simplejson as json

    if result['success'] == True:
        return_array = json.loads(result["json"])
        #full_path = django_settings.MEDIA_ROOT+'/upfiles/answer_ref_attaches/'+return_array['store_name']
        #aa = get_thumbnail(full_path,'140x140', quality=99)
        #return_array['thum_path'] = aa.url
        return_array = json.dumps(return_array)
    return HttpResponse(return_array)   

def get_question_answers_dajax(request, jurisdiction, question, data): 
    dajax = Dajax()     
    requestProcessor = HttpRequestProcessor(request)    
    data = get_question_data(request, jurisdiction, question, data)
    print '1'
    body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_cqa_qa.html', data, '')
    dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)
    script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_cqa_qa.js' , data, '')
    dajax.script(script)   
    
    if data['category'] == 'all_info':          
        question_categories = QuestionCategory.objects.filter(accepted=1)
    else:
        question_categories = QuestionCategory.objects.filter(name__iexact=data['category'])               
            
    # for google map
    if question.id == 4:
        str_addr = question.get_addresses_for_map(jurisdiction)  
        data['str_address'] = str_addr
        dajax.script("load_google_map('"+str(str_addr)+"')")       

    return dajax

def get_question_data(request, jurisdiction, question, data):
    validation_util_obj = FieldValidationCycleUtil()      
    requestProcessor = HttpRequestProcessor(request)    
    user = request.user
    questions = Question.objects.filter(id=question.id)
    
    display_answers = []    
    answers_headings = {}   
    login_user_suggested_a_value = True   
    pending_editable_answer_ids_array = [] 
    answers_with_attachments = []   
    answers_comments_text = {} 
    
    template_ids = TemplateQuestion.objects.filter(question = questions).values_list('template_id')  
    templates = Template.objects.filter(id__in=template_ids)
    question_answers = get_jurisdiction_answers(jurisdiction, templates, questions) 
    
    data['jurisdiction'] = jurisdiction      
    data['question'] = question       
    data['user'] = user       
 
    if len(question_answers) > 0:     
        question_approved_answers = question_answers.filter(approval_status = 'A')     
        question_pending_answers = question_answers.filter(approval_status = 'P')
        
        '''                                         
        if question.id == 4:
            data['show_google_map'] = True
            ################# get the correct address for google map ####################         
            data['str_address'] = question.get_addresses_for_map(jurisdiction)  
            data['google_api_key'] = django_settings.GOOGLE_API_KEY 
            #############################################################################         
        '''             
        answers_contents = {}    
        answers_attachments = {}

    
        for answer in question_approved_answers:
            this_answer_question = answer.question
            display_answers.append(answer)

            if this_answer_question.id == 16:
                fee_info = validation_util_obj.process_fee_structure(json.loads(answer.value) )                   
                for key in fee_info.keys():
                    data[key] = fee_info.get(key)               
                
            answer_content = json.loads(answer.value)    
            answers_contents[answer.id] = answer_content        
                
            if this_answer_question.support_attachments == 1:
                answers_with_attachments.append(answer)
                #answers_attachments[answer.id] = []  
                
            answers_comments_text[answer.id] = get_answer_comment_txt(jurisdiction, answer, user)
            
            if answer.creator_id == user.id: 
                login_user_suggested_a_value = True            
                
            if this_answer_question.has_multivalues == 0:
                break;                       
                
        for answer in question_pending_answers:
            this_answer_question = answer.question
            display_answers.append(answer)

            if this_answer_question.id == 16:
                fee_info = validation_util_obj.process_fee_structure(json.loads(answer.value) )                   
                for key in fee_info.keys():
                    data[key] = fee_info.get(key)               
                
            answer_content = json.loads(answer.value)    
            answers_contents[answer.id] = answer_content        
                
            if this_answer_question.support_attachments == 1:
                answers_with_attachments.append(answer)        
                #answers_attachments[answer.id] = []        
                
            answers_comments_text[answer.id] = get_answer_comment_txt(jurisdiction, answer, user)       
            
            if answer.creator_id == user.id: 
                login_user_suggested_a_value = True
            
            if answer.approval_status == 'P':
                pending_editable_answer_ids_array.append(answer.id)                      
                     
        if len(answers_with_attachments) > 0:
            attachments = AnswerAttachment.objects.filter(answer_reference__in=answers_with_attachments)    # to gather all the attachments for all the answers.
            for attachment in attachments:
                #answers_attachments[attachment.answer_reference.id] = attachment[0]    # to build dict of attachment per answer, for ease of retrival   
                answers_attachments[attachment.answer_reference.id] ={}
                answers_attachments[attachment.answer_reference.id]['file_name'] = str(attachment.file_name)    # to build dict of attachment per answer, for ease of retrival 
                answers_attachments[attachment.answer_reference.id]['file_upload'] = str(attachment.file_upload)                  
        
        if len(display_answers) > 0:        
            answers_headings = get_answers_headings(question_answers, user)                    
        
        data['question_messages'] = get_question_messages(question, question_answers, user)     
        #print data['question_messages']  

        data['display_answers'] = display_answers 
        data['answers_contents'] = answers_contents
        data['answers_headings'] = answers_headings    
        data['answers_attachments'] = answers_attachments
        data['question_pending_editable_answer_ids_array'] = pending_editable_answer_ids_array         

        data['question_login_user_suggested_a_value'] = login_user_suggested_a_value     
        data['user'] = user
        data['answers_comments_text'] = answers_comments_text
        print answers_attachments
    else:
        data['display_answers'] = display_answers     # 0 records
        data['question_login_user_suggested_a_value'] = False
        
    return data


def get_answer_voting_info(category_name, jurisdiction, login_user, answer_ids):
    action_category = ActionCategory.objects.filter(name__iexact=category_name)

    votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction, entity_id__in=answer_ids).order_by('entity_id', '-action_datetime')    


    vote_info = {}
    if len(votes) > 0:
        for vote in votes:
            if vote.entity_id not in vote_info:
                vote_info[vote.entity_id] = {}
                vote_info[vote.entity_id]['total_up_votes'] = 0
                vote_info[vote.entity_id]['total_down_votes'] = 0
                vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                vote_info[vote.entity_id]['can_vote_up'] = False
                vote_info[vote.entity_id]['can_vote_down'] = False
                vote_info[vote.entity_id]['last_down_vote_date'] = ''
                vote_info[vote.entity_id]['up_vote_found'] = False
                vote_info[vote.entity_id]['login_user_last_vote'] = ''
                                               
            if vote.data == 'Vote: Up':
                vote_info[vote.entity_id]['total_up_votes'] = vote_info[vote.entity_id]['total_up_votes'] + 1   
                vote_info[vote.entity_id]['up_vote_found'] = True
                vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                if vote_info[vote.entity_id]['login_user_last_vote'] == '':
                    vote_info[vote.entity_id]['login_user_last_vote'] = 'up'
                                                         
            elif vote.data == 'Vote: Down':
                vote_info[vote.entity_id]['total_down_votes'] = vote_info[vote.entity_id]['total_down_votes'] + 1   
                        
                if 'last_down_vote_date' not in vote_info[vote.entity_id]:
                    #vote_info[vote.entity_id]['last_down_vote'] = vote
                    datetime_util_obj = DatetimeHelper(vote.action_datetime)
                    last_down_vote_date = datetime_util_obj.showStateTimeFormat(jurisdiction.state)                    
                    vote_info[vote.entity_id]['last_down_vote_date'] = last_down_vote_date
                        
                if vote_info[vote.entity_id]['login_user_last_vote'] == '':
                    vote_info[vote.entity_id]['login_user_last_vote'] = 'down'                        
                                            
                if vote_info[vote.entity_id]['up_vote_found'] == False:
                    vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = vote_info[vote.entity_id]['num_consecutive_last_down_votes'] + 1
    
                    
            #if vote.user_id not in vote_info[vote.entity_id]['user_last_vote_on_this_item']:
            #    vote_info[vote.entity_id]['user_last_vote_on_this_item'][vote.user_id] = vote
                    
            # temp test data
            #vote_info[vote.entity_id]['can_vote_up'] = False
            #vote_info[vote.entity_id]['can_vote_down'] = False
                        
    return vote_info    

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

def get_questions_in_category(user, jurisdiction, category):
    if category == 'all_info':
        return (None, False) # we really mean all questions
    else:
        category_objs = QuestionCategory.objects.filter(name__iexact=category, accepted__exact=1)
        if len(category_objs) == 0:  # view
            if category == 'favorite_fields':
                category_objs = View.objects.filter(user = user, view_type__exact='f')        
            elif category == 'quirks':
                category_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='q')
            elif category == 'attachments':
                category_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='a')         
            else:
                category_objs = View.objects.filter(name__iexact=category)  # we work with one view per ahj content, not like muliple categories in all_info            
            view_questions = ViewQuestions.objects.filter(view__in=category_objs).order_by('display_order').values('question_id').distinct()
            return ([q.get('question_id') for q in view_questions], True)
        else:
            category_questions = Question.objects.filter(accepted=1, category__in=category_objs).values('id').distinct()             
            return ([q.get('id') for q in category_questions], False)

def get_ahj_data(jurisdiction, category, empty_data_fields_hidden, user, question_ids = []):
    placeholder = ",".join(["%s" for id in question_ids]) if question_ids else None
    query_str = '''SELECT * FROM   (
            SELECT
                   website_answerreference.id,
                   website_answerreference.question_id,
                   website_answerreference.value,
                   website_answerreference.file_upload,
                   website_answerreference.create_datetime,
                   website_answerreference.modify_datetime,
                   website_answerreference.jurisdiction_id,
                   website_answerreference.is_current,
                    website_answerreference.is_callout,
                    website_answerreference.approval_status,
                    website_answerreference.creator_id,
                    website_answerreference.status_datetime,
                    website_answerreference.organization_id,
                    website_question.form_type,
                    website_question.answer_choice_group_id,
                    website_question.display_order,
                    website_question.default_value,
                    website_question.reviewed,
                    website_question.accepted,
                    website_question.instruction,
                    website_question.category_id,
                    website_question.applicability_id,
                    website_question.question,
                    website_question.label,
                    website_question.template,
                    website_question.validation_class,
                    website_question.js,
                    website_question.field_attributes,
                    website_question.terminology,
                    website_question.has_multivalues,
                    website_question.qtemplate_id,
                    website_question.display_template,
                    website_question.field_suffix,
                    website_question.migration_type,
                    website_question.state_exclusive,
                    website_question.description,
                    website_question.support_attachments,
                    website_questioncategory.name,
                    website_questioncategory.description AS cat_description,
                    website_questioncategory.accepted AS cat_accepted,
                    website_questioncategory.display_order AS cat_display_order,
                    auth_user.username,
                    auth_user.first_name,
                    auth_user.last_name,
                    auth_user.is_staff,
                    auth_user.is_active,
                    auth_user.is_superuser,
                    website_userdetail.display_preference
            FROM
                    website_answerreference,
                    website_question,
                    website_questioncategory,
                    auth_user,
                    website_userdetail
            WHERE
                    website_answerreference.jurisdiction_id = %s
            '''

    if placeholder:
        query_str += '''AND website_question.id IN ('''+ placeholder + ''')'''
    
    query_str += '''
                    AND website_question.id = website_answerreference.question_id
                    AND website_questioncategory.id = website_question.category_id
                    AND auth_user.id = website_answerreference.creator_id
                    AND website_userdetail.user_id = website_answerreference.creator_id
                    AND website_question.accepted = '1'
                    AND (
                            (
                                    (
                                            website_answerreference.approval_status = 'A'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime = (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    ) OR (
                                            website_answerreference.approval_status = 'P'
                                            AND website_question.has_multivalues = '0'
                                            AND website_answerreference.create_datetime != (
                                                    SELECT
                                                            MAX(create_datetime)
                                                    FROM
                                                            website_answerreference AS temp_table
                                                    WHERE
                                                            temp_table.question_id = website_answerreference.question_id
                                                            AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                            AND temp_table.approval_status = 'A'
                                            )
                                    )
                            ) OR (
                                    (
                                            website_question.has_multivalues = '1'
                                            AND (
                                                    website_answerreference.approval_status = 'A'
                                                    OR website_answerreference.approval_status = 'P'
                                            )
                                    )
                            ) OR (
                                    website_answerreference.approval_status = 'P'
                                    AND (
                                            SELECT
                                                    MAX(create_datetime)
                                            FROM
                                                    website_answerreference AS temp_table
                                            WHERE
                                                    temp_table.question_id = website_answerreference.question_id
                                                    AND temp_table.jurisdiction_id = website_answerreference.jurisdiction_id
                                                    AND temp_table.approval_status = 'A'
                                    ) IS NULL
                            )
                    )
            ) AS sorting_table
            '''
    if empty_data_fields_hidden != 1:
        query_str += '''
    UNION SELECT
                   NULL AS id,
                   website_question.id AS question_id,
                   NULL AS value,
                   NULL AS file_upload,
                   NULL AS create_datetime,
                   NULL AS modify_datetime,
                   NULL AS jurisdiction_id,
                   NULL AS is_current,
                    NULL AS is_callout,
                    NULL AS approval_status,
                    NULL AS creator_id,
                    NULL AS status_datetime,
                    NULL AS organization_id,
                    website_question.form_type,
                    website_question.answer_choice_group_id,
                    website_question.display_order,
                    website_question.default_value,
                    website_question.reviewed,
                    website_question.accepted,
                    website_question.instruction,
                    website_question.category_id,
                    website_question.applicability_id,
                    website_question.question,
                    website_question.label,
                    website_question.template,
                    website_question.validation_class,
                    website_question.js,
                    website_question.field_attributes,
                    website_question.terminology,
                    website_question.has_multivalues,
                    website_question.qtemplate_id,
                    website_question.display_template,
                    website_question.field_suffix,
                    website_question.migration_type,
                    website_question.state_exclusive,
                    website_question.description,
                    website_question.support_attachments,
                    website_questioncategory.name,
                    website_questioncategory.description AS cat_description,
                    website_questioncategory.accepted AS cat_accepted,
                    website_questioncategory.display_order AS cat_display_order,
                    NULL AS username,
                    NULL AS first_name,
                    NULL AS last_name,
                    NULL AS is_staff,
                    NULL AS is_active,
                    NULL AS is_superuser,
                    NULL AS display_preference
    FROM
            website_question,
            website_questioncategory
    WHERE
            website_questioncategory.id = website_question.category_id
            '''
              
        if placeholder:
            query_str += '''AND website_question.id IN ('''+ placeholder + ''') '''
    
        query_str += '''                
                    AND website_questioncategory.accepted = '1' 
                    AND website_question.accepted = '1'
            '''
                
    query_str +='''
    ORDER BY
            cat_display_order ASC,
            category_id ASC,
            display_order ASC,
            question_id ASC,
            approval_status ASC,
            create_datetime DESC,
            id DESC;
    '''
    #print(empty_data_fields_hidden)
    query_params = []
    query_params.append(jurisdiction.id)
    if question_ids:
        for question_id in question_ids:
            query_params.append(question_id)
        if empty_data_fields_hidden != 1:                
            for question_id in question_ids:
                query_params.append(question_id)
                      
    cursor = connections['default'].cursor()
    cursor.execute(query_str, query_params)
    records = dictfetchall(cursor)

    return records
