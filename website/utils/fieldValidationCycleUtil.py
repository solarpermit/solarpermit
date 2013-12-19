from website.utils.httpUtil import HttpRequestProcessor
from website.models import Jurisdiction, Question, AnswerReference, OrganizationMember, QuestionCategory, User, ActionCategory, Action, Comment, UserCommentView, AnswerAttachment, Organization
from website.utils.datetimeUtil import DatetimeHelper
from website.utils.miscUtil import UrlUtil
import json
import datetime
import operator
from datetime import timedelta, date
from django.conf import settings as django_settings
from website.utils.mathUtil import MathUtil


class FieldValidationCycleUtil():
  

    def get_AHJ_question_data(self, request, jurisdiction, question, data):
        requestProcessor = HttpRequestProcessor(request) 
        question_data = {}
        question_data['jurisdiction'] = jurisdiction        
        question_data['question'] = question   
        question_data['terminology'] = self.get_terminology(question)  
        question_data['question_label'] = self.get_field_label(question, jurisdiction)                               

        answers = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, approval_status__in=('A', 'P')).order_by('approval_status','create_datetime')  
        
        # the followings is to reject any pending answer whose status date is after the approved answer's status date. for only non-multivalue questions.
        if question.has_multivalues == 0:
            approved_answer_status_datetime = None
            pending_answer_rejected = False
            for answer in answers:
                if answer.approval_status == 'A':
                    approved_answer_status_datetime = answer.status_datetime
                    #print 'approve ' + str(approved_answer_status_datetime)
                else:
                    #print 'pending ' + str(answer.status_datetime)
                    if approved_answer_status_datetime != None and answer.status_datetime <= approved_answer_status_datetime:
                        answer.approval_status = 'R'
                        answer.status_datetime = datetime.datetime.now()
                        answer.save()
                        pending_answer_rejected = True
                        #print 'answer status updated'
                        
            if pending_answer_rejected:
                answers = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, approval_status__in=('A', 'P')).order_by('approval_status','create_datetime')             
        
        if (answers != None and len(answers) > 0):  
            question_data['has_suggestions'] = True
        else:       
            question_data['has_suggestions'] = False
                                                          
        if answers != None and len(answers) > 0:
            category_name = 'VoteRequirement'                
            question_data['vote_info'] = self.get_jurisdiction_voting_info_by_category(category_name, jurisdiction, question.category, question)               
            if request.user.is_authenticated():
                content = self.get_authenticated_displayed_content(request, jurisdiction, question, question_data['vote_info'], answers, question_data['terminology'])
            else:
                content = self.get_unauthenticated_displayed_content(request, jurisdiction, question, question_data['vote_info'], answers, question_data['terminology'])
        else:
            if request.user.is_authenticated():
                content = self.get_suggest_a_value(question, question_data['terminology'])
            else:
                content = self.get_login_to_suggest_a_value(question, question_data['terminology'])          

        if content:               
            for content_key in content.keys():
                question_data[content_key] = content.get(content_key)   
            
        return question_data
        
            
    def get_field_label(self, question, jurisdiction):
        if question.label != None and question.label != '':      
            if question.id == 6:
                question_label = "Utility companies associated with [AHJ name]"
            
            question_label = question.label.replace('[AHJ name]', jurisdiction.name)
        else:
            question_label = question.question
            
        return question_label
 
                    
    def get_terminology(self, question):
                     
        if question.terminology == None or question.terminology == '':
            question_terminology = 'value'
        else:
            question_terminology = question.terminology
            
        return question_terminology     
        
    def get_suggest_a_value(self, question, question_terminology):
        content = {}        

        content['prompt'] = 'No info available yet...'
        content['message'] = ''                
        content['answers'] = None      
        
        content['add_btn_value'] = self.get_add_btn_value(question, [], []) 
        
        content['allow_suggest'] = True        
        content['do_not_show_add_button'] = True 
        content['has_no_answer'] = True 
        
        content['show_edit_mode'] = True
                    
        return content              

    def get_login_to_suggest_a_value(self, question, question_terminology):
        content = {}      
        a_or_an = 'a'  
               
        if question_terminology[0] in 'aeiou':
            a_or_an = 'an'
            
        content['prompt'] = 'Please sign in to suggest '+a_or_an+' '+ question_terminology
        content['message'] = ''                
        content['answers'] = None          
        
        content['allow_suggest'] = False        
        content['do_not_show_add_button'] = True 
        content['has_no_answer'] = True
        
        content['show_edit_mode'] = False
        
        return content     
    
    def get_unauthenticated_displayed_content(self, request, jurisdiction, question, vote_info, answers, question_terminology):   
        content = {} 
        approved_answers = []      
        approved_answer_list = []      
        # logic dictates that there should be only one approved value at at time, but in some cases there can be muli

        approved_existed = False
        pending_existed = False

        for answer in answers:
            if answer.approval_status == 'P':
                pending_existed = True
                    
            else:
                approved_existed = True
                approved = {}
                entity_id=answer.id
                approved['answer_content'] = json.loads(answer.value) 
                approved['answer'] = answer
                
                if question.id == 16:
                    fee_info = self.process_fee_structure(approved['answer_content'])
                    for key in fee_info.keys():
                        approved[key] = fee_info.get(key)   
                        print key
                        print approved[key]  
                                    
                if len(vote_info) > 0:
                    if answer.id in vote_info:
                        approved['total_up_votes'] = vote_info[answer.id]['total_up_votes']                 #self.get_voting_tally(action_category, entity_id, jurisdiction, question.category)   # get up dnd down vote counts 
                        approved['total_up_votes'] = vote_info[answer.id]['total_down_votes'] 
                        approved['down_vote_last'] = vote_info[answer.id]['num_consecutive_last_down_votes']               #self.get_entity_last_down_votes(action_category, entity_id, jurisdiction, question.category)
                        if 'last_down_vote_date' in vote_info[answer.id]:
                            approved['last_down_vote_date'] = vote_info[answer.id]['last_down_vote_date']
                        else:
                            approved['last_down_vote_date'] = ''                              #self.get_entity_last_down_vote(action_category, entity_id, jurisdiction, question.category)                   
                    
                    else:
                        approved['total_up_votes'] = 0
                        approved['total_down_votes'] = 0                     
                        approved['down_vote_last'] = 0
                        approved['last_down_vote_date'] = ''
          
                approved['can_vote'] = False
            
                approved_answers.append(approved)
           
            
        if pending_existed == True:
            content['prompt'] = 'There is unverified information available for this field.<br /> Please sign in to see the info and vote on its accuracy.'   
        else:
            content['prompt'] = ''  
            
        if len(approved_answers) > 1:
            if question.has_multivalues != 1:
                approved_answer_list.append(approved_answers[-1])        # multple validated, display only the last one.  the question does not have multiple values.
            else:
                approved_answer_list = list(approved_answers)
        else:
            approved_answer_list = list(approved_answers)
                           
        content['answers'] = approved_answer_list        
        content['allow_suggest'] = False              

        content['do_not_show_add_button'] = True 
        content['has_no_answer'] = False
        content['show_edit_mode'] = False
                    
        return content
    
    def get_question_messages(self, question, answer, existed_pending_answers, existed_approved_answers, count):
        message = ''
        if existed_pending_answers > 1:       
            message += "More than one "+question_terminology +" suggested.  Please vote.<br/>"

        if answer.approval_status == 'P': 
            if answer.creator_id == login_user.id:      # your own suggestion. cannot vote on your own suggestion.                    
                message += 'You suggested a ' + question_terminology  + ' for this field on ' + answer_create_datetime + '.<br>The community must vote on its accuracy or it must remain unchallenged for one week before it is approved.<br/>'
            else:
                message += temp_str + question_terminology  + " was suggested by <a href='#' id='"+div_id+"' onmouseover=\""+onmouseover+"\" onmouseout=\""+onmouseout+"\" >"+user_display_name + "</a> on " + answer_create_datetime + ".<br>Please vote on its accuracy.<br/>"
        else:
            if existed_pending_answers > 0 and message == '':    
                message += 'The previous approved '+ question_terminology  + ' has been challenged.<br/>'  
                            
        return message    
                    
    def get_suggestion_header(self, question, answer, existed_pending_answers, existed_approved_answers, count):
        suggestion_header = ''
        if answer.approval_status == 'P':
            if question.has_multivalues != 1:
                if existed_approved_answers > 0:      # has approved answers   
                    if existed_pending_answers == 1:       # one approved answer and only one suggestion
                        suggestion_header = 'New suggestion'
                    else:                               # one approved answer and multiple suggestion (2 max)
                        suggestion_header = 'New suggestion ' + str(count) 
                else:                                   # NO approved answer   
                    if existed_pending_answers == 1:       # NO approved answer and only one suggestion
                        suggestion_header = ''
                    else:                               # one approved answer and multiple suggestion (no max in num of suggestions)
                        suggestion_header = 'Suggestion ' + str(count)  
            else:
                suggestion_header = ''    # no heading is needed for multivalues items
        else:            
            if question.has_multivalues != 1:
                if existed_pending_answers > 0:     # one approved answer and there are new suggestion
                    suggestion_header = 'Previously approved value'
                    
        return suggestion_header
    
    def get_answer_comments(self, jurisdiction, answer, login_user):
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
    #has answers, uer logged in.
    def get_authenticated_displayed_content(self, request, jurisdiction, question, vote_info, answers, question_terminology):
        content = {}
        allow_suggest = True
        message = ''
        login_user = request.user
        pending_editable_answer_ids = ''
        show_edit_mode = False
        can_still_add = True   
        answer_objs = []
        approved_answer_list = []      
        
        existed_pending_answers = 0 
        existed_approved_answers = 0
        
        for answer in answers:
            if answer.approval_status == 'A':
                existed_approved_answers = existed_approved_answers + 1
            else:
                existed_pending_answers = existed_pending_answers + 1
                    
                
                
        #approved_answers = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, approval_status__exact='A')
        #pending_answers = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, approval_status__exact='P')
        
        if existed_pending_answers > 1:       
            message += "More than one "+question_terminology +" suggested.  Please vote.<br/>"
                        
        count = 0
        for answer in answers:

                       
            answer_obj = {}
            answer_obj['answer_content'] = json.loads(answer.value) 
            answer_obj['answer'] = answer 
            
            if question.id == 16:
                fee_info = self.process_fee_structure(answer_obj['answer_content'])
                for key in fee_info.keys():
                    answer_obj[key] = fee_info.get(key)   
            
            if question.support_attachments == 1:
                answer_obj['attachments'] = AnswerAttachment.objects.filter(answer_reference = answer)
            
            if answer.approval_status == 'P':
                count = count + 1            
            answer_obj['suggestion_header'] = self.get_suggestion_header(question, answer, existed_pending_answers, existed_approved_answers, count)
            comments = self.get_answer_comments(jurisdiction, answer, login_user)
            
            for key in comments.keys():
                answer_obj[key] = comments.get(key)  


            answer_obj['total_up_votes'] = 0
            answer_obj['total_down_votes'] = 0                     
            answer_obj['down_vote_last'] = 0
            answer_obj['last_down_vote_date'] = ''   
                 
            if len(vote_info) > 0:
                if answer.id in vote_info:
                    answer_obj['total_up_votes'] = vote_info[answer.id]['total_up_votes']                 #self.get_voting_tally(action_category, entity_id, jurisdiction, question.category)   # get up dnd down vote counts 
                    answer_obj['total_down_votes'] = vote_info[answer.id]['total_down_votes'] 
                    answer_obj['down_vote_last'] = vote_info[answer.id]['num_consecutive_last_down_votes']               #self.get_entity_last_down_votes(action_category, entity_id, jurisdiction, question.category)
                    if 'last_down_vote_date' in vote_info[answer.id]:
                        answer_obj['last_down_vote_date'] = vote_info[answer.id]['last_down_vote_date']
                    else:
                        answer_obj['last_down_vote_date'] = ''                              #self.get_entity_last_down_vote(action_category, entity_id, jurisdiction, question.category)                   
                    
                                     
         
                                                 
            if answer.approval_status == 'P':
                datetime_util_obj = DatetimeHelper(answer.create_datetime)
                answer_create_datetime= datetime_util_obj.showStateTimeFormat(jurisdiction.state) 
                    
                answer_obj['show_cancel'] = False
                answer_obj['show_edit'] = False
                if answer.creator_id == login_user.id:      # your own suggestion. cannot vote on your own suggestion.
                 
                    answer_obj['can_vote'] = False
                    answer_obj['can_vote_up'] = 'false'
                    answer_obj['can_vote_down'] = 'false'                           
                    can_still_add = False
                    answer_obj['show_edit'] = True                    
                    answer_obj['show_cancel'] = True

                    if answer_obj['total_up_votes'] > 0 or answer_obj['total_down_votes'] > 0:
                        
                        answer_obj['can_edit'] = False
                        answer_obj['can_cancel'] = False    # only the creator can cancel and if no voting has been done yet
                        answer_obj['cancel_msg'] = 'Voting in progress.  You can no longer cancel your suggestion.'
                        answer_obj['edit_msg'] = 'Voting in progress.  You can no longer edit your suggestion.'
                        answer_obj['disable_edit_mode'] = True
                        #pending_editable_answer_ids = pending_editable_answer_ids + str(answer.id) + ' '
                    else:
                      
                        answer_obj['can_edit'] = True
                        answer_obj['can_cancel'] = True     # only the creator can cancel and if no voting has been done yet
                        answer_obj['cancel_msg'] = 'Cancel your suggestion'     
                        answer_obj['edit_msg'] = 'Edit your suggestion'    
                        answer_obj['disable_edit_mode'] = False                      
                        pending_editable_answer_ids = pending_editable_answer_ids + str(answer.id) + ' '
                        show_edit_mode = True   # the creator can no longer cancel or edit because it item has been voted on.

                    if question.has_multivalues == 0:   # by default, the login user can no longer make a suggestion once he has made one.  but if this is a multivalue items he can continue to do so
                        allow_suggest = False

                    message += 'You suggested a ' + question_terminology  + ' for this field on ' + answer_create_datetime + '.<br>The community must vote on its accuracy or it must remain unchallenged for one week before it is approved.<br/>'

                else: 
             
                    answer_obj['can_edit'] = False  
                    answer_obj['can_cancel'] = False        # only the creator can cancel
                    answer_obj['cancel_msg'] = 'You can only cancel your own suggestion.'
                    try:                                    # somebody else's suggestion.  u can vote on it
                        user = User.objects.get(id=answer.creator_id)
                        user_display_name = user.get_profile().get_display_name()
                        user_id = user.id
                    except:
                        user_id = 0
                        user_display_name = 'NA'

                    user_last_vote = self.get_user_last_vote_on_this_item(login_user, 'VoteRequirement', answer.id, jurisdiction, question.category)

                    if answer.id in vote_info:  # this answer has been voted
                        if login_user.id in vote_info[answer.id]['user_last_vote_on_this_item']:                   
                            user_last_vote = vote_info[answer.id]['user_last_vote_on_this_item'][login_user.id]     # the login user's last vote on this item
                        else:
                            user_last_vote = None   # the login user has not voted on this item
                    else:
                        user_last_vote = None       # this answer has no voting yet.                    
                    
                    
                    if user_last_vote != None:
                        if user_last_vote.data == 'Vote: Up':
                            answer_obj['can_vote_up'] = 'false'
                            answer_obj['can_vote_down'] = 'true' 
                        else:
                            answer_obj['can_vote_up'] = 'true'
                            answer_obj['can_vote_down'] = 'false' 
                    else:
                        answer_obj['can_vote_up'] = 'true'
                        answer_obj['can_vote_down'] = 'true'                         
                            
                    answer_obj['can_vote'] = True  
                    
                    if login_user.is_superuser == 1:
                        answer_obj['can_approve'] = True  
                    else:
                        answer_obj['can_approve'] = False  
                        
   
                    div_id="id_"+str(answer.id) 
                    onmouseover="controller.postRequest('/account/', {ajax: 'user_profile_short', user_id: '"+str(user_id)+"',  unique_list_id: '"+str(answer.id)+"'  });" 
                    onmouseout = "document.getElementById('simple_popup_div_on_page').style.display='none';"
                    temp_str = ''
                    if existed_approved_answers > 0:
                        if existed_pending_answers == 1: 
                            temp_str = "A new "
                    else:
                        if existed_pending_answers == 1: 
                            temp_str = 'This ' 
                    
                    message += temp_str + question_terminology  + " was suggested by <a href='#' id='"+div_id+"' onmouseover=\""+onmouseover+"\" onmouseout=\""+onmouseout+"\" >"+user_display_name + "</a> on " + answer_create_datetime + ".<br>Please vote on its accuracy.<br/>"
              


                                            
            else:            
                if existed_pending_answers > 0 and message == '':    
                    message += 'The previous approved '+ question_terminology  + ' has been challenged.<br/>'  
          
                allow_suggest = False
                if answer.creator_id == login_user.id:  
                    answer_obj['can_vote'] = False
                    answer_obj['can_vote_up'] = 'false'
                    answer_obj['can_vote_down'] = 'false'                       
                    #if question.has_multivalues == 0:   # by default, the login user can no longer make a suggestion once he has made one.  but if this is a multivalue items he can continue to do so
                        #allow_suggest = False
                else:
                    answer_obj['can_vote'] = True
                    
                    if answer.id in vote_info:
                        if login_user.id in vote_info[answer.id]['user_last_vote_on_this_item']:                   
                            user_last_vote = vote_info[answer.id]['user_last_vote_on_this_item'][login_user.id]
                        else:
                            user_last_vote = None
                    else:
                        user_last_vote = None
                                            
                    if user_last_vote != None:                    
                        if user_last_vote.data == 'Vote: Up':
                            answer_obj['can_vote_up'] = 'false'
                            answer_obj['can_vote_down'] = 'true' 
                        else:
                            answer_obj['can_vote_up'] = 'true'
                            answer_obj['can_vote_down'] = 'false'       
                    else:
                        answer_obj['can_vote_up'] = 'true'
                        answer_obj['can_vote_down'] = 'true'     
                        
                answer_obj['show_edit'] = False                       
                answer_obj['can_edit'] = False                                            
                answer_obj['can_approve'] = False    
                
                if answer.creator_id == login_user.id:  
                    if login_user.is_superuser == 1: 
                        answer_obj['show_cancel'] = True                       
                        answer_obj['can_cancel'] = True                      
                else:
                    answer_obj['show_cancel'] = False                       
                    answer_obj['can_cancel'] = False  
                
            if login_user.is_superuser == 1:
                answer_obj['can_cancel'] = True    
                answer_obj['show_cancel'] = True  
                                            
            answer_objs.append(answer_obj)
            
        # new requirement: admin can cancel any suggestion, his or others, validated or not, has vote or no vote
                        
            
        if len(answer_objs) > 1 and existed_approved_answers > 0:
            if question.has_multivalues != 1:
                if len(answer_objs) == existed_approved_answers:
                    approved_answer_list.append(answer_objs[-1])
                else:
                    approved_answer_list = answer_objs[existed_approved_answers-1:]
            else:
                approved_answer_list = list(answer_objs)
        else:
            approved_answer_list = list(answer_objs)
                
        content['answers'] = approved_answer_list              
        content['prompt'] = ''                                                  
        content['message'] = message                # top message for each question   
        content['do_not_show_add_button'] = False 
        content['has_no_answer'] = False        
        
        
        content['pending_editable_answer_ids'] = pending_editable_answer_ids              
        content['add_btn_value'] = self.get_add_btn_value(question, existed_approved_answers, existed_pending_answers) 
      
        if allow_suggest == True and login_user.is_authenticated(): 
            content['allow_suggest'] = True    # show the suggest a new value  
        else:
            content['allow_suggest'] = allow_suggest    # hide the suggest a new value            
            
        if existed_pending_answers == 0 and existed_approved_answers == 0:
            content['show_edit_mode'] = True
        else:
            content['show_edit_mode'] = show_edit_mode

        content['show_add_button'] = content['allow_suggest']   # obvious that if can suggest, can see add button
         
        content['can_still_add'] = False            
        if existed_approved_answers > 0:
            content['can_still_add'] = can_still_add            # has approved answer and the login user already made the pending suggestion, can no longer add.
            content['allow_suggest'] = True
            content['show_edit_mode'] = True
            if question.has_multivalues == 0: 
                content['show_add_button'] = False                  # however, add via clicking on the field label like the first time, so hide the add button
            else:
                content['show_add_button'] = True
                
        return content
        
    def get_validation_history(self, entity_name, entity_id):       # for approved items only
        data = {}
        if entity_name == 'requirement':
            data['answer'] = answer = AnswerReference.objects.get(id=entity_id)
            if data['answer'].creator.is_superuser != 1:
                action_category = 'VoteRequirement'
                
                #get the org in the AnswerReference if exist, this is the org at the time of suggestion
                if answer.organization != None:
                    data['organization'] = answer.organization
                else:
                    orgmembers = OrganizationMember.objects.filter(user = data['answer'].creator, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R')
                    if orgmembers != None and len(orgmembers) >  0:
                        data['organization'] = orgmembers[0].organization
                    else:
                        data['organization'] = None
               
                datetime_util_obj = DatetimeHelper(data['answer'].create_datetime)
                data['create_datetime'] = datetime_util_obj.showStateTimeFormat(data['answer'].jurisdiction.state)                
                
                datetime_util_obj = DatetimeHelper(data['answer'].status_datetime)
                data['approval_datetime'] = datetime_util_obj.showStateTimeFormat(data['answer'].jurisdiction.state)               
                
                data['vote'] = self.get_voting_tally(action_category, entity_id, data['answer'].jurisdiction, data['answer'].question.category) 
            else:
                data['vote'] = {}
                data['organization'] = None
                datetime_util_obj = DatetimeHelper(data['answer'].status_datetime)
                data['approval_datetime'] = datetime_util_obj.showStateTimeFormat(data['answer'].jurisdiction.state)   
                                
        return data             
    
             
    def get_formatted_value(self, value, question):

        answer = json.loads(value)     
        
        if question.question == 'Primary phone number' or question.question == 'Zoning department primary phone number':
            value = answer['phone']
            if value != None:
                if 'ext' in answer and answer['ext'] != '' and answer['ext'] != None:
                    value += " ext. "+str(answer['ext'])           
                    
        elif question.question == 'Zoning department email': 
            value = answer['value']
            value = "<div><a href='mailto:"+value+"'>"+value+"</a></div>"
                    
        elif question.question == 'Department Hours':      
            jurisdiction_obj = Jurisdiction()          
            value = jurisdiction_obj.get_formatted_jurisdiction_dept_hours(answer)  
            value = "<div>"+value+"</div>"   
            if 'note' in answer and answer['note'] != '' and answer['note'] != None:  
                value += "<div>"+answer['note']+"</div> "    
                
        elif question.question == 'Online forms':
            value = ''
            if 'link_1' in answer and 'name_1' in answer:
                value += "<a href='" +answer['link_1']+"' target='_blank' >"+answer['name_1']+"</a><br/>"    
            
        elif question.question == 'Utilities serving the AHJ':
            value = ''
            if 'link_1' in answer and 'name_1' in answer:            
                value += "<a href='" +answer['link_1']+"' target='_blank' >"+answer['name_1']+"</a><br/>"                             
                
        elif question.question == 'Permit Cost':
            jurisdiction_obj = Jurisdiction()             
            value = jurisdiction_obj.get_formatted_jurisdiction_permit_cost(answer)                                

        elif question.question == 'Accepts electronic submissions':
            jurisdiction_obj = Jurisdiction()             
            value = jurisdiction_obj.get_formatted_jurisdiction_accepts_electronic_submissions(answer)   

        elif question.question == 'Plan-check service type':
            value = answer['plan_check_service_type']
            if value != None:        
                value = "<div>"+value+"</div>"
            else:
                value = ''
            
            if 'note' in answer:
                value += "<div>"+answer['note']+"</div> "    
 
        elif question.question == 'How long does it take this jurisdiction to do "turn around" on a roof mounted pv system?':
            value = answer['time_qty'] + " " + answer['time_unit'] 
            value = "<div>"+value+"</div>"
            if 'note' in answer and answer['note'] != '' and answer['note'] != None:  
                value += "<div>"+answer['note']+"</div> "     
                
        elif question.question == 'How long does it take this jurisdiction to do "turn around" on a ground mounted pv system?':
            value = answer['time_qty'] + " " + answer['time_unit'] 
            value = "<div>"+value+"</div>"
            if 'note' in answer and answer['note'] != '' and answer['note'] != None:  
                value += "<div>"+answer['note']+"</div> "    
                
        elif question.question == 'Department website':
            value = ''
            if 'value' in answer and answer['value'] != '' and answer['value'] != None:
                urlUtil = UrlUtil(answer['value'])
                value = "<a href='"+urlUtil.get_href()+"' target='_blank' >"+urlUtil.get_display_website()+"</a>"            
                
        elif question.question == 'Department address' or question.question == 'Zoning department address':     
            jurisdiction_obj = Jurisdiction()             
            value = jurisdiction_obj.get_formatted_jurisdiction_address(answer)  
                  
        elif question.template == 'radio_with_exception.html':
            if 'radio' in answer:
                value = "<div>"+answer['radio']
                if answer['radio'] == 'Yes, with exceptions':
                    if 'exceptions' in answer:
                        value += ' \"'+ answer['exceptions'] + '\"'
                value += "</div>"
                
        else:
            if question.form_type == 'CF' or question.form_type != 'MF':
                if 'value' in answer:
                    value = "<div>"+answer['value']
                    if question.field_suffix != '' and question.field_suffix != None:
                        value = value + " " + question.field_suffix
                        
                    value = value + "</div>"   
                              
        return value
            
    def process_vote(self, user, vote, entity_name, entity_id, user_confirm_vote='not_yet'):  
        if entity_name == 'requirement':
            category_name = 'VoteRequirement'
            
        action_categorys = ActionCategory.objects.filter(name__iexact=category_name)            
        action_category = action_categorys[0]
        effect_approve_reject = self.pre_validation_check(action_category, vote, entity_id)
        
        if (effect_approve_reject == 'will_approve' or effect_approve_reject == 'will_reject') and user_confirm_vote == 'not_yet':       # approve reject none
            return effect_approve_reject
        else:
            if entity_name == 'requirement':
                answer = AnswerReference.objects.get(id=entity_id)
            
            feedback = self.register_vote(action_category, user.id, vote, entity_name, entity_id, answer.jurisdiction_id)
            
            if entity_name == 'requirement':
                if effect_approve_reject == 'will_approve':
                    answer.approval_status = 'A'
                elif effect_approve_reject == 'will_reject':
                    answer.approval_status = 'R'
                    
            if effect_approve_reject == 'will_approve' :   #or effect_approve_reject == 'will_reject'
                feedback = 'registered_with_changed_status'
                answer.status_datetime = datetime.datetime.now()
                answer.save()
                # reject all others suggestions only if the question is not of multivalues type
                
                self.on_approving_a_suggestion(jurisdiction, answer)
            
        return feedback
    
    def on_approving_a_suggestion(self, answer):
        if answer.question.has_multivalues == 0:        
            answers = AnswerReference.objects.filter(jurisdiction=answer.jurisdiction, question=answer.question).exclude(id=answer.id)
            if len(answers) > 0:
                for this_answer in answers:
                    this_answer.approval_status = 'R'
                    this_answer.status_datetime = datetime.datetime.now()
                    this_answer.save()   
                    
        return True     
    
    def register_vote(self, action_category, user_id, vote, entity_name, entity_id, jurisdiction_id):     

        user_obj = User.objects.get(pk=user_id)
  
        action_objs = Action.objects.filter(category__exact=action_category, entity_id = entity_id, user__exact=user_obj)
        action_data = "Vote: " + vote.title()
            
        if len(action_objs) > 0:
            action_obj = action_objs[0]
            action_obj.action_datetime = datetime.datetime.now()
            action_obj.data = str(action_data)
            action_obj.save()
        else:
            #contributionHelper = ContributionHelper()           
            #action_obj = contributionHelper.save_action(action_category_name, vote, entity_id, entity_name, user_id, jurisdiction_id)
            if entity_name == 'requirement' :
                entity = AnswerReference.objects.get(id=entity_id)
                question = Question.objects.get(id=entity.question_id)
                entity_category_id = question.category_id   
                           
                action_obj = Action.objects.create(category_id=action_category.id, entity_id=entity_id, data=action_data, entity_name=entity_name, user_id=user_id, scale=action_category.points, jurisdiction_id=jurisdiction_id, question_category_id=entity_category_id)
            
            

        #self.rate(action_category_name, entity_name, eid, action_obj, user_id, jurisdiction_id)
        return 'registered'
        #return action_obj
        
    def pre_validation_check(self, action_category, vote, entity_id):

        answer = AnswerReference.objects.get(id=entity_id)
        #answer_status_datetime = answer.create_datetime
        status ='no_change'
        
        try:
            if answer.approval_status == 'P':
                answer_pending_datetime = answer.status_datetime

                # if net of 3 up vote at any time ==> approved
                total_up_votes_while_pending = Action.objects.filter(category=action_category, entity_id=entity_id, data__iexact='vote: up', action_datetime__gt=answer_pending_datetime).order_by('action_datetime')    

                total_down_votes_while_pending = Action.objects.filter(category=action_category, entity_id=entity_id, data__iexact='vote: down', action_datetime__gt=answer_pending_datetime).order_by('action_datetime')                
 
                if vote == 'up' and len(total_up_votes_while_pending) >= len(total_down_votes_while_pending) + 2 :
                    status = 'will_approve'        
                
                if vote == 'down' and len(total_down_votes_while_pending) >= 2:     # 3 down votes to reject
                    status = 'will_reject'
                                
            # if already approved
            elif answer.approval_status == 'A':
                answer_approval_datetime = answer.status_datetime
                #total_votes_after_approval = Action.objects.filter(category=action_category, entity_id=entity_id, action_datetime__gt=answer_approval_datetime)
                five_consecutive_down_votes_after_approval = Action.objects.filter(category=action_category, entity_id=entity_id, data__iexact='vote: down', action_datetime__gt=answer_approval_datetime).order_by('action_datetime')[:4]            
                # if last 5 votes are down votes ==> rejected again
                if vote == 'down' and len(five_consecutive_down_votes_after_approval) == 4:
                    status = 'will_reject'
                else:
                    # if net of 5 down votes ==> rejected again.
                    #total_up_votes_after_approval = Action.objects.filter(category=action_category, entity_id=entity_id, data__iexact='vote: up', action_datetime__gt=answer_approval_datetime).order_by('action_datetime')    
                    total_down_votes_after_approval = Action.objects.filter(category=action_category, entity_id=entity_id, data__iexact='vote: down', action_datetime__gt=answer_approval_datetime).order_by('action_datetime')                
                    #if vote == 'down' and len(total_down_votes_after_approval) >= len(total_up_votes_after_approval) + 4 :
                    if vote == 'down' and len(total_down_votes_after_approval) >= 4:
                        status = 'will_reject'
        except:
            pass
        print status
        return status
    
    def get_jurisdiction_voting_info_by_category(self, category_name, jurisdiction, entity_category, question = None):
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        if question == None:
            votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction, question_category=entity_category).order_by('-action_datetime')    
        else:
            answer_ids = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question).exclude(approval_status__exact='R').exclude(approval_status__exact='F').exclude(approval_status__exact='C').values_list('id')
            votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction, question_category=entity_category, entity_id__in=answer_ids).order_by('-action_datetime')    
            
        vote_info = {}
        for vote in votes:
            if vote.entity_id not in vote_info:
                vote_info[vote.entity_id] = {}
                vote_info[vote.entity_id]['total_up_votes'] = 0
                vote_info[vote.entity_id]['total_down_votes'] = 0
                vote_info[vote.entity_id]['user_last_vote_on_this_item'] = {}
                vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                vote_info[vote.entity_id]['up_vote_found'] = False
                
            if vote.data == 'Vote: Up':
                vote_info[vote.entity_id]['total_up_votes'] = vote_info[vote.entity_id]['total_up_votes'] + 1                
            elif vote.data == 'Vote: Down':
                vote_info[vote.entity_id]['total_down_votes'] = vote_info[vote.entity_id]['total_down_votes'] + 1   
                
                if 'last_down_vote_date' not in vote_info[vote.entity_id]:
                    #vote_info[vote.entity_id]['last_down_vote'] = vote
                    datetime_util_obj = DatetimeHelper(vote.action_datetime)
                    last_down_vote_date = datetime_util_obj.showStateTimeFormat(jurisdiction.state)                    
                    vote_info[vote.entity_id]['last_down_vote_date'] = last_down_vote_date
                                        
                if vote_info[vote.entity_id]['up_vote_found'] == False:
                    vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = vote_info[vote.entity_id]['num_consecutive_last_down_votes'] + 1
                
            if vote.user_id not in vote_info[vote.entity_id]['user_last_vote_on_this_item']:
                vote_info[vote.entity_id]['user_last_vote_on_this_item'][vote.user_id] = vote
                

        return vote_info
    
    def get_jurisdiction_voting_info(self, category_name, jurisdiction, questions = None):
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        print action_category
        if questions == None:
            votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction).order_by('question_category', 'entity_id', '-action_datetime')    
        else:
            answer_ids = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__in=questions).exclude(approval_status__exact='R').exclude(approval_status__exact='F').exclude(approval_status__exact='C').values_list('id')
            print answer_ids
            votes = Action.objects.filter(category__in=action_category, jurisdiction=jurisdiction).order_by('question_category', 'entity_id', '-action_datetime')    
        print votes
        vote_info = {}
        for vote in votes:
            if vote.entity_id not in vote_info:
                vote_info[vote.entity_id] = {}
                vote_info[vote.entity_id]['total_up_votes'] = 0
                vote_info[vote.entity_id]['total_down_votes'] = 0
                vote_info[vote.entity_id]['user_last_vote_on_this_item'] = {}
                vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = 0
                vote_info[vote.entity_id]['up_vote_found'] = False
                
            if vote.data == 'Vote: Up':
                vote_info[vote.entity_id]['total_up_votes'] = vote_info[vote.entity_id]['total_up_votes'] + 1                
            elif vote.data == 'Vote: Down':
                vote_info[vote.entity_id]['total_down_votes'] = vote_info[vote.entity_id]['total_down_votes'] + 1   
                
                if 'last_down_vote_date' not in vote_info[vote.entity_id]:
                    #vote_info[vote.entity_id]['last_down_vote'] = vote
                    datetime_util_obj = DatetimeHelper(vote.action_datetime)
                    last_down_vote_date = datetime_util_obj.showStateTimeFormat(jurisdiction.state)                    
                    vote_info[vote.entity_id]['last_down_vote_date'] = last_down_vote_date
                                        
                if vote_info[vote.entity_id]['up_vote_found'] == False:
                    vote_info[vote.entity_id]['num_consecutive_last_down_votes'] = vote_info[vote.entity_id]['num_consecutive_last_down_votes'] + 1
                
            #if vote.user_id not in vote_info[vote.entity_id]['user_last_vote_on_this_item']:
            #    vote_info[vote.entity_id]['user_last_vote_on_this_item'][vote.user_id] = vote
                
            # temp test data
            #vote_info[vote.entity_id]['can_vote_up'] = False
            #vote_info[vote.entity_id]['can_vote_down'] = False
                        
        return vote_info    
        
        
    def get_voting_tally(self, category_name, entity_id, jurisdiction, entity_category):

        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        up_count = Action.objects.filter(category__in=action_category, entity_id__exact=entity_id, jurisdiction=jurisdiction, question_category=entity_category, data__iexact="Vote: Up").count()
        down_count = Action.objects.filter(category__in=action_category, entity_id__exact=entity_id, jurisdiction=jurisdiction, question_category=entity_category, data__iexact="Vote: Down").count()
        if up_count == None:
            up_count = 0
        if down_count == None:
            down_count = 0
                        
        vote_info = {}
        vote_info['total_up_votes'] = up_count
        vote_info['total_down_votes'] = down_count

        return vote_info
    
    def get_user_last_vote_on_this_item(self, user, category_name, entity_id, jurisdiction, entity_category):
        action = None

        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        actions = Action.objects.filter(category__in=action_category, entity_id__exact=entity_id, user=user,jurisdiction=jurisdiction, question_category=entity_category).order_by('-action_datetime')
        if actions:
            action = actions[0]

        return action
 
    def get_entity_last_down_vote(self, category_name, entity_id, jurisdiction, entity_category):
        action = None
        down_vote_count = 0  
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        actions = Action.objects.filter(category__in=action_category, entity_id__exact=entity_id, jurisdiction=jurisdiction, question_category=entity_category).order_by('-action_datetime')[:1]
        if actions:  
            action = actions[0]
           
            #jurisdiction = Jurisdiction.objects.get(id=action.jurisdiction_id)
                        
            datetime_util_obj = DatetimeHelper(action.action_datetime)
            last_down_vote_date = datetime_util_obj.showStateTimeFormat(jurisdiction.state)
        else:
            last_down_vote_date = ''
            
        return last_down_vote_date    
    
    def get_entity_last_down_votes(self, category_name, entity_id, jurisdiction, entity_category):
        action = None
        down_vote_count = 0  
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        actions = Action.objects.filter(category__in=action_category, entity_id__exact=entity_id, jurisdiction=jurisdiction, question_category=entity_category).order_by('-action_datetime')
        if actions:  
            down_vote_count = 0          
            for action in actions:
                if action.data != 'Vote: Down':
                    break
                else:
                    down_vote_count = down_vote_count + 1
                    
        return down_vote_count
    
    def get_addresses_for_map(self, jurisdiction):

        questions = Question.objects.filter(id=4) #question id 4 is supposed to be the address

        question = questions[0]
            
        answers = AnswerReference.objects.filter(question=question, jurisdiction=jurisdiction, approval_status__exact='A').order_by('-status_datetime')
        if answers != None and len(answers) > 0:
            answer = answers[0] # only one approved
         
            answer_value = json.loads(answer.value)    
            str_addr = jurisdiction.get_formatted_jurisdiction_address(answer_value)  
        else:
            if jurisdiction.jurisdiction_type == 'CI':
                if jurisdiction.county == None:
                    str_addr = jurisdiction.city + ', ' + jurisdiction.state
                else:
                    str_addr = jurisdiction.city + ', ' + jurisdiction.county
            elif jurisdiction.jurisdiction_type == 'CO':
                str_addr = jurisdiction.county + ' county, ' + jurisdiction.state
            else:
                str_addr = ''  
                

        return str_addr              
        
    def get_add_btn_value(self, question, existed_approved_answers, existed_pending_answers):
        a_or_an = 'a'  
        
        question_terminology = self.get_terminology(question)  
                     
        if question_terminology[0] in 'aeiou':
            a_or_an = 'an'
                    
        if question.has_multivalues == 1:
            if existed_approved_answers > 0 or existed_pending_answers > 0:
                value = '+ Add another ' + question_terminology
            else:           
                value = '+ Add '+a_or_an+' '+ question_terminology
        else:
            if existed_approved_answers > 0 or existed_pending_answers > 0:
                value = '+ Suggest a new ' + question_terminology 
            else:           
                value = '+ Suggest '+a_or_an+' '+ question_terminology
                
        #if question.question == 'Utilities serving the AHJ':
        #    value = value + " company"

        return value
    
    def get_AHJ_display_by_category(self, request, jurisdiction, questions, question_category_obj, data):
        question_data = {}
        
        category_name = 'VoteRequirement'
        data['vote_info'] = self.get_jurisdiction_voting_info_by_category(category_name, jurisdiction, question_category_obj)
        #data['answers'] = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__category__exact=question_category_obj).exclude(approval_status__exact='R').exclude(approval_status__exact='F').exclude(approval_status__exact='C')
        

        for question in questions:
            question_data[question.id] = {}
            question_data[question.id]['suggestions'] = self.get_question_answers_display_data(request, jurisdiction, question, data)               


        return question_data
    
    def get_form_field_data(self, jurisdiction, question):
        data = {}

        data['question_template'] = self.get_question_template(question)
        data['form_id'] = 'form_' + str(question.id) 
        data['id'] = 'id_' + str(question.id)
        data['question_id'] = question.id 
        data['question'] = question         
        data['question_label'] = self.get_field_label(question, jurisdiction)                             
        data['name'] = 'value'
        
        if question.field_suffix == None:     
            data['field_suffix'] = ''
        else:   
            data['field_suffix'] = question.field_suffix
        
        if question.form_type != 'MF':
            data['validation_class'] = question.validation_class
            data['field_attributes'] = question.field_attributes
            
        if question.instruction == None:
            data['instruction'] = ''
        else:
            data['instruction'] = question.instruction  
              
        data['js'] = []
        if question.js != '' and question.js != None:
            data['js'].append(question.js)
        else:
            data['js'].append('AHJ_validation_default.js')
                
        return data  
    
    def get_question_template(self, question):
        if question.form_type == 'CF':
            question_template = 'textarea.html'
        elif question.form_type == 'T':
            question_template = 'text_field.html'
        elif question.form_type == 'TA':
            question_template = 'textarea.html'       
        elif question.form_type == 'R':
            question_template = 'radio_field.html'     
        elif question.form_type == 'DD':
            question_template = 'dropdown_field.html'                               
        else:
            question_template = question.template
            
        return question_template        
    
    def save_answer(self, question_obj, answer, juris, action_category_name, user, is_callout, answer_id=None):
        if question_obj.id == 16:
            answer = self.process_answer(question_obj, answer)    
            
        encoded_txt = answer.encode('utf-8') 
                            
        if answer_id != None:
            
            answerreference = AnswerReference.objects.get(id=answer_id)
            answerreference.value = encoded_txt
            #answerreference.modify_datetime = datetime.datetime.now()
            answerreference.save()
                    
        else:
            answerreferences = AnswerReference.objects.filter(question__exact=question_obj, jurisdiction__exact=juris, approval_status__in=('A', 'P'))  
            '''
            if answerreferences:
                for answer_ref_obj in answerreferences:
                    answer_ref_obj.is_current = 0
                    answer_ref_obj.modify_datetime = datetime.datetime.now()
                    answer_ref_obj.save()
            '''
         
            save_n_approved = False
            if user.is_superuser == 1:
                if question_obj.has_multivalues == 1:
                    save_n_approved = True
                elif question_obj.has_multivalues == 0 and len(answerreferences) == 0:   # if entered by superadmin and not a multi-value item and if there is no existing suggestion -> automatic approval
                    save_n_approved = True
                if question_obj.has_multivalues == 0 and len(answerreferences) > 0:
                    save_n_approved = True                                             # It was False before.  Logic: if entered by superadmin and not a multi-value item and if there is no existing suggestion -> NO automatic approval
            else:                                                                       # now changed to True per Tommy
                save_n_approved = False
                
            if save_n_approved == True:
                approval_status = 'A'
            else:
                approval_status = 'P'
                
            if approval_status == 'A' and question_obj.has_multivalues == 0:
                answerreferences = AnswerReference.objects.filter(question__exact=question_obj, jurisdiction__exact=juris, approval_status__in='P')  
                if answerreferences:
                    for answer_ref_obj in answerreferences:
                        answer_ref_obj.approval_status = "R"  
                        answer_ref_obj.save()    
                    
                
            answerreference = AnswerReference(question_id = question_obj.id, value = encoded_txt, jurisdiction_id = juris.id, is_callout = is_callout, rating_status='U', approval_status=approval_status, is_current=1, creator_id=user.id,  status_datetime = datetime.datetime.now())            
            
            answerreference.save()
            
            self.process_questions_with_link_or_file(answerreference)


        org_members = OrganizationMember.objects.filter(user=user, status = 'A', organization__status = 'A')
        if len(org_members) > 0:
            org = org_members[0].organization
            juris.last_contributed_by_org = org
            answerreference.organization = org
            answerreference.save()            
                
        juris.last_contributed = datetime.datetime.now()
        juris.last_contributed_by = user

        juris.save()
        
        entity_name='Requirement'
        data = str(answer)
        action_obj = Action()
        action_obj.save_action(action_category_name, data, answerreference, entity_name, user.id, juris) 
        
        if question_obj.id == 96 or question_obj.id == 105 or question_obj.id == 36 or question_obj.id == 282 or question_obj.id == 62:
            print 'process_link_or_file'
            self.process_link_or_file(answerreference) 

        return answerreference 
    
    def process_answer(self, question, answer):
        # "default_value": "{\"percentage_of_total_system_cost_cap\": \"\", \"fee_per_inverter\": \"\", \"flat_rate_amt\": \"\", \"fee_per_major_components\": \"\", 
        # \"jurisdiction_cost_recovery_notes\": \"\", \"percentage_of_total_system_cost\": \"\", \"percentage_of_total_system_cost_cap_amt\": \"\", \"fee_per_component_cap\": \"\", 
        # \"fee_per_component_cap_cap_amt\": \"\", \"fee_per_module\": \"\"}",

        # "default_value": "{\"fee_type_1\": \"\", \"fee_item_1_1\": \"\", \"fee_formula_1_1\": \"flat_rate\", \"fee_other_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_1_1\": \"\", 
        # \"fee_per_inverter_1_1\": \"\", \"fee_flat_rate_1_1\": \"\", \"fee_per_major_components_1_1\": \"\", \"fee_jurisdiction_cost_recovery_notes_1_1\": \"\", 
        # \"fee_percentage_of_total_system_cost_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_amt_1_1\": \"\", \"fee_per_component_cap_1_1\": \"\", 
        # \"fee_per_component_cap_cap_amt_1_1\": \"\", \"fee_per_module_1_1\": \"\"}",
        
        #{"fee_formula_1_1": "percentage_of_total_system_cost", "fee_percentage_of_total_system_cost_1_1": "5", "fee_percentage_of_total_system_cost_cap_amt_1_1": "1000", 
        #"fee_type_1": "xxx", "fee_item_1_1": "yyy"}      
        
        mathUtil = MathUtil()
        answer = json.loads(answer)
        if question.id == 16:
            flat_rate_amt = 0
            percentage_of_total_system_cost = 0
            fee_per_inverter = 0
            fee_per_module = 0
            fee_per_major_components = 0
            percentage_of_total_system_cost_cap_amt = 0
            fee_per_component_cap_cap_amt = 0
                    
            explicit_zero = False
            
            for answer_key in answer.keys():
         
                value = answer.get(answer_key)
                if value != '' and mathUtil.is_number(value) == True:  
                    value = float(value.replace(',', ''))
                    if value == 0:
                        explicit_zero = True                    
                    if answer_key.find('fee_flat_rate_') == 0:  
                        flat_rate_amt = flat_rate_amt + value  
                    else:
                        if answer_key.find('fee_percentage_of_total_system_cost_') == 0 and answer_key.find('fee_percentage_of_total_system_cost_cap') == -1:      
                            percentage_of_total_system_cost = percentage_of_total_system_cost + value  
                            
                            array_fee_percentage_of_total_system_cost = answer_key.split('fee_percentage_of_total_system_cost_')
                            fee_key = str(array_fee_percentage_of_total_system_cost[1])
                            cap_key = 'fee_percentage_of_total_system_cost_cap_' + fee_key
                            if cap_key in answer:
                                cap = answer.get(cap_key)
                                if cap == 'yes':
                                    cap_amt_key = 'fee_percentage_of_total_system_cost_cap_amt_' + fee_key
                                    if cap_amt_key in answer:
                                        cap_amt = answer.get(cap_amt_key)
                                        if cap_amt != '' and mathUtil.is_number(cap_amt) == True:  
                                            cap_amt = float(cap_amt.replace(',', ''))
                                            if cap_amt > 0:
                                                if percentage_of_total_system_cost_cap_amt == 0:
                                                    percentage_of_total_system_cost_cap_amt = cap_amt
                                                elif percentage_of_total_system_cost_cap_amt > 0:
                                                    if cap_amt < percentage_of_total_system_cost_cap_amt:
                                                        percentage_of_total_system_cost_cap_amt = cap_amt 
                                    
                        
                        else:
                            if answer_key.find('fee_percentage_of_total_system_cost_cap_') == -1:
                                fee_key = ''
                                cap_amt = 0
                                array_fee_per_inverter = answer_key.split('fee_per_inverter_')
                                if len(array_fee_per_inverter) >= 2:      
                                    fee_per_inverter = fee_per_inverter + value
                                    fee_key = array_fee_per_inverter[1]
                                else:
                                    array_fee_per_module = answer_key.split('fee_per_module_')
                                    if len(array_fee_per_module) >= 2:      
                                        fee_per_module = fee_per_module + value  
                                        fee_key = array_fee_per_module[1]                                         
                                    else:
                                        array_fee_per_major_components = answer_key.split('fee_per_major_components_')
                                        if len(array_fee_per_major_components) >= 2:      
                                            fee_per_major_components = fee_per_major_components + value
                                            fee_key = array_fee_per_major_components[1]
                           
                                if fee_key != '':
                                    cap_key = 'fee_per_component_cap_' + str(fee_key)
                             
                                    if cap_key in answer:
                                        cap = answer.get(cap_key)
                               
                                        if cap == 'yes':
                                            cap_amt_key = 'fee_per_component_cap_cap_amt_' + str(fee_key)
                 
                                            if cap_amt_key in answer:
                                                cap_amt = answer.get(cap_amt_key)
                                           
                                                if cap_amt != '' and mathUtil.is_number(cap_amt) == True:  
                                                    cap_amt = float(cap_amt.replace(',', ''))
                                                    if cap_amt > 0:
                                                        if fee_per_component_cap_cap_amt == 0:
                                                            
                                                            fee_per_component_cap_cap_amt = cap_amt
                                                        elif fee_per_component_cap_cap_amt > 0:
                                                        
                                                            if cap_amt < fee_per_component_cap_cap_amt:

                                                                fee_per_component_cap_cap_amt = cap_amt                      
                                            
                                     
                                     
            if flat_rate_amt == 0:
                if explicit_zero == True:
                    answer['flat_rate_amt'] = '0'
                else:
                    answer['flat_rate_amt'] = ''
            else:             
                answer['flat_rate_amt'] = str(flat_rate_amt)
                
            if percentage_of_total_system_cost == 0:
                if explicit_zero == True:
                    answer['percentage_of_total_system_cost'] = '0'
                else:
                    answer['percentage_of_total_system_cost'] = ''
            else:                          
                answer['percentage_of_total_system_cost'] = str(percentage_of_total_system_cost)

            if fee_per_inverter == 0:
                if explicit_zero == True:
                    answer['fee_per_inverter'] = '0'
                else:
                    answer['fee_per_inverter'] = ''
            else:                          
                answer['fee_per_inverter'] = str(fee_per_inverter)
                
            if fee_per_module == 0:
                if explicit_zero == True:
                    answer['fee_per_module'] = '0'
                else:
                    answer['fee_per_module'] = ''
            else:                                         
                answer['fee_per_module'] = str(fee_per_module)
                
            if fee_per_major_components == 0:
                if explicit_zero == True:
                    answer['fee_per_major_components'] = '0'
                else:
                    answer['fee_per_major_components'] = ''
            else:                              
                answer['fee_per_major_components'] = str(fee_per_major_components)
            
            if percentage_of_total_system_cost_cap_amt == 0:
                if explicit_zero == True:
                    answer['percentage_of_total_system_cost_cap_amt'] = '0'
                else:
                    answer['percentage_of_total_system_cost_cap_amt'] = ''             
            else:            
                answer['percentage_of_total_system_cost_cap_amt'] = str(percentage_of_total_system_cost_cap_amt)
                
            if fee_per_component_cap_cap_amt == 0:
                if explicit_zero == True:
                    answer['fee_per_component_cap_cap_amt'] = '0'
                else:
                    answer['fee_per_component_cap_cap_amt'] = '' 
            else:
                answer['fee_per_component_cap_cap_amt'] = str(fee_per_component_cap_cap_amt)  
                    
                          
        return json.dumps(answer)
    
    def get_top_contributors(self, jurisdiction, entity_categories): 
        top_contributors = []
        answers = AnswerReference.objects.filter(jurisdiction=jurisdiction, question__category__in=entity_categories, approval_status ='A') 
  
        if len(answers)>0:
            contributors = {}
           
            for answer in answers:
                '''
                org_members = OrganizationMember.objects.filter(user=answer.creator, organization__status='A')
   
                if len(org_members) > 0:
                    org_member = org_members[0]  # supposed to be one anyway
                    if org_member.organization.id in contributors:
                        contributors[org_member.organization] =  contributors[org_member.organization] + 1
                    else:
                        contributors[org_member.organization] = 1
                '''
           
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
                 
    def cron_validate_answers(self):
        # get all 'pending' answers that is just 2 weeks old
        # today date - create date >= 2 weeks
        # assign approval_status = 'A' - answerreference, action
        today_date = date.today()
        print today_date
        user_id = 1 # supposedly the django admin user.
        
        number_days_unchallenged_b4_approved = django_settings.NUM_DAYS_UNCHALLENGED_B4_APPROVED        
        two_weeks_before_today = today_date - timedelta(days=number_days_unchallenged_b4_approved)
        print two_weeks_before_today
        vote_action_category = ActionCategory.objects.filter(name__iexact='VoteRequirement')
        entity_name='Requirement'
        action_obj = Action()
        
        validate_action_category_name = 'ValidateRequirement'
                        
        already_processed_jurisdiction_question = []
        answers = AnswerReference.objects.filter(approval_status__iexact='P', create_datetime__lte=two_weeks_before_today).order_by('jurisdiction__id', 'question__id', 'create_datetime')  
        #print answers
        for answer in answers:
            #print 'answer :: ' + str(answer.id)
            #print answer
            jurisdiction_question_str = str(answer.jurisdiction.id) + '_'  + str(answer.question.id)
            #print 'jurisdiction_question_str :: ' + str(jurisdiction_question_str)
            if jurisdiction_question_str not in already_processed_jurisdiction_question:
                votes = Action.objects.filter(data__iexact='vote: down', entity_name__iexact=entity_name, entity_id=answer.id, action_datetime__gt=answer.create_datetime)
                #print 'number of down votes :: ' + str(len(votes))
                if len(votes) == 0:
                    answer.approval_status = 'A'
                    answer.status_datetime = datetime.datetime.now()
                    answer.save()
                    #print 'answer saved :: ' + str(answer.id)
                    already_processed_jurisdiction_question.append(jurisdiction_question_str)       
                    #print already_processed_jurisdiction_question
                    #action
                    data = 'approved - unchallenged for 1 week(s) after creation'
                    aobj = action_obj.save_action(validate_action_category_name, data, answer, entity_name, user_id, answer.jurisdiction)  
                    
                    # cancel all subsequent answers to the same question
                    question = answer.question
                    if question.has_multivalues == 0:
                        answers_to_be_rejected = AnswerReference.objects.filter(question = answer.question, jurisdiction = answer.jurisdiction, approval_status = 'P' )    # reject all other pending answers
                        for answer_to_be_rejected in answers_to_be_rejected:
                            answer_to_be_rejected.approval_status = 'R'
                            answer_to_be_rejected.status_datetime = datetime.datetime.now()
                            answer_to_be_rejected.save()
                        
                            #action
                            data = 'rejected - another answer was approved by the cron job'
                            action_obj.save_action(validate_action_category_name, data, answer_to_be_rejected, entity_name, user_id, answer.jurisdiction)                      
                
    def process_fee_structure(self, answer):
        
        #"default_value": "{\"fee_type_1\": \"\", \"fee_item_1_1\": \"\", \"fee_formula_1_1\": \"\", \"fee_other_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_1_1\": \"\", \"fee_per_inverter_1_1\": \"\", \"fee_flat_rate_1_1\": \"\", \"fee_per_major_components_1_1\": \"\", \"fee_jurisdiction_cost_recovery_notes_1_1\": \"\", \"fee_percentage_of_total_system_cost_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_amt_1_1\": \"\", \"fee_per_component_cap_1_1\": \"\", \"fee_per_component_cap_cap_amt_1_1\": \"\", \"fee_per_module_1_1\": \"\"}",

        # get fee type:
        fee_type_ids = []
        fee_ids = {}
        highest_fee_type_id = 0
        highest_fee_item_ids = {}

        for answer_key in answer.keys():

            array_fee_type = answer_key.split('fee_type_')
        
            if len(array_fee_type) >= 2:
                fee_type_id = array_fee_type[1]
             
                if fee_type_id not in fee_type_ids:
                    fee_type_ids.append(fee_type_id)
      
                    fee_ids[fee_type_id] = []
                    if fee_type_id > highest_fee_type_id:
                        highest_fee_type_id = fee_type_id
                        
            array_fee_item = answer_key.split('fee_item_')
            if len(array_fee_item) >= 2:
                fee_item = array_fee_item[1]
                array_fee_item_id = fee_item.split('_')
                if len(array_fee_item_id) >= 2:
                    fee_type_id = array_fee_item_id[0]
                    if fee_type_id not in fee_type_ids:
                        fee_type_ids.append(fee_type_id)
                        if fee_type_id > highest_fee_type_id:
                            highest_fee_type_id = fee_type_id
                        
                    fee_item_id = array_fee_item_id[1]
                    if fee_type_id not in fee_ids:
                        fee_ids[fee_type_id] = []
                        fee_ids[fee_type_id].append(fee_item_id) 
                        highest_fee_item_ids[fee_type_id] = fee_item_id
                    else:
                        if fee_item_id not in fee_ids[fee_type_id]:
                            fee_ids[fee_type_id].append(fee_item_id)  
                            if fee_type_id in  highest_fee_item_ids:
                                if fee_item_id > highest_fee_item_ids[fee_type_id]:
                                    highest_fee_item_ids[fee_type_id] = fee_item_id    
                            else:
                                 highest_fee_item_ids[fee_type_id] = fee_item_id                      
                
        data = {}
        data['fee_types'] = sorted(fee_type_ids)     
        for key in fee_ids.keys():
            fee_ids[key] = sorted(fee_ids.get(key)) 
        data['fee_items'] = fee_ids             # need to order them
        data['highest_fee_type_id'] = highest_fee_type_id   
        data['highest_fee_item_ids'] = highest_fee_item_ids 
                
  
        return data
        # get fee type's item
        
        # get fee item's details
        
    def process_questions_with_link_or_file(self, answer):
        print 'process_questions_with_link_or_file'
        process = False
        if answer.question.id == 96 or answer.question.id == 105:
            if answer.approval_status == 'A':
                answer_details = json.loads(answer.value)
                if 'available' in answer_details:    
                    if answer_details['available'] == 'no':
                        process = True
        '''
        if answer.question.id == 36: 
            if 'value' in answer_details:
                if answer_details['value'] == 'n in series in a rectangle allowed':
                    process = True
        '''        
        if process == True:
            question = Question.objects.get(id=answer.question.id)
            jurisdiction = Jurisdiction.objects.get(id=answer.jurisdiction.id)
            answers = AnswerReference.objects.filter(question__exact=question, jurisdiction__exact=jurisdiction).exclude(id__exact=answer.id)
            if len(answers) > 0:
                for answer in answers:
                    answer.approval_status = 'R'
                    answer.status_datetime = datetime.datetime.now()
                    answer.save()
                        # need to save to table action
                    
    
                    
        
    def process_link_or_file(self, answer):
        answer_details = json.loads(answer.value)
        print answer.question.question
        if 'form_option' in answer_details:
            print answer_details['form_option'] 
            if answer_details['form_option'] == 'link':
                answerattachments = AnswerAttachment.objects.filter(answer_reference__exact= answer)
                print len(answerattachments)
                if len(answerattachments) > 0:
                    for answerattachment in answerattachments:
                        answerattachment.delete()  
                        print "===> delete"
            elif answer_details['form_option'] == 'upload':      
                answer_details['link_1'] = ''
                answer.value = json.dumps(answer_details)
                answer.save()                     
            