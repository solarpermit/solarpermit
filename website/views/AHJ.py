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
from website.utils.paginationUtil import PaginationUtil
from website.utils.geoHelper import GeoHelper
from website.models import Jurisdiction, Zipcode, UserSearch, Question, AnswerReference, AnswerAttachment, OrganizationMember, QuestionCategory, Comment, UserCommentView, Template, ActionCategory, JurisdictionContributor, Action, UserDetail, OrganizationMember
from website.models import View, ViewQuestions, ViewOrgs
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from website.utils.miscUtil import UrlUtil
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.datetimeUtil import DatetimeHelper
from django.contrib.auth.models import User
import json
import datetime

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
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js', data, '')
            dajax.script(script)
            #script = requestProcessor.decode_jinga_template(request,'website/blocks/comments_list.js', data, '')
            #dajax.script(script)
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
            script =  requestProcessor.decode_jinga_template(request,'website/jurisdictions/create_comment.js', data, '')
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
            comment.entity_name = entity_name
            comment.entity_id = entity_id
            comment.user = user
            comment.comment_type = comment_type
            comment.comment = comment_text
            if parent_comment != '':
                parent = Comment.objects.get(id = parent_comment)
                comment.parent_comment = parent
            comment.save()
            
            userviews = UserCommentView.objects.filter(user = user, jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id)
            userview = userviews[0]
            userview.last_comment = comment
            userview.comments_count = Comment.objects.filter(jurisdiction = jurisdiction, entity_name = entity_name, entity_id = entity_id).count()
            userview.view_datetime = datetime.datetime.now()
            userview.save()
            
            
            dajax.script('controller.closeSecondDialog();')
            dajax.script('controller.postRequest("/jurisdiction_comment/", {ajax: "open_jurisdiction_comment", jurisdiction_id:'+str(jurisdiction_id)+', entity_id: "'+str(entity_id)+'", entity_name: "'+str(entity_name)+'", comments_changed: "yes"});')

            data = {}
            answer = AnswerReference.objects.get(id=entity_id) 
            validation_util_obj = FieldValidationCycleUtil()                  
     
            question = answer.question
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)  

            for key in question_content.keys():
                data[key] = question_content.get(key)
            
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
       
            dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)
            dajax.script('controller.updateUrlAnchor("#add_comment");')
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)                
                
        if ajax =='reply_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid)            
            data['comment'] = comment
            body = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.html', data, '')
            script = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.js', data, '')
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            dajax.script(script)
            
        
        if ajax == 'cancel_reply':
            cid = requestProcessor.getParameter('cid')
            body = '<a class="smallbutton" href="#" onClick="controller.postRequest(\'/jurisdiction_comment/\', {ajax: \'reply_comment\', cid: '+str(cid)+'});return false;">Reply</a><a class="smallbutton" href="#">Flag</a>'
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            
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
            dajax.assign('#show_commnet_div', 'innerHTML', '<a id="id_a_hide" href="#"><img src="/media/images/arrow_down.png" style="vertical-align:middle;" alt="Hide old comments"> Hide old comments </a>')
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/jurisdiction_comment.js', data, '')
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
    
def view_sc_AHJ(request, id):
    requestProcessor = HttpRequestProcessor(request)   
    jurisdiction = Jurisdiction.objects.get(id=id)  
             
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
    
def view_unincorporated_AHJ(request, id):
    requestProcessor = HttpRequestProcessor(request)   
    dajax = Dajax()
    ajax = requestProcessor.getParameter('ajax')
    user = request.user
    jurisdiction = Jurisdiction.objects.get(id=id)  
             
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
            script = requestProcessor.decode_jinga_template(request,'website/blocks/create_ucomment.js', data, '')
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
            dajax.assign('.ul-level-1','innerHTML', body) 
        
        if ajax =='reply_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid)            
            data['comment'] = comment
            body = requestProcessor.decode_jinga_template(request,'website/blocks/reply_ucomment_form.html', data, '')
            script = requestProcessor.decode_jinga_template(request,'website/blocks/reply_comment_form.js', data, '')
            dajax.assign('#button-div-'+str(cid),'innerHTML', body) 
            dajax.script(script)
        
        if ajax == 'flag_comment':
            cid = requestProcessor.getParameter('cid')
            comment = Comment.objects.get(id = cid) 
            comment.approval_status = 'F'
            comment.save()
            
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
            jurisdiction = Jurisdiction.objects.get(id=name)
        except:
            jurisdiction = None
        if jurisdiction != None:
            if category == 'all_info':
                return redirect('/jurisdiction/'+str(jurisdiction.name_for_url) + '/')
            else:
                return redirect('/jurisdiction/'+str(jurisdiction.name_for_url)+'/'+category)
    '''
    jurisdictions = []
    name = str(name).strip().replace('+', ' ')
    array_name = name.split('-')
    if len(array_name) == 2:
        name = str(BeautifulSoup(array_name[0],convertEntities=BeautifulSoup.HTML_ENTITIES))
        state = array_name[1]     
        city_type = ['CI', 'CINP', 'IC', 'U', 'SCFO', 'O', 'S']
        jurisdictions = Jurisdiction.objects.filter(name__iexact=name, state__iexact=state, jurisdiction_type__in=(city_type))             
        
    elif len(array_name) >= 3:
        array_last_index = len(array_name)-1
        array_2nd_to_last_index = len(array_name)-2
        county_equivalent = array_name[array_2nd_to_last_index]
        state = array_name[array_last_index]
      
        
        if county_equivalent.lower() == 'county' or county_equivalent.lower() == 'parish' or county_equivalent.lower() == 'borough':
            del array_name[array_last_index]  
            del array_name[array_2nd_to_last_index]
            type = ['CO','SC', 'CONP']
        else:
            del array_name[array_last_index] 
            type = ['CI', 'CINP', 'IC', 'U', 'SCFO', 'O', 'S']   
            
        name = ''
        for name_part in array_name:
            name = name + '-' + name_part
                
        name = name.lstrip('-')
        name = str(BeautifulSoup(name,convertEntities=BeautifulSoup.HTML_ENTITIES))
        jurisdictions = Jurisdiction.objects.filter(name__iexact=name, state__iexact=state, jurisdiction_type__in=type)  #, jurisdiction_type__exact=jurisdiction_type
                
                                 
    else:
        print 'not enough information to get the jur id'
    '''    

    jurisdictions = Jurisdiction.objects.filter(name_for_url__iexact=name)

    if len(jurisdictions) >= 1:
        jurisdiction = jurisdictions[0]
        id = jurisdiction.id
        
        if jurisdiction.jurisdiction_type == 'U' or jurisdiction.jurisdiction_type == 'CONP' or jurisdiction.jurisdiction_type == 'CINP':
            return view_unincorporated_AHJ(request, id)
        elif jurisdiction.jurisdiction_type == 'SC':
            return view_sc_AHJ(request, id)
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
                    else:   # views
                        if user.is_authenticated():
                            login_user = User.objects.get(id=user.id)
                            if login_user.is_staff or login_user.is_superuser or ('accessible_views' in request.session and category in request.session['accessible_views']):
                                pass  # logged in user, he is either a staff or superuser, or this user has access to the view per his organization membership
                            else:
                                return redirect('/jurisdiction/'+str(jurisdiction.name_for_url)+'/')   # in the case of a non-question category, dump him at the general category    
                        else:
                            return redirect('/')                           
                        
            return view_AHJ(request, id, category)
        
    else:
        print 'bad identification.  cannot find the jurisdiction'
        return redirect('/')
    
    return redirect('/') #
    
def view_AHJ(request, id, category='all_info'):
    
    requestProcessor = HttpRequestProcessor(request)        
    data = {}  
    dajax = Dajax()
    validation_util_obj = FieldValidationCycleUtil()  
    
    # to turn off the top nav bar
    data['nav'] = 'no'   
    data['current_nav'] = 'browse'    
    data['home'] = '/'       
    data['page'] = 'AHJ'
    data['unauthenticated_page_message'] = "The information on this page is available to all visitors of the National Solar Permitting Database.  If you would like to add information to the database and interact with the solar community, please sign in below or "
    data['authenticated_page_message'] = 'See missing or incorrect information? Mouse over a field and click the blue pencil to add or edit the information.'
    data[category] = ' active'      # to set the active category in the left nav
    #question_category_objs = QuestionCategory.objects.filter(name__iexact=category)  
    #question_category_obj = question_category_objs[0]       # if this causes a problem, it's your fault in setting up the data.
    #data['category_obj'] = question_category_obj 
    
    

          
    jurisdiction = Jurisdiction.objects.get(id=id)
    datetime_util_obj = DatetimeHelper(jurisdiction.last_contributed)
    data['last_contributed_date'] = datetime_util_obj.showStateTimeFormat(jurisdiction.state)      
        
    # to determine the last contributor's organization
    organization = None
    
    try:
        contributor = jurisdiction.last_contributed_by
    except:
        contributor = None
        
    if contributor != None:
        organization_members = OrganizationMember.objects.filter(user=contributor, organization__status = 'A')
        if len(organization_members) > 0:
            organization = organization_members[0].organization
    '''       
    if organization != None: 
        data['last_contributed_by'] = organization.name
    elif contributor:
        data['last_contributed_by'] = contributor       # this is a user object
    else:
        data['last_contributed_by'] = ''
    '''
    data['last_contributed_by']  = contributor        
    data['state'] = jurisdiction.state
    data['state_long_name'] = dict(US_STATES)[data['state']]  
    
    data['city'] = jurisdiction.city   
    data['jurisdiction_type'] = jurisdiction.get_jurisdiction_type()              
    data['jurisdiction_id'] = jurisdiction.id   
    data['jurisdiction'] = jurisdiction      
    
    data['google_api_key'] = django_settings.GOOGLE_API_KEY     # may need to move this to where ever google map connection is initialized.
    
    layout = requestProcessor.getParameter('layout')
    q_layout = requestProcessor.getParameter('q')   
    
    if layout == None or layout == '':
        if q_layout != None and q_layout != '':
            layout = q_layout

    data['is_print'] = False
    if layout !=None and layout == 'print':
        data['is_print'] = True
        
    user = request.user
    data['user'] = user
    if user.is_authenticated() and jurisdiction != None:
        save_recent_search(user, jurisdiction)
    
    '''    
    jur_url = '/jurisdiction/' + str(jurisdiction.name_for_url)
    jur_url_with_slash = jur_url + '/'
    if str(request.META.get('PATH_INFO')) != jur_url and str(request.META.get('PATH_INFO')) != jur_url_with_slash:
        data['canonical_url'] = django_settings.SITE_URL+'/' + jurisdiction.name_for_url + '/'
    elif len(request.GET) > 0:
        data['canonical_url'] = django_settings.SITE_URL+'/' + jurisdiction.name_for_url + '/'
    '''    
            
    # ajax-related
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        question_id = requestProcessor.getParameter('question_id')
        data['question_id'] = question_id
        jurisdiction_id = requestProcessor.getParameter('jurisdiction_id')
        data['jurisdiction_id'] = jurisdiction_id
        
        if jurisdiction_id != None:
            jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id) 
            data['jurisdiction_type'] =  jurisdiction.get_jurisdiction_type()
            data['state'] = jurisdiction.state
            data['city'] = jurisdiction.city               
        else:
            data['jurisdiction_type'] = ''
            
            
        if question_id != None:
            question = Question.objects.get(id=question_id)
        else:
            question = None
                                    
        if (ajax == 'get_add_form'):  
            data['mode'] = 'add'
            
            data['form_field'] = {}
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
                
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'get_edit_form'):
            data['mode'] = 'edit'
            answer_id = requestProcessor.getParameter('answer_id')           
            answer_for_edit = AnswerReference.objects.get(id=answer_id)       

            data['values'] = {} 
            form_field_data = validation_util_obj.get_form_field_data(jurisdiction, question)
            for key in form_field_data:
                data[key] = form_field_data[key]    
                
            data['values'] = {}                
            answer = json.loads(answer_for_edit.value) 
            for key in answer:
                data[key] = answer[key]  
                
            #data['city'] =  jurisdiction.city
            #data['state'] = jurisdiction.state                                  
 
            data['answer_id'] = answer_id   
            print data['question_template']
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

            #if 'js' in data and data['js'] != None and data['js'] != '':
            for js in data['js']:
                script = requestProcessor.decode_jinga_template(request, "website/form_fields/"+js, data, '')
                dajax.script(script)         
   
            return HttpResponse(dajax.json())         
                    
        if ajax == 'get_question_content_1st' or ajax == 'get_question_content':     
      
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)  

            for key in question_content.keys():
                data[key] = question_content.get(key)
                
            if request.user.is_authenticated():
                view_questions_obj = ViewQuestions()
                quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)
                data['quirk_number_of_questions'] = 0    
                if 'view_questions' in quirks:
                    data['quirk_number_of_questions'] = len(quirks['view_questions'])        
            
                quirk_questions = []
                if data['quirk_number_of_questions'] > 0:
                    for quirk in quirks['view_questions']:
                        quirk_questions.append(quirk.question_id)
                        
                data['quirk_questions'] = quirk_questions
                
                data['user_number_of_favorite_fields'] = 0    
                user_obj = User.objects.get(id=request.user.id)
                if user_obj != None:
                    user_favorite_fields = view_questions_obj.get_user_favorite_fields(user_obj)
                           
                    if 'view_questions' in user_favorite_fields:
                        data['user_number_of_favorite_fields'] = len(user_favorite_fields['view_questions'])        
                 
                favorite_questions = []
                if data['user_number_of_favorite_fields'] > 0:
                    for favorite_question in user_favorite_fields['view_questions']:
                        favorite_questions.append(favorite_question.question_id)    
                        
                data['favorite_questions'] = favorite_questions                
                        
                    
                data['category'] = category
                                            
            if request.user.is_authenticated():
                if data['has_no_answer'] == False:
                    body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
                else:
                    body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated_no_data.html', data, '')
            else:         
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_unauthenticated.html', data, '')        

            dajax.assign('#div_question_content_'+str(question_id),'innerHTML', body)
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)
            
            if ajax == 'get_question_content':     
                # for google map
                if question.id == 4:
                    str_addr = validation_util_obj.get_addresses_for_map(jurisdiction)
                    data['str_address'] = str_addr
                    dajax.script("load_google_map('"+str(str_addr)+"')")
                    
            dajax.script('$("#qa_'+str(question_id)+'_data .cancel_btn").tooltip({track: true});$("#qa_'+str(question_id)+'_data .edit_btn").tooltip({track: true});')      
              
            return HttpResponse(dajax.json())          
        
        if (ajax == 'suggestion_submit'):     
            answers = {} 
            field_prefix = 'field_'
            jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)    
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
                        
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)            
            
            for key in question_content.keys():
                data[key] = question_content.get(key)               
                            
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
            dajax.assign('#div_question_content_'+str(question_id),'innerHTML', body)
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)
            
            # for google map
            if question.id == 4:
                str_addr = validation_util_obj.get_addresses_for_map(jurisdiction)
                data['str_address'] = str_addr
                dajax.script("load_google_map('"+str(str_addr)+"')")
                
            return HttpResponse(dajax.json())  
        
        if (ajax == 'suggestion_edit_submit'):     
            answers = {} 
            answer_id = requestProcessor.getParameter('answer_id')
            field_prefix = 'field_'
            jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)    
            question = Question.objects.get(id=question_id)              
            answers = requestProcessor.get_form_field_values(field_prefix)

            for key, answer in answers.items():
                if answer == '':
                    del answers[key]
                    
            process_answer(answers, question, jurisdiction, request.user, answer_id) 
            
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)           
            
            for key in question_content.keys():
                data[key] = question_content.get(key)               
                            
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
            dajax.assign('#div_question_content_'+str(question_id),'innerHTML', body)            
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)
          
            # for google map
            if question.id == 4:
                str_addr = validation_util_obj.get_addresses_for_map(jurisdiction)
                data['str_address'] = str_addr
                dajax.script("load_google_map('"+str(str_addr)+"')")
                
            return HttpResponse(dajax.json())  
        
        
        if (ajax == 'vote'):
            #data = {}
            requestProcessor = HttpRequestProcessor(request)
            dajax = Dajax()
                  
            ajax = requestProcessor.getParameter('ajax')
            if (ajax != None):
                if (ajax == 'vote'):
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
                            #data['action'] = 'refresh_ahj_qa'
                            #body = validation_util_obj.get_question_answers_display_data(request, answer.jurisdiction, answer.question, data)    
                            #print 'here :: ' + str(answer.question_id)    
                            data['jurisdiction'] = answer.jurisdiction

                            question = answer.question                                
                            data['this_question'] = question            
                            
                            question_content = validation_util_obj.get_AHJ_question_data(request, data['jurisdiction'], question, data)  
                                
                            
                            for key in question_content.keys():
                                data[key] = question_content.get(key)                                  
                                            
                            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
                            dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)            
                            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
                            dajax.script(script)
                                                 
                            
                            dajax.script("show_hide_vote_confirmation('"+entity_id+"');")
                                        
                    elif feedback == 'registered_with_changed_status':
                        
                        if entity_name == 'requirement':
                            
                            answer = AnswerReference.objects.get(id=entity_id)   
                            
                            data['jurisdiction'] = answer.jurisdiction                            
                            #data['action'] = 'refresh_ahj_qa'  
                            #body = validation_util_obj.get_question_answers_display_data(request, answer.jurisdiction, answer.question, data)    
                            #print 'here :: ' + str(answer.question_id)    
                            #dajax.assign('#div_'+str(answer.question_id),'innerHTML', body)
                            
                            question = answer.question
                            data['this_question'] = question            
                            
                            question_content = validation_util_obj.get_AHJ_question_data(request, data['jurisdiction'], data['this_question'], data)  
                              
                            
                            for key in question_content.keys():
                                data[key] = question_content.get(key)                                             
                                            
                            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
                            dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)            
                            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
                            dajax.script(script)
                            
                            # for google map
                            if question.id == 4:
                                str_addr = validation_util_obj.get_addresses_for_map(data['jurisdiction'])
                                data['str_address'] = str_addr
                                dajax.script("load_google_map('"+str(str_addr)+"')")                              
                            
                            terminology = question.terminology
                            if terminology == None or terminology == '':
                                terminology = 'value'                       
                              
                            if answer.approval_status == 'A':                          
                                dajax.script("controller.showMessage('"+str(terminology)+" approved.  Thanks for voting.', 'success');")  
                            elif answer.approval_status == 'R':
                                dajax.script("controller.showMessage('"+str(terminology)+" rejected. Thanks for voting.', 'success');") 
                            dajax.script("show_hide_vote_confirmation('"+entity_id+"');") 
                                
                            if category == 'all_info':          
                                question_categories = QuestionCategory.objects.filter(accepted=1)
                                #data['category'] = 'All categories'
                                data['category_name'] = 'All categories'
                            else:
                                question_categories = QuestionCategory.objects.filter(name__iexact=category)
                                #data['category'] = category
                                if len(question_categories) > 0:
                                    data['category_name'] = question_categories[0].description
                                else:
                                    data['category_name'] = ''                                
            
                            data['top_contributors'] = validation_util_obj.get_top_contributors(data['jurisdiction'], question_categories)  
                            body = requestProcessor.decode_jinga_template(request,'website/blocks/top_contributors.html', data, '')   
                            dajax.assign('#top_contributors','innerHTML', body)                                  


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
                        dajax.script('confirm_rejected();')
                    #dajax.script("controller.showMessage('Your feedback has been sent and will be carefully reviewed.', 'success');")                 
                    
                    return HttpResponse(dajax.json())                     
        
        if (ajax == 'cancel_suggestion'):
            user = request.user
            entity_id = requestProcessor.getParameter('entity_id') 
            #entity_name = requestProcessor.getParameter('entity_name') 
            
            #if entity_name == 'requirement':
            answer = AnswerReference.objects.get(id=entity_id) 
            answer.approval_status = 'C'
            answer.status_datetime = datetime.datetime.now()
            answer.save()
                
            question = answer.question
            jurisdiction = answer.jurisdiction                           
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)             
            
            for key in question_content.keys():
                data[key] = question_content.get(key)               
                            
            if data['has_no_answer'] == True:
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated_no_data.html', data, '')      
            else:
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
                
            dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)                     
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)
            
            # for google map
            if question.id == 4:
                str_addr = validation_util_obj.get_addresses_for_map(jurisdiction)
                data['str_address'] = str_addr
                dajax.script("load_google_map('"+str(str_addr)+"')")              
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'approve_suggestion'):

            user = request.user
            entity_id = requestProcessor.getParameter('entity_id') 

            answer = AnswerReference.objects.get(id=entity_id) 
            answer.approval_status = 'A'
            answer.status_datetime = datetime.datetime.now()
            answer.save()
   
            question = answer.question               
            jurisdiction = answer.jurisdiction  
            data['this_question'] = question            
            
            question_content = validation_util_obj.get_AHJ_question_data(request, jurisdiction, question, data)  
             
            
            for key in question_content.keys():
                data[key] = question_content.get(key)     
                            
            body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content_authenticated.html', data, '')
            dajax.assign('#div_question_content_'+str(question.id),'innerHTML', body)
            script = requestProcessor.decode_jinga_template(request,'website/jurisdictions/AHJ_question_content.js', data, '')
            dajax.script(script)
            
            '''
            question_categories = QuestionCategory.objects.filter(name__exact=question_category.name)
            data['top_contributors'] = validation_util_obj.get_top_contributors(answer.jurisdiction, question_categories)  
            body = requestProcessor.decode_jinga_template(request,'website/blocks/top_contributors.html', data, '')   
            dajax.assign('#top_contributors','innerHTML', body)            
            '''   
                
            if category == 'all_info':          
                question_categories = QuestionCategory.objects.filter(accepted=1)
                #data['category'] = 'All categories'
                data['category_name'] = 'All categories'
            else:
                question_categories = QuestionCategory.objects.filter(name__iexact=category)
                #data['category'] = category
                if len(question_categories) > 0:
                    data['category_name'] = question_categories[0].description
                else:
                    data['category_name'] = ''                


            data['jurisdiction'] = jurisdiction
            data['top_contributors'] = validation_util_obj.get_top_contributors(jurisdiction, question_categories)  
            body = requestProcessor.decode_jinga_template(request,'website/blocks/top_contributors.html', data, '')   
            dajax.assign('#top_contributors','innerHTML', body)                
            
            # for google map
            if question.id == 4:
                str_addr = validation_util_obj.get_addresses_for_map(jurisdiction)
                data['str_address'] = str_addr
                dajax.script("load_google_map('"+str(str_addr)+"')")   
                           
            return HttpResponse(dajax.json())         
                                                    
        if (ajax == 'validation_history'):
            caller = requestProcessor.getParameter('caller')
            entity_name = requestProcessor.getParameter('entity_name')              
            entity_id = requestProcessor.getParameter('entity_id')   
            data = validation_util_obj.get_validation_history(entity_name, entity_id)
            data['destination'] = requestProcessor.getParameter('destination')   
            
            if caller == None:
                params = 'zIndex: 8000'
            elif caller == 'dialog':
                params = 'zIndex: 12000'
                
            if data['destination'] == None:
                data['destination']  = ''
                            
            if data['destination'] == 'dialog':
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/validation_history_dialog.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)       
                dajax.script('controller.showModalDialog("#fancyboxformDiv");')                
            else:
                body = requestProcessor.decode_jinga_template(request,'website/jurisdictions/validation_history.html', data, '')                 
                dajax.assign('#validation_history_div_'+entity_id,'innerHTML', body)
                #dajax.assign('.info_content','innerHTML', body)
                #dajax.script("controller.showInfo({target: '#validation_history_"+entity_id+"', "+params+"});")          
                        
            return HttpResponse(dajax.json())    
        
        
        if (ajax == 'add_to_views'):
            view_obj = None
            user = request.user
            entity_name = requestProcessor.getParameter('entity_name') 
      
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
                dajax.assign('#quirk_'+str(question.id),'innerHTML', 'Added to quirks')                    
                        
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
                    dajax.assign('#favorite_field_'+str(question.id),'innerHTML', 'Added to favorite fields')  
            
            return HttpResponse(dajax.json())  
        
        if (ajax == 'remove_from_views'):
            view_obj = None
            user = request.user
            entity_name = requestProcessor.getParameter('entity_name') 
      
            if entity_name == 'quirks':
                view_objs = View.objects.filter(view_type = 'q', jurisdiction = jurisdiction)
                if len(view_objs) > 0:
                    view_obj = view_objs[0]
                    
            elif entity_name == 'favorites':
                view_objs = View.objects.filter(view_type = 'f', user = request.user)
                if len(view_objs) > 0:
                    view_obj = view_objs[0]          
            
            if view_obj != None:
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
                        
                dajax.assign('#div_question_content_'+str(question.id),'innerHTML', '') 
            
            return HttpResponse(dajax.json())
        
        if (ajax == 'open_attachement'):                           
            answer_id = requestProcessor.getParameter('answer_id')             
            answer = AnswerReference.objects.get(id=answer_id)
            
            aats = AnswerAttachment.objects.filter(answer_reference = answer)
            
            data['attachements'] = aats
            data['answer1'] = answer
            
            validation_util_obj = FieldValidationCycleUtil()
            category_name = 'VoteRequirement' 
            vote_info = validation_util_obj.get_jurisdiction_voting_info_by_category(category_name, answer.jurisdiction, answer.question.category, answer.question)
            terminology = validation_util_obj.get_terminology(answer.question)  
            #question_content = validation_util_obj.get_AHJ_question_data(request, update.jurisdiction, update.question, data)  
            question_content = validation_util_obj.get_authenticated_displayed_content(request, answer.jurisdiction, answer.question, vote_info, [answer], terminology)
            for key in question_content.keys():
                data[key] = question_content.get(key)
                
            body = requestProcessor.decode_jinga_template(request,'website/blocks/attachement_block.html', data, '')                 
            dajax.assign('#qa_'+answer_id+'_attachements','innerHTML', body)
            
            script = requestProcessor.decode_jinga_template(request,'website/blocks/attachement_block.js', data, '')
            dajax.script(script)
            
            dajax.script('$("#qa_'+answer_id+'_attachements").show("slow");');
            
        if (ajax == 'save_attachements'):
            answer_id = requestProcessor.getParameter('answer_id')             
            answer = AnswerReference.objects.get(id=answer_id)
            
            file_names = requestProcessor.getParameter('filename') 
            file_store_names = requestProcessor.getParameter('file_store_name') 
            if (file_names != '' and file_names != None) and (file_store_names != '' and file_store_names != None):
                file_name_list = file_names.split(',')
                file_store_name_list = file_store_names.split(',')
                for i in range(0, len(file_name_list)):
                    aac = AnswerAttachment()
                    aac.answer_reference = answer
                    aac.file_name = file_name_list[i]
                    store_file = '/upfiles/answer_ref_attaches/'+file_store_name_list[i]
                    aac.file_upload = store_file
                    aac.creator = user
                    aac.save()
            dajax.script('$("#qa_'+answer_id+'_attachements").hide("slow");'); 
            attachement_count = len(AnswerAttachment.objects.filter(answer_reference = answer))
            dajax.assign('#attachement_link','innerHTML', 'Attachments('+str(attachement_count)+')')
            
        return HttpResponse(dajax.json()) #don't return here yet, more ajax action at the end
            
            
              
    data['question_content'] = {}
    data['question_categories'] = {}    
    data['questions'] = {}
    data['custom_questions'] = {}
    template_obj = Template()
    jurisdiction_templates = template_obj.get_jurisdiction_question_templates(jurisdiction)

    if category == 'all_info':
        question_categories = QuestionCategory.objects.filter(accepted=1).order_by('display_order')
    else:
        question_categories = QuestionCategory.objects.filter(name__iexact=category, accepted=1)

    empty_data_fields_hidden = None
    data['show_top_contributors'] = True 
    data['enable_custom_questions'] = True
    data['show_google_map'] = False
    if len(question_categories) > 0:

        empty_data_fields_hidden = requestProcessor.getParameter('empty_data_fields_hidden')        
        if empty_data_fields_hidden != None:
            data['empty_data_fields_hidden'] = int(empty_data_fields_hidden)
        else:
            if 'empty_data_fields_hidden' in request.session:
                data['empty_data_fields_hidden'] = request.session['empty_data_fields_hidden']
            else:
                data['empty_data_fields_hidden'] = None     # to be determineed by various factors in susbsequent codes
                

    

                
        question_obj = Question()
                   
        question_category_objs = []
        categories_with_answers = {}
        for question_category in question_categories:
            question_category_obj = {}
            question_category_obj['question_category'] = question_category
            questions = Question.objects.filter(category=question_category, accepted=1, qtemplate__in=jurisdiction_templates).order_by('display_order')
            #question_category_obj['questions'] = question_obj.get_questions_by_category(templates, question_category.id)
            
            questions_with_answers = {}
            if data['empty_data_fields_hidden'] == 1 or data['empty_data_fields_hidden'] == None:
                print 'category id :: ' + str(question_category.id)
                answers = AnswerReference.objects.filter(jurisdiction = jurisdiction, question__category__exact=question_category, approval_status__in=('A', 'P'))
                print 'len(anssers) :: ' + str(len(answers))
                if len(answers) > 0:
                    for answer in answers:
                        questions_with_answers[answer.question_id] = answer.question_id
                        
                    categories_with_answers[question_category.id] = question_category.id
                    if data['empty_data_fields_hidden'] == None:
                        data['empty_data_fields_hidden'] = 1
                        
                else:
                    if data['empty_data_fields_hidden'] == None:
                        data['empty_data_fields_hidden'] = 0
                        
                    
            current_questions = []
            for question in questions:
                current_questions.append(question.id)
                if question.id == 4:
                    data['show_google_map'] = True
                    
            question_category_obj['questions'] = questions
            question_category_obj['current_questions'] = current_questions
            question_category_obj['questions_with_answers'] = questions_with_answers            
            question_category_objs.append(question_category_obj)
            
        data['question_categories'] = question_category_objs
        data['categories_with_answers'] = categories_with_answers        
        data['non_question_categories'] = False    
        
        if data['empty_data_fields_hidden'] == 1 and len(categories_with_answers) == 0:
            #print 'len(categories_with_answers) :: ' + str(len(categories_with_answers))
            data['show_top_contributors'] = False   
            
        if data['empty_data_fields_hidden'] == 1:
            data['enable_custom_questions'] = False                   

    else: # no real question category => view
        question_category_objs = []
        
        if category == 'favorite_fields':
            views = View.objects.filter(user = user, view_type__exact='f')    
            view_title = 'Favorite Fields'        
        elif category == 'quirks':
            views = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='q')
            view_title = 'Quirks'
        else:
            views = View.objects.filter(name__iexact=category)  # we work with one view per ahj content, not like muliple categories in all_info
            view_title = ''
        
        if len(views) >= 1:
            view = views[0]

            vquestions = ViewQuestions.objects.filter(view = view).order_by('display_order')

                
            question_category_obj = {}   
            question_category_obj['question_category'] = view
            
            questions = []
            for vquestion in vquestions:
                questions.append(vquestion.question)       
                if vquestion.question.id == 4:
                    data['show_google_map'] = True                     
                        
            current_questions = []
            for question in questions:
                current_questions.append(question.id)
            question_category_obj['questions'] = questions
            question_category_obj['current_questions'] = current_questions
            question_category_objs.append(question_category_obj)
            
        else:
            data['view_title'] = view_title
                
        data['question_categories'] = question_category_objs
        data['empty_data_fields_hidden'] = 0
        data['non_question_categories'] = True
        data['enable_custom_questions'] = False
        data['categories_with_answers'] = {}          
        data['show_top_contributors'] = False
        
               
    
    ''''
    question_obj = Question()
    for question_category_obj in question_categories:
        questions = question_obj.get_questions_by_category(templates, question_category_obj.id)   

        data['questions'][question_category_obj.id] = {}
        data['questions'][question_category_obj.id] = questions
    '''
    
    '''
        custom_questions = question_obj.get_custom_fields_by_jurisdiction_by_category(jurisdiction, question_category_obj.id)
        print 'custom_questions: ' + str(custom_questions)

        data['custom_questions'][question_category_obj.id] = {} #why is this here, when the next line erases it???
        data['custom_questions'][question_category_obj.id] = custom_questions        
    '''    
    if category == 'all_info':          
        question_categories = QuestionCategory.objects.filter(accepted=1)
        #data['category'] = 'All categories'
        data['category_name'] = 'All categories'
    else:
        question_categories = QuestionCategory.objects.filter(name__iexact=category)
        #data['category'] = category
        if len(question_categories) > 0:
            data['category_name'] = question_categories[0].description
        else:
            data['category_name'] = ''
        
    data['jurisdiction'] = jurisdiction    
    data['top_contributors'] = validation_util_obj.get_top_contributors(jurisdiction, question_categories)

    # to provide data for the google map
    data['category'] = category
    
    if data['show_google_map'] == True:    
        data['str_address'] = validation_util_obj.get_addresses_for_map(jurisdiction)  
    else:
        data['str_address'] = ''
    

    # check this later                
    template = "website/jurisdictions/AHJ.html"

    if layout !=None and layout == 'print':
        template = 'website/jurisdictions/AHJ_print.html'

    data['layout'] = template  
    
    if data['is_print'] == True:
        data['page_format'] = 'print' 
    else:
        data['page_format'] = 'regular' 
    
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
    

    if 'accessible_views' in request.session:
        data['accessible_views'] = request.session['accessible_views']
    else:
        data['accessible_views'] = []
        
    view_questions_obj = ViewQuestions()
    quirks = view_questions_obj.get_jurisdiction_quirks(jurisdiction)
    
    data['quirk_number_of_questions'] = 0    
    if 'view_id' in quirks:
        data['view_id'] = quirks['view_id']
    else:
        data['view_id'] = None
       
    if 'view_questions' in quirks:
        data['quirk_number_of_questions'] = len(quirks['view_questions'])        

    quirk_questions = []
    if data['quirk_number_of_questions'] > 0:
        for quirk in quirks['view_questions']:
            quirk_questions.append(quirk.question_id)
            
    data['quirk_questions'] = quirk_questions
    
    data['user_number_of_favorite_fields'] = 0    
    if user.is_authenticated():
        user_obj = User.objects.get(id=user.id)
        if user_obj != None:
            user_favorite_fields = view_questions_obj.get_user_favorite_fields(user_obj)
            if 'view_id' in user_favorite_fields:
                data['view_id'] = user_favorite_fields['view_id']
            else:
                data['view_id'] = None
               
            if 'view_questions' in user_favorite_fields:
                data['user_number_of_favorite_fields'] = len(user_favorite_fields['view_questions'])        
     
    favorite_questions = []
    if data['user_number_of_favorite_fields'] > 0:
        for favorite_question in user_favorite_fields['view_questions']:
            favorite_questions.append(favorite_question.question_id)    
            
    data['favorite_questions'] = favorite_questions
    
    if empty_data_fields_hidden != None:
        request.session['empty_data_fields_hidden'] = data['empty_data_fields_hidden']    
        
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_categories_questions.html', data, '') 

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



