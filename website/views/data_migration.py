import os
import json
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_unicode 
from django.conf import settings
from django.db import connections, transaction
from dajax.core import Dajax
from django.contrib.auth.models import User
from website.utils.httpUtil import HttpRequestProcessor
from website.models import *
from website.utils.LogHelper import LogHelper
from website.utils.answerHelper import AnswerHelper

from website.models import User, UserDetail, Organization, Address, OrganizationAddress, RoleType, OrganizationMember, Question, AnswerReference

import datetime, random
import json
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil

#mappings from natSolDB to our db
JURISTICTION_TYPE_MAPPING = {
    None: None,
    'City': 'CI',
    'County': 'CO',
    'City and County': 'CC',
    'Independent City': 'IC',
    'State Agency': 'S',
    'Unincorporated': 'U',
}

@login_required
def migrate_jurisdiction_data(request):
    user = request.user
    requestProcessor = HttpRequestProcessor(request)
    dajax = Dajax()
    data = {}
    data['message'] = ''
    
    log_files = []
    log_path = os.path.join(settings.LOG_ROOT, 'migration')
    files = [ f for f in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, f)) ]
    for file in reversed(files):
        log_file = {'name': file, 'url': '/media/log/migration/'+file}
        log_files.append(log_file)
    data['log_files'] = log_files
    
    if not user.is_superuser:
        return requestProcessor.render_to_response(request,'website/deny.html', {}, '')
    
    ajax = requestProcessor.getParameter('ajax')
    if ajax != None:
        #just checking progress
        if ajax == 'progress':
            progress = ServerVariable.get('migrate_jurisdiction_progress')
            dajax.assign('#progress_div','innerHTML', progress)
            status = ServerVariable.get('migrate_jurisdiction_status')
            if status == 'ended':
                dajax.assign('#status','innerHTML', 'ended')
                dajax.assign('#result_div','innerHTML', 'Migration ended.')
            return HttpResponse(dajax.json())
        
        #reset in case it is stuck
        if ajax == 'reset':
            ServerVariable.set('migrate_jurisdiction_progress', '')
            ServerVariable.set('migrate_jurisdiction_status', 'reset')
            dajax.assign('#status','innerHTML', 'ended')
            dajax.assign('#result_div','innerHTML', 'Migration reset.')
            return HttpResponse(dajax.json())
        
        #quick test of the migration process
        if ajax == 'test':
            #testing, limit records
            #alpha_list = ['u','z']
            #alpha_list = ['sam'] #include Sample Jurisdiction
            #alpha_list = ['san ']
            alpha_list = ['san ', 'sam'] #include Sample Jurisdiction
            #alpha_list = ['cloud', 'oakland'] #Oakland, Cloud has parent of Cloud
            #alpha_list = ['ma'] #address import test
            #alpha_list = ["O'"] #test bad char in jurisdiction name
            ajax = 'run'
            
        #start the complete migration process
        if ajax == 'start':
            alpha_list = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
            ajax = 'run'
            
        #run the migration process
        if ajax == 'run':
            #don't start another process if already running
            migrate_jurisdiction_status = ServerVariable.get('migrate_jurisdiction_status')
            if migrate_jurisdiction_status == 'started':
                dajax.assign('#progress_div','innerHTML', 'Process already running!')
                return HttpResponse(dajax.json())
            ServerVariable.set('migrate_jurisdiction_status', 'started') #remember this has started
            
            #standard data
            answer_helper = AnswerHelper()
            tab = '&nbsp;&nbsp;&nbsp;&nbsp;'
            answer_action_category = ActionCategory.objects.get(name='AddRequirement')
            vote_action_category = ActionCategory.objects.get(name='VoteRequirement')
            
            log_helper = LogHelper('migration', 'MigrateJurisdictions')
            log_helper.write_header()
            cursor = connections['natSolDB'].cursor()
            #cursor.execute("SELECT jurisdictionID, jurisdictionName, city, county, state, latitude, longitude, jurisdictionType, parentJurisdiction FROM nspd_jurisdictions")
            
            #load a dict of nspd org id to our organization objects
            cursor.execute('''SELECT *
                        FROM nspd_organizations
                        WHERE 1=1''', [])
            org_records = dictfetchall(cursor)
            org_lookup = {}
            has_org = False
            for org_record in org_records:
                organizations = Organization.objects.filter(name__iexact=org_record['oName'])
                if len(organizations) == 0:
                    dajax.assign('#result_div','innerHTML', 'Missing organization in this database:'+smart_unicode(org_record['oName']))
                    dajax.assign('#status','innerHTML', 'ended')
                    return HttpResponse(dajax.json())
                else:
                    has_org = True
                    organization = organizations[0]
                    org_lookup[org_record['oID']] = organization
            if has_org == False:
                    dajax.assign('#result_div','innerHTML', 'Unable to set up organization mapping.')
                    dajax.assign('#status','innerHTML', 'ended')
                    return HttpResponse(dajax.json())
            
            #loop alphabetically
            for alpha in alpha_list:
                #try:
                if True: #for testing to see exception
                    name_like = alpha+'%'
                    cursor.execute('''SELECT j.jurisdictionID AS id, j.jurisdictionName AS name, j.city, j.county, s.pusps AS state, j.latitude, j.longitude, t.name AS jurisdictionType, j.parentJurisdiction, j.created, j.lastModified
                        FROM nspd_jurisdictions AS j 
                        LEFT JOIN nspd_states AS s ON j.state = s.fips 
                        LEFT JOIN nspd_jurisdictionTypes AS t ON j.jurisdictionType = t.jurisdictionTypeID 
                        WHERE j.jurisdictionName LIKE %s''', [name_like])
                    records = dictfetchall(cursor)
                    
                    matching_jurisdiction_count = 0
                    new_jurisdiction_count = 0
                    record_count = 0
                    for record in records:
                        #ensure incoming text is clean unicode
                        record['name'] = smart_unicode(record['name'])
                        record['city'] = smart_unicode(record['city'])
                        record['county'] = smart_unicode(record['county'])
                        
                        notes = ''
                        notes2 = ''
                        #has it been migrated?
                        jid = MigrationHistory.get_target_id('nspd_jurisdictions', record['id'], 'Jurisdiction')
                        if jid != None:
                            similar_jurisdictions = Jurisdiction.objects.filter(id=jid)
                        else:
                            #find the same jurisdiction in our db by matching fields
                            #similar_jurisdictions = Jurisdiction.objects.filter(name=record['name'], city=record['city'], state=record['state'], jurisdiction_type=JURISTICTION_TYPE_MAPPING[record['jurisdictionType']])
                            similar_jurisdictions = [] #don't try to match, avoid similar ones
                        if len(similar_jurisdictions) > 0:
                            #for now, just use the first one
                            jurisdiction = similar_jurisdictions[0]
                            matching_jurisdiction_count += 1
                            #currently modifying jurisdiction even if already exist
                            
                        else:
                            jurisdiction = Jurisdiction(name=record['name'], city=record['city'], state=record['state'], jurisdiction_type=JURISTICTION_TYPE_MAPPING[record['jurisdictionType']])
                            #try to use the original id, if not exist in this db
                            same_id_jurisdictions = Jurisdiction.objects.filter(id=record['id'])
                            if len(same_id_jurisdictions) == 0:
                                jurisdiction.id = record['id']
                            
                            new_jurisdiction_count += 1
                            
                        jurisdiction.county = record['county']
                        jurisdiction.latitude = record['latitude']
                        jurisdiction.longitude = record['longitude']
                        jurisdiction.create_datetime = record['created']
                        jurisdiction.modify_datetime = record['lastModified']
                        jurisdiction.save()
                        
                        #if not exactly one match
                        if len(similar_jurisdictions) != 1:
                            log_helper.write_all('Warning - Name: '+record['name']+', County: '+record['county']+', State: '+record['state']+', Type: '+record['jurisdictionType']+' has '+str(len(similar_jurisdictions))+' matching jurisdictions in this database.')
                            for similar_jurisdiction in similar_jurisdictions:
                                log_helper.write_all(tab+similar_jurisdiction.name+', '+similar_jurisdiction.county+', '+similar_jurisdiction.state+', '+similar_jurisdiction.jurisdiction_type+'')
                        
                        notes += smart_unicode(jurisdiction.name)+', '+smart_unicode(jurisdiction.county)+', '+str(jurisdiction.state)+', '+str(jurisdiction.jurisdiction_type)
                        MigrationHistory.save_history(jurisdiction, 'nspd_jurisdictions', record['id'], 'Jurisdiction', jurisdiction.id, notes, notes2)
                        
                        #Migrate jurisdiction parent info
                        if record['parentJurisdiction'] != 0:
                            #look up parent j id in migration history
                            jurisdiction_histories = MigrationHistory.objects.filter(source_table='nspd_jurisdictions', source_id=record['parentJurisdiction'], target_table='Jurisdiction')
                            if len(jurisdiction_histories) == 0:
                                log_helper.write_all('Warning - Name: '+record['name']+', County: '+record['county']+', State: '+record['state']+', Type: '+record['jurisdictionType']+' Cannot set parent jurisdiction, not migrated yet, parent natSolDB id: '+str(record['parentJurisdiction'])+'.')
                                notes2 += 'Warning: Cannot set parent jurisdiction, not migrated yet, parent natSolDB id: '+str(record['parentJurisdiction'])
                                MigrationHistory.save_history(jurisdiction, 'nspd_jurisdictions', record['id'], 'Jurisdiction', jurisdiction.id, notes, notes2)
                            else:
                                jurisdiction_history = jurisdiction_histories[0]
                                parent_jurisdictions = Jurisdiction.objects.filter(id=jurisdiction_history.target_id)
                                if len(parent_jurisdictions) == 0:
                                    log_helper.write_all('Warning - Name: '+record['name']+', County: '+record['county']+', State: '+record['state']+', Type: '+record['jurisdictionType']+' Cannot look up parent jurisdiction, id: '+str(jurisdiction_history.target_id)+'.')
                                else:
                                    parent_jurisdiction = parent_jurisdictions[0]
                                    jurisdiction.parent = parent_jurisdiction
                                    jurisdiction.save()
                                    notes2 += 'Parent jurisdiction id: '+str(parent_jurisdiction.id)+ ', name: '+parent_jurisdiction.name
                                    MigrationHistory.save_history(jurisdiction, 'nspd_jurisdictions', record['id'], 'Jurisdiction', jurisdiction.id, notes, notes2)
                                    
                        #look up existing answers in natSolDB
                        cursor.execute('''SELECT * 
                        FROM nspd_answers AS a
                        WHERE a.jurisdictionID = %s
                        ORDER BY a.questionID, a.created''', [record['id']])
                        answer_records = dictfetchall(cursor)
                        
                        if len(answer_records) > 0:
                            log_helper.write_log('Name: '+record['name']+', County: '+record['county']+', State: '+record['state']+', Type: '+record['jurisdictionType']+' - has '+str(len(answer_records))+' answers in natSolDB.')
                            
                            #get all answers already in our db for this jurisdiction
                            #answers = AnswerReference.objects.filter(jurisdiction=jurisdiction).order_by('question__id')
                            #log_helper.write_log(tab+'This database has '+str(len(answers))+' answers.')
                            
                        #loop through the answer records
                        last_edit_time = None
                        last_contributor = None
                        for answer_record in answer_records:
                            answer_notes = 'Question ID: '+str(answer_record['questionID'])+' '
                            answer_value = answer_helper.format_import_answer(answer_record)
                            answer_notes += smart_unicode(answer_value)
                            answer_notes2 = ''
                            #log_helper.write_log(tab+'Question ID: '+str(answer_record['questionID'])+' Answer: '+answer_value)
                            #skip if this answer is a child of another question
                            if answer_helper.is_child_answer(answer_record) == True:
                                #log_helper.write_log(tab+'Answer to child question, skipping.')
                                answer_notes2 += 'Child answer, to be migrated with parent.'
                                MigrationHistory.save_history(jurisdiction, 'nspd_answers', answer_record['answerID'], 'AnswerReference', None, answer_notes, answer_notes2)
                                continue
                            
                            #does this question has child questions
                            child_answer_records = answer_helper.get_child_answers(answer_record, answer_records)
                            for child_answer_record in child_answer_records:
                                answer_notes += 'Has child answer with Question ID: '+str(child_answer_record['questionID'])+'.'
                            
                            #check if answer already in our db
                            #look up our user from natSolDB user id
                            creator = UserDetail.get_migrated_user_by_id(answer_record['creatorUserID'])
                            if creator == None:
                                log_helper.write_all(tab+'Warning - User from natSolDB with ID: '+str(answer_record['creatorUserID'])+' does not exist in this DB, answer skipped.')
                                continue #skip
                            
                            #get question, question id in both dbs should be the same
                            try:
                                question = Question.objects.get(id=answer_record['questionID'])
                            except:
                                #log_helper.write_log(tab+tab+'Failed to find question in this DB with id:'+str(answer_record['questionID'])+', skipped.')
                                answer_notes2 += 'Warning: no such question to migrate over.'
                                MigrationHistory.save_history(jurisdiction, 'nspd_answers', answer_record['answerID'], 'AnswerReference', None, answer_notes, answer_notes2)
                                #can't import this answer
                                continue
                            #has it been migrated?
                            new_answer = False
                            aid = MigrationHistory.get_target_id('nspd_answers', answer_record['answerID'], 'AnswerReference')
                            if aid != None:
                                similar_answers = AnswerReference.objects.filter(id=aid)
                                matching_answer = similar_answers[0]
                            else:
                                #exclude other answers already migrated
                                migrated_answer_ids = MigrationHistory.objects.filter(source_table='nspd_answers', source_id=answer_record['answerID'], target_table='AnswerReference').values_list('target_id', flat=True)
                                #similar answer not migrated
                                similar_answers = AnswerReference.objects.filter(jurisdiction=jurisdiction, question=question, creator=creator).exclude(id__in=migrated_answer_ids)
                                matching_answer = None
                                new_answer = True
                                for similar_answer in similar_answers:
                                    if answer_helper.is_answer_match(answer_record, similar_answer):
                                        matching_answer = similar_answer
                                        new_answer = False
                                        #log_helper.write_log(tab+tab+'Has matching answer in this DB.')
                            if matching_answer == None:
                                #log_helper.write_log(tab+tab+'No matching answer in this DB.')
                                #add answer
                                matching_answer = AnswerReference(jurisdiction=jurisdiction, question=question, creator=creator)
                            
                            #if address, try to get value from nspd_addresses
                            if question.migration_type == 'address':
                                cursor.execute('''SELECT * 
                                FROM nspd_addresses
                                WHERE answerId = %s''', [answer_record['answerID']])
                                address_records = dictfetchall(cursor)
                                if len(address_records) == 0:
                                    #no address yet, put into free-form
                                    matching_answer.value = answer_helper.migrate_answer_value(question, answer_record, child_answer_records)
                                    answer_notes2 += 'Warning - using free-form address: '+smart_unicode(matching_answer.value)
                                
                                else:
                                    address_record = address_records[0] #should have only one anyway
                                    #pass in address_record instead of answer record
                                    matching_answer.value = answer_helper.migrate_answer_value(question, address_record, child_answer_records, True) #is_special=True
                                    answer_notes2 += 'From nspd_addresses: '+smart_unicode(matching_answer.value)
                                
                            else:
                                matching_answer.value = answer_helper.migrate_answer_value(question, answer_record, child_answer_records)
                                answer_notes2 += smart_unicode(matching_answer.value)
                                
                            #log_helper.write_log(tab+tab+'Answer JSON: '+matching_answer.value)
                            matching_answer.is_callout = answer_record['isCallout']
                            if answer_record['isValidated'] == 1:
                                matching_answer.approval_status = 'A'
                            else:
                                matching_answer.approval_status = 'P'
                            if answer_record['creatorOrgID'] != None:
                                try:
                                    organization = org_lookup[answer_record['creatorOrgID']]
                                    matching_answer.organization = organization
                                except:
                                    answer_notes2 += ' Warning - failed to look up organization: '+smart_unicode(answer_record['creatorOrgID'])
                            matching_answer.migrated_answer_id = answer_record['answerID']
                            matching_answer.creator = creator
                            matching_answer.save()
                            #save again to aviod auto_now_add value
                            matching_answer.create_datetime = answer_record['created']
                            matching_answer.modify_datetime = answer_record['created']
                            matching_answer.status_datetime = answer_record['created']
                            matching_answer.save()
                            
                            MigrationHistory.save_history(jurisdiction, 'nspd_answers', answer_record['answerID'], 'AnswerReference', matching_answer.id, answer_notes, answer_notes2)
                            
                            #Action for Answer
                            matching_answer_action = None
                            answer_action_notes = ''
                            answer_action_notes2 = ''
                            similar_answer_actions = Action.objects.filter(user=creator, category=answer_action_category, entity_id=matching_answer.id)
                            if len(similar_answer_actions) > 0:
                                #already has this action
                                matching_answer_action = similar_answer_actions[0] #should be only one anyway
                                #log_helper.write_log(tab+tab+'Already has same answer action in DB.')
                            else:
                                #if no match, add
                                matching_answer_action = Action(user=creator, category=answer_action_category, entity_id=matching_answer.id)
                                #log_helper.write_log(tab+tab+'No matching answer action in DB.')
                            matching_answer_action.jurisdiction = jurisdiction
                            matching_answer_action.question_category = question.category
                            matching_answer_action.entity_name = 'Requirement'
                            #matching_answer_action.entity_name = 'AnswerReference' #TODO: should be changed to this in the whole app
                            matching_answer_action.data = 'Answer: '+matching_answer.value
                            matching_answer_action.scale = answer_action_category.points
                            matching_answer_action.save()
                            #save again to aviod auto_now_add value
                            matching_answer_action.action_datetime = answer_record['created']
                            matching_answer_action.save()
                            
                            answer_action_notes += ''
                            answer_action_notes2 += ''
                            MigrationHistory.save_history(jurisdiction, 'nspd_answers', answer_record['answerID'], 'Action', matching_answer_action.id, answer_action_notes, answer_action_notes2)
                            
                            # TODO: save action for Vote
                            #vote_action.save()
                            
                            #look up comments for this answer in natSolDB
                            cursor.execute('''SELECT * 
                            FROM nspd_comments
                            WHERE answerID = %s
                            ORDER BY created''', [answer_record['answerID']])
                            comment_records = dictfetchall(cursor)
                            
                            #loop through the comments
                            for comment_record in comment_records:
                                #look up our user from natSolDB user id
                                commenter = UserDetail.get_migrated_user_by_id(comment_record['uID'])
                                if commenter == None:
                                    log_helper.write_all(tab+'Warning - User from natSolDB with ID: '+str(comment_record['uID'])+' does not exist in this DB, comment skipped.')
                                    continue #skip
                                
                                #check if the comment is already in our db
                                #has it been migrated?
                                matching_comment = None
                                cid = MigrationHistory.get_target_id('nspd_comments', comment_record['commentID'], 'Comment')
                                if cid != None:
                                    similar_comments = Comment.objects.filter(id=cid)
                                    if len(similar_comments) > 0:
                                        matching_comment = similar_comments[0] #there should be only one
                                if matching_comment == None:
                                    #add new comment
                                    matching_comment = Comment()
                                    
                                matching_comment.jurisdiction = jurisdiction
                                matching_comment.entity_name = 'AnswerReference'
                                matching_comment.entity_id = matching_answer.id
                                matching_comment.user = commenter
                                matching_comment.comment_type = 'JC' #'Jurisdiction Comment'
                                matching_comment.comment = smart_unicode(comment_record['comment'])
                                matching_comment.parent_comment = None
                                if comment_record['isFlagged'] == 1:
                                    matching_comment.approval_status = 'F'
                                else:
                                    matching_comment.approval_status = 'P'
                                matching_comment.save()
                                #save again to aviod auto_now_add value
                                matching_comment.create_datetime = comment_record['created']
                                matching_comment.save()
                                    
                                comment_notes = ''
                                comment_notes2 = matching_comment.comment
                                MigrationHistory.save_history(jurisdiction, 'nspd_comments', comment_record['commentID'], 'Comment', matching_comment.id, comment_notes, comment_notes2)
                                    
                            #look up votes for this answer in natSolDB
                            cursor.execute('''SELECT * 
                            FROM nspd_votes AS v
                            WHERE v.answerID = %s
                            ORDER BY v.modified''', [answer_record['answerID']])
                            vote_records = dictfetchall(cursor)
                            if len(vote_records) > 0:
                                #log_helper.write_log(tab+tab+'This answer has '+str(len(vote_records))+' votes.')
                                pass
                            
                            #loop through the votes
                            for vote_record in vote_records:
                                #look up our user from natSolDB user id
                                voter = UserDetail.get_migrated_user_by_id(vote_record['uID'])
                                if voter == None:
                                    log_helper.write_all(tab+'Warning - User from natSolDB with ID: '+str(answer_record['creatorUserID'])+' does not exist in this DB, answer skipped.')
                                    continue #skip

                                #check if the vote is already in our db
                                #has it been migrated?
                                vote_action = None
                                vid = MigrationHistory.get_target_id('nspd_votes', vote_record['voteID'], 'Action')
                                if vid != None:
                                    similar_votes = Action.objects.filter(id=vid)
                                    if len(similar_votes) > 0:
                                        vote_action = similar_votes[0] #there should be only one
                                if vote_action == None:
                                    #add new vote action
                                    vote_action = Action()

                                vote_action.user = voter
                                vote_action.category = vote_action_category
                                vote_action.entity_id = matching_answer.id
                                vote_action.jurisdiction = jurisdiction
                                vote_action.question_category = question.category
                                vote_action.entity_name = 'reference'
                                #vote_action.entity_name = 'AnswerReference' #TODO: should be changed to this in the whole app
                                if vote_record['voteIsPositive'] == 1:
                                    vote_action.data = 'Vote: Up'
                                else:
                                    vote_action.data = 'Vote: Down'
                                vote_action.scale = 2
                                vote_action.save()
                                #save again to aviod auto_now_add value
                                vote_action.action_datetime = vote_record['modified']
                                vote_action.save()
                                
                                vote_notes = ''
                                vote_notes2 = vote_action.data
                                MigrationHistory.save_history(jurisdiction, 'nspd_votes', vote_record['voteID'], 'Action', vote_action.id, vote_notes, vote_notes2)
                            #end votes loop
                                
                            #print str(last_edit_time) +', ' + str(record['created'])
                            if last_edit_time == None or last_edit_time < record['created']:
                                last_edit_time = record['created']
                                last_contributor = creator
                            
                        #end answers loop
                            
                                
                        if last_edit_time != None:
                            jurisdiction.last_contributed = last_edit_time
                            jurisdiction.last_contributed_by = last_contributor
                            org_members = OrganizationMember.objects.filter(user=last_contributor)
                            if len(org_members) > 0:
                                org = org_members[0].organization
                                jurisdiction.last_contributed_by_org = org
                            jurisdiction.save()
                            
                        record_count += 1
                        progress_text = 'Name starting with "'+alpha+'": '+str(record_count)+' of '+str(len(records))+' records processed'
                        ServerVariable.set('migrate_jurisdiction_progress', progress_text)
                        
                    #end records loop
                    
                    log_helper.write_all(str(len(records))+' jurisdictions starting with "'+alpha+'" in natSolDB.')
                    log_helper.write_all(str(matching_jurisdiction_count)+' matching jurisdictions starting with "'+alpha+'" in this DB.')
                    log_helper.write_all('Added '+str(new_jurisdiction_count)+' jurisdictions starting with "'+alpha+'" to this DB.')
                
                #comment out except and handling for test...
                #except Exception, e:
                    #log_helper.write_all('Exception: '+str(e))
                
                    
            ServerVariable.set('migrate_jurisdiction_status', 'ended') #update server status
            
            log_helper.write_footer()
    
            #dajax.assign('#result_div','innerHTML', log_helper.log_buffer)
            dajax.assign('#result_div','innerHTML', 'Migration completed.')
            dajax.assign('#status','innerHTML', 'ended')
            
            #update showing of log files
            log_files = []
            log_path = os.path.join(settings.LOG_ROOT, 'migration')
            files = [ f for f in os.listdir(log_path) if os.path.isfile(os.path.join(log_path, f)) ]
            #for file in reversed(files):
            for file in files:
                log_file = {'name': file, 'url': '/media/log/migration/'+file}
                log_files.append(log_file)
            data['log_files'] = log_files
            body = requestProcessor.decode_jinga_template(request,'website/utils/migration_logs.html', data, '')
            dajax.assign('#log_div','innerHTML', body)
            
            return HttpResponse(dajax.json())
                
                
    return requestProcessor.render_to_response(request,'website/utils/migrate_jurisdictions.html', data, '')  

#show jurisdiction migration result on a page, admin only
@login_required
def jurisdiction_migration_result(request, id):
    user = request.user
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    
    if not user.is_staff and not user.is_superuser: #admin only
        return requestProcessor.render_to_response(request,'website/deny.html', {}, '')
    
    data['jurisdiction'] = jurisdiction= Jurisdiction.objects.filter(id=id)
    data['histories'] = histories = MigrationHistory.objects.filter(jurisdiction_id=id).exclude(target_table='Action').order_by('source_table','source_id')
    
    return requestProcessor.render_to_response(request,'website/utils/migration_result.html', data, '')  

@login_required
def migrate_unincorporated(request):
    user = request.user
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    miss_parent_jurisdiction = []
    unincorporated_add_num = 0
    unincorporated_update_num = 0
    unincorporated_without_parent_num = 0
    if not user.is_superuser:
        return requestProcessor.render_to_response(request,'website/deny.html', {}, '')      
    
    cursor = connections['natSolDB'].cursor()
        
    cursor.execute("SELECT fips, pusps, status FROM nspd_states")
    records = dictfetchall(cursor)
            
    states = {}
    for record in records:
        states[record['fips']] = record['pusps']
    
    cursor.execute("SELECT jurisdictionID, jurisdictionName, city, county, state, latitude, longitude, jurisdictionType, parentJurisdiction FROM nspd_jurisdictions n WHERE n.jurisdictionType = 6 ")
    records = dictfetchall(cursor)  
    for record in records:
        #print record['longitude']
        jurisdictions = Jurisdiction.objects.filter(name__iexact=record['jurisdictionName'], latitude__iexact=record['latitude'], longitude__iexact=record['longitude'], jurisdiction_type__iexact='U')
        if jurisdictions:
            jurisdiction = jurisdictions[0]
            unincorporated_update_num += 1
        else:
            jurisdiction = Jurisdiction()
            unincorporated_add_num += 1
            if record['parentJurisdiction'] == '' or record['parentJurisdiction'] == None:
                unincorporated_without_parent_num +=1
                miss_parent_jurisdiction.append(record['jurisdictionName'])
            else:
                cursor.execute("SELECT jurisdictionID, jurisdictionName, city, county, state, latitude, longitude, jurisdictionType, parentJurisdiction FROM nspd_jurisdictions n WHERE n.jurisdictionID = " + str(record['parentJurisdiction']))
                parent_records = dictfetchall(cursor)
                if parent_records:
                    parent_record = parent_records[0]
                    parent_jurisdictions = None
                    if parent_record['jurisdictionType'] == 1:
                        parent_jurisdictions = Jurisdiction.objects.filter(name__iexact=parent_record['jurisdictionName'], latitude__iexact=parent_record['latitude'],longitude__iexact=parent_record['longitude'], jurisdiction_type__iexact='CI')
                    elif parent_record['jurisdictionType'] == 2:
                        parent_jurisdictions = Jurisdiction.objects.filter(name__iexact=parent_record['jurisdictionName'], latitude__iexact=parent_record['latitude'],longitude__iexact=parent_record['longitude'], jurisdiction_type__iexact='CO')
                    elif parent_record['jurisdictionType'] == 3:
                        parent_jurisdictions = Jurisdiction.objects.filter(name__iexact=parent_record['jurisdictionName'], latitude__iexact=parent_record['latitude'],longitude__iexact=parent_record['longitude'], jurisdiction_type__iexact='CC')
                    #else:
                    
                    if parent_jurisdictions:
                        parent_jurisdiction = parent_jurisdictions[0]
                        jurisdiction.parent = parent_jurisdiction
                    else:
                        unincorporated_without_parent_num +=1
                        miss_parent_jurisdiction.append(record['jurisdictionName'])
                else:
                    unincorporated_without_parent_num +=1
                    miss_parent_jurisdiction.append(record['jurisdictionName'])
        jurisdiction.name = record['jurisdictionName']
        jurisdiction.jurisdiction_type = 'U'
        jurisdiction.city = record['city']
        jurisdiction.county = record['county']
        jurisdiction.state = states[record['state']]
        jurisdiction.latitude = record['latitude']
        jurisdiction.longitude = record['longitude']
        jurisdiction.save()
    data['miss_parent_jurisdiction'] = miss_parent_jurisdiction   
    data['unincorporated_add_num'] = unincorporated_add_num
    data['unincorporated_update_num'] = unincorporated_update_num
    data['unincorporated_without_parent_num'] = unincorporated_without_parent_num
    return requestProcessor.render_to_response(request,'website/utils/migrate_unincorporated.html', data, '')  

def dictfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        dict(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]
    
    
#@csrf.csrf_protect
def set_up_data_sprint_19(request):
    if request.user.is_authenticated() and request.user.is_superuser == 1:   
        set_up_county_city_relationship()
        
        match_user_n_details()
        
        #migrate_temmplatequestion_to_question()    no need.  to be done by initial_data.json
        
    return HttpResponseRedirect("/")         
    
def set_up_county_city_relationship():
    return
    counties = Jurisdiction.objects.filter(jurisdiction_type='CO').order_by('state', 'name')
    for county in counties:
        cities = Jurisdiction.objects.filter(jurisdiction_type='CI',  state__iexact=county.state, county__istartswith=county.name).order_by('state', 'city') 
        for city in cities:
            city.parent_id = county.id
            city.save()
            
        
def match_user_n_details():
    return
    users = User.objects.all()
    for user in users:
        user_detail = UserDetail.objects.filter(user=user)
        if len(user_detail) == 0:
            user_detail = UserDetail()
            user_detail.user_id = user.id
            user_detail.display_preference = 'username'
            user_detail.save()
            
def migrate_temmplatequestion_to_question():
    template_questions = TemplateQuestion.objects.all()
    for template_question in template_questions:
        try:
            question = Question.objects.get(id=template_question.question_id)
            question.qtemplate_id = template_question.template_id
            question.save()
        except:
            print "no question for id = " + str(template_question.question_id)
            
def migrate_organizationMember():
    return
    members = OrganizationMember.objects.filter(role__id = 3)
    role = RoleType.objects.get(id = 1)
    for member in members:
        member.role = role
        member.save()

@login_required
def migrate_users(request):
    user = request.user
    requestProcessor = HttpRequestProcessor(request)
    data = {}
    
    print "data migration starts >>>>>>>>>> "
    if not user.is_superuser:
        return requestProcessor.render_to_response(request,'website/deny.html', {}, '')  
    

    cursor = connections['natSolDB'].cursor()
    
    cursor.execute("SELECT fips, pusps, status FROM nspd_states")
    records = dictfetchall(cursor)
            
    states = {}
    for record in records:
        states[record['fips']] = record['pusps']  
    
    
    # get unique jurisdictionID from natSolDB's answers.
    # get same jurisdiction from doe_dev
    # build matching_jurisdictions
    '''
    matching_jurisdictions = {}
    no_matching_jurisdictions = {}
    cursor.execute("SELECT jurisdictionID, jurisdictionName, city, county, state, jurisdictionType FROM nspd_jurisdictions n WHERE n.jurisdictionID IN (SELECT DISTINCT a.jurisdictionID FROM nspd_answers a)")
    records = dictfetchall(cursor)    
    
    print "distinct jurs from nspd count :: " + str(len(records))
    for record in records:
        print "nspd jur :: " 
        print str(record['jurisdictionName']) + '-' + str(record['city']) + '-' + str(record['county'])       
        if record['jurisdictionType'] == 1:
            jurisdictions = Jurisdiction.objects.filter(name__iexact=record['jurisdictionName'],city__iexact=record['city'],county__iexact=record['county'],state__iexact=states[record['state']], jurisdiction_type__iexact='CI')   
        elif record['jurisdictionType'] == 2:
            jurisdictions = Jurisdiction.objects.filter(name__iexact=record['jurisdictionName'],county__iexact=record['county'],state__iexact=states[record['state']], jurisdiction_type__iexact='CO')  
        elif record['jurisdictionType'] == 3:
            jurisdictions = Jurisdiction.objects.filter(name__iexact=record['jurisdictionName'],city__iexact=record['city'],county__iexact=record['county'],state__iexact=states[record['state']], jurisdiction_type__iexact='CC')  
            
        if jurisdictions:
            #print "doe jur match found"
            matching_jurisdictions[record['jurisdictionID']] = jurisdictions[0].id
        else:
            print ">>>>>>>>>> doe jur match NOT FOUND >>> " + str(record['jurisdictionName'])
            no_matching_jurisdictions[record['jurisdictionID']] = record['jurisdictionName'] + '-' + str(record['city']) + '-' + record['county'] + '-' + str(record['state'])
              
    print "matching_jurisdictions count :: " + str(len(matching_jurisdictions))
    print "no_matching_jurisdictions count :: " + str(len(no_matching_jurisdictions))
    print "no_matching_jurisdictions :: "
    print no_matching_jurisdictions
    
    
    matching_question_categories = {}
    cursor.execute("SELECT questionCategoryID, questionCategory FROM nspd_questionCategories")
    records = dictfetchall(cursor)    
    for record in records:
        question_categories = QuestionCategory.objects.filter(name__iexact=record['questionCategory'])    
        if question_categories:
            matching_question_categories[record['questionCategoryID']] = question_categories[0].id        
     
    print "matching_question_categories count :: " + str(len(matching_question_categories))      
    
    # get unique questionID from natSolDB's answers.
    # get same question from doe_dev
    # build matching_questions
    matching_questions = {}
    no_matching_questions = {}
    cursor.execute("SELECT q.questionID, questionCategoryID, question FROM nspd_questions q WHERE q.questionID IN (SELECT DISTINCT a.questionID FROM nspd_answers a)")
    records = dictfetchall(cursor)    
    
    print "distinct questionID from nspd count :: " + str(len(records))
    for record in records:
        print str(record['questionID']) + '-' + str(record['question'])  
        question_category_id = matching_question_categories[record['questionCategoryID']]
        questionCategory = QuestionCategory.objects.get(id=question_category_id)
        questions = Question.objects.filter(category__exact=questionCategory, question__iexact=record['question'])
            
        if questions:
            #print "doe question match found"
            matching_questions[record['questionID']] = questions[0].id
        else:
            print ">>>>>>>>>> doe question match NOT FOUND >>> " + str(record['questionID']) + '_' + str(record['question'])
            no_matching_questions[record['questionID']] = record['question']
              
    print "matching_questions count :: " + str(len(matching_questions))
    print "no_matching_questions count :: " + str(len(no_matching_questions))
    print "no_matching_questions :: "
    print no_matching_questions    

    '''         
    
    # organization
    matching_orgs = {}
    nspd_org_owners = {}
    cursor.execute("SELECT oID, oName, oDescription, oOwnerID, oPhone, oAddress, oAddress2, oCity, oState, oZip, oUrl  FROM nspd_organizations")
    records = dictfetchall(cursor)        
    data['nspd_organizations'] = len(records)
    org_added = 0
    org_existed = 0
    for record in records:
        doe_orgs = Organization.objects.filter(name__iexact=record['oName'])    # assumption: org name is unique
        if doe_orgs:
            print "org already exists.  check if has address." + str(record['oName'])
            org = doe_orgs[0]
            org_id = org.id
            org_existed = org_existed + 1
            if record['oDescription'] != None:
                org.description=record['oDescription']
            if record['oPhone'] != None:
                org.phone=record['oPhone']
            if record['oUrl'] != None:            
                org.website=record['oUrl']  
            org.save()          
            
            
            doe_org_addresses = OrganizationAddress.objects.filter(organization__exact=doe_orgs[0])
            if doe_org_addresses:
                print "address already exists.  don't add the address"
            else:
                if record['oAddress'] != None or record['oAddress2'] != None or record['oCity'] != None or record['oState'] != None or record['oZip'] != None:
                    address = Address()
                    if record['oAddress'] != None:
                        address.address1=record['oAddress']
                    if record['oAddress2'] != None:
                        address.address2=record['oAddress2']
                    if record['oCity'] != None:
                        address.city=record['oCity']
                    if record['oState'] != None:
                        address.state=states[record['oState']]
                    if record['oZip'] != None:
                        address.zip_code=record['oZip']
                    address.save()         
                    print "add address"
                    organization_address = OrganizationAddress(organization_id=org_id, address_id=address.id)
                    organization_address.save()   
                    print "add org address" 
                else:
                    print "don't add address because data is not provided"                                           
        else:
            org = Organization()
            org.name=record['oName']
            
            if record['oDescription'] != None:
                org.description=record['oDescription']
            if record['oPhone'] != None:
                org.phone=record['oPhone']
            if record['oUrl'] != None:            
                org.website=record['oUrl']
            org.save()
            org_added = org_added + 1
            org_id = org.id
            print "add org >>>> " + str(record['oName'])
            if record['oAddress'] != None or record['oAddress2'] != None or record['oCity'] != None or record['oState'] != None or record['oZip'] != None:
                address = Address()
                if record['oAddress'] != None:
                    address.address1=record['oAddress']
                if record['oAddress2'] != None:
                    address.address2=record['oAddress2']
                if record['oCity'] != None:
                    address.city=record['oCity']
                if record['oState'] != None:
                    address.state=states[record['oState']]
                if record['oZip'] != None:
                    address.zip_code=record['oZip']
                address.save()
                print "add address "
                organization_address = OrganizationAddress(organization_id=org_id, address_id=address.id)
                organization_address.save()
                print "add org address"
            else:
                print "don't add address because data is not provided"

            
        
        matching_orgs[record['oID']] = org_id
        nspd_org_owners[record['oID']] = record['oOwnerID']
        
    print "matching orgs :: " + str(len(matching_orgs))
    print matching_orgs
        
    data['org_added'] = org_added
    data['org_existed'] = org_existed
    
    # user
    nspd_user_org = {}
    nspd_org_user = {}
    cursor.execute("SELECT uID, oID FROM nspd_userOrganizations")
    records = dictfetchall(cursor)      
    for record in records:
        nspd_user_org[record['uID']] = record['oID']
        if record['oID'] not in nspd_org_user:
            nspd_org_user[record['oID']] = record['uID']
            
    ownerRole = RoleType.objects.get(name="Administrator")
    memberRole = RoleType.objects.get(name="Member")
            
    matching_users = {}
    cursor.execute("SELECT uID, uName, uEmail, uPassword, uIsActive, uDateAdded, uLastLogin FROM Users")
    records = dictfetchall(cursor)      
    
    data['nspd_users'] = len(records)
    user_added = 0
    user_existed = 0
        
    for record in records:
        if record['uID'] in nspd_user_org:      # this user belongs to an org
            nspd_org_id = nspd_user_org[record['uID']]
            doe_org_id = matching_orgs[nspd_org_id]
            
            if nspd_org_id in nspd_org_owners:  # this org has an owner
                if record['uID'] == nspd_org_owners[nspd_org_id]:   # this user is an org owner
                    role_id = ownerRole.id
                else:
                    role_id = memberRole.id  
            else:
                role_id = memberRole.id            
        else:
            doe_org_id = 0
                              
        users_by_email_username = User.objects.filter(email__iexact=record['uEmail'], username__iexact=record['uName'])
        if users_by_email_username:
            print 'exact user already exists. same email, same username. update it.'
            user = users_by_email_username[0]   # should be only one user with that unique username
            update(user, record)
            user_existed = user_existed + 1
            user_id = user.id
        else:
            print "check if any user with email similar to that of the incoming record."
            users_by_email = User.objects.filter(email__iexact=record['uEmail'])
            if users_by_email:
                for user in users_by_email: # there may be more than one with email similar to the incoming one.
                    users_by_uname = User.objects.filter(username__iexact=record['uName']).exclude(email__iexact=record['uEmail'])
                    if users_by_uname:
                        "the username exists in the system. give the incoming username to the user in question.  but first change the username of all the found users"
                        user_with_same_uname = users_by_uname[0] # by unique name, should be only one.
                        user_with_same_uname.username = user_with_same_uname.username + str(random.randrange(1,100+1))
                        user_with_same_uname.save()
                        
                    # update the user with the new username
                    update(user, record)
                    user_existed = user_existed + 1
                    user_id = user.id                     
            else:
                # no record with similar email.  check if any similar username
                print "no similar email.  check if any user with username similar to that of the incoming record."
                users_by_uname = User.objects.filter(username__iexact=record['uName'])
                if users_by_uname:
                    print "user " + str(record['uName']) + ' already exists. '   
                    user = users_by_uname[0] # only one allowed by the system     
                    update(user, record)
                    user_existed = user_existed + 1
                    user_id = user.id 
                else:
                    print "incoming record has no similar email or uname in the existing db. >>>> add as the new user."
                    user = User()
                    user.username = record['uName']
                    user.email = record['uEmail']                    
                    user.is_active=record['uIsActive']
                    user.last_login=datetime.datetime.fromtimestamp(record['uLastLogin']) #need to convert to right format
                    user.date_joined=record['uDateAdded']     
                    user.save()       
                    user_added = user_added + 1  
                    user_id = user.id           
                    
        user = User.objects.get(id=user_id)
        user_details = UserDetail.objects.filter(user__exact=user)
        if user_details:
            user_detail = user_details[0]
            user_detail.old_password = record['uPassword']
            user_detail.migrated_id = record['uID']                 
            user_detail.save()
        else:
            user_detail = UserDetail()
            user_detail.user_id = user_id
            user_detail.old_password = record['uPassword']
            user_detail.migrated_id = record['uID']              
            user_detail.save()             
                      
        if doe_org_id > 0:
            print "This user belongs to an org."
            org = Organization.objects.get(id=doe_org_id)
            doe_org_members = OrganizationMember.objects.filter(user__exact=user, organization__exact=org)
            if doe_org_members:
                print "user already a member to the same org in doe as in nspd.  don't add another one."
            else:
                print "add member to org in doe as in nspd"       
                org_member = OrganizationMember(organization_id=doe_org_id, user_id=user_id,role_id=role_id, status='A')
                org_member.save()
        else:
            print "This user belongs to no org in nspd."
                                                
        matching_users[record['uID']] = user_id
        
    print "matching users count :: " + str(len(matching_users))
    print matching_users

    data['matching_users'] = len(matching_users)
    data['user_added'] = user_added
    data['user_existed'] = user_existed                
    
    '''
    # answer
    matching_answers = {}
    answers_not_added = {}
    added_answer_count = 0
    action_category = ActionCategory.objects.filter(name__iexact='AddRequirement')
    entity_name='Requirement'  
    cursor.execute("SELECT answerID, jurisdictionID, questionID, creatorOrgID, isValidated, textValue, tinytextValue, tinyintValue, smallintValue, mediumintValue, intValue, timeValue, created FROM nspd_answers")
    records = dictfetchall(cursor)          
    answer_added = 0
    answer_existed = 0 
    
    data['nspd_answers'] = len(records)    
    for record in records:

        if record['textValue'] != None:
            answer_data = record['textValue']
        elif record['tinytextValue'] != None:
            answer_data = record['tinytextValue']
        elif record['tinyintValue'] != None:
            answer_data = record['tinyintValue']
        elif record['smallintValue'] != None:
            answer_data = record['smallintValue']
        elif record['mediumintValue'] != None:
            answer_data = record['mediumintValue']
        elif record['intValue'] != None:
            answer_data = record['intValue']
        elif record['timeValue'] != None:
            answer_data = record['timeValue']
        else:
            answer_data = None
           
        if answer_data != None: 
            if record['jurisdictionID'] in matching_jurisdictions:
                jurisdiction_id = matching_jurisdictions[record['jurisdictionID']]
                #user_id = matching_users[record['uID']]
                contributorOrgId = matching_orgs[record['creatorOrgID']]    # user this to figure out contribution
                
                question_id = matching_questions[record['questionID']] 
                
                # may need to avoid adding answers already existed in the system caused by previous migration.
                question = Question.objects.get(id=question_id)
                question_category_ids = QuestionCategory.objects.filter(question__exact=question)
                question_category_id = question_category_ids[0].id
                       
                jurisdiction = Jurisdiction.objects.get(id=matching_jurisdictions[record['jurisdictionID']])
                if isinstance(answer_data, (int, long)):
                    answer_value = str(answer_data)
                else:
                    answer_value = answer_data.encode('utf-8')     
                               
                doe_jur_answers = AnswerReference.objects.filter(question__exact=question, jurisdiction__exact=jurisdiction, migrated_answer_id__exact=record['answerID'])
                
                if doe_jur_answers:
                    answer_existed = answer_existed + 1
                else:
                    answer = AnswerReference()
                    answer.question_id = question_id
                    answer.value = answer_value
                    answer.jurisdiction_id = jurisdiction_id
                    #answer.is_current = ''                  # need to check the other database
                    #answer.rating = ''                      # vote data?
                    if record['isValidated'] == 1:
                        answer.rating_status = 'C'
                    else:
                        answer.rating_status = 'U'
                    #answer.approal_status = ''

                    if record['creatorOrgID'] in nspd_org_user:
                        nspd_user_id = nspd_org_user[record['creatorOrgID']]
                        if nspd_user_id != 0:
                            if nspd_user_id in matching_users:
                                answer.creator_id = matching_users[nspd_user_id] # no creatorID, so we use org owner instead.
                    
                    answer.create_datetime = record['created']
                    answer.migrated_answer_id = record['answerID']
                    answer.save()
                    answer_added = answer_added + 1
                    matching_answers[record['answerID']] = answer.id
                    added_answer_count = added_answer_count + 1
                    #answer_data = str(answer.value) 
                    
                    contributionHelper = ContributionHelper()  
                    contributionHelper.save_action('AddRequirement', answer.value, answer.id, entity_name, answer.creator_id, jurisdiction_id )
          
            else:
                answers_not_added[record['answerID']] = str(record['answerID']) + 'answer not added because no matching jurisdiction'
        else:
            answers_not_added[record['answerID']] = str(record['answerID']) + 'answer not added because no actual data'
            
    data['answer_added'] = answer_added
    data['answer_existed'] = answer_existed     
    data['answers_not_added'] = answers_not_added
    print "nspd answers count :: " + str(len(records))
    print "added_answer_count :: " + str(added_answer_count)
    
    # need to maintain vote, contribution, rating, status
    action_category = ActionCategory.objects.filter(name__iexact='VoteRequirement')
    entity_name='Requirement'  
    cursor.execute("SELECT uID, oID, answerID, voteIsPositive, modified FROM nspd_votes")
    records = dictfetchall(cursor)          
    vote_added = 0
    vote_existed = 0  
    vote_helper = VoteHelper()
    data['nspd_votes'] = len(records)        
    for record in records:    
        if record['answerID'] in matching_answers:
            answer_id = matching_answers[record['answerID']]
            answer = AnswerReference.objects.get(id=answer_id)
            question = Question.objects.get(id=answer.question_id)
    
            if record['voteIsPositive'] == 1:
                vote_data = "Up"
            else:
                vote_data = "Down"
                
            user_id = matching_users[record['uID']]
            final_vote_data = 'Vote: ' + str(vote_data)
            votes = Action.objects.filter(entity_name__iexact=entity_name, entity_id__exact=answer_id, category__exact=action_category[0], data__iexact= final_vote_data)
            if votes:
                print "vote already migrated or existed.  Don't do anything."
                vote_existed = vote_existed + 1
            else:
                vote_helper.vote(answer_id, vote_data, user_id, entity_name, answer.jurisdiction_id) 
                vote_added = vote_added + 1 
        else:
            print "vote not migrated because of no matching answer found"  + str(record['answerID'])  
           
    data['vote_added'] = vote_added
    data['vote_existed'] = vote_existed   
    '''     

    return requestProcessor.render_to_response(request,'website/data_migration.html', data, '')  

    # no need to migrate comment because all are junk or test comment.
    



def update(user, record):
    user.username = record['uName']            
    user.password = ''        
    user.email = record['uEmail']
    user.is_active=record['uIsActive']
    user.last_login=datetime.datetime.fromtimestamp(record['uLastLogin']) #need to convert to right format
    user.date_joined=record['uDateAdded']          
    user.save()     
            
def patch_cf_questions_display_order():
    question_categories = QuestionCategory.objects.filter(accepted=1).order_by('display_order')
    data = {}
    data['non_cf_questions'] = {}
    data['cf_questions'] = {}
    for question_category in question_categories:
        questions = Question.objects.filter(category=question_category, accepted=1).exclude(form_type__exact='CF').order_by('-display_order')
        last_question = questions[0]    # assumption: non-cf questions are predefined and setup. always have questions and they all have display_order.  if not, bad setup.
        display_order = last_question.display_order
        data[question_category.id] = {}
        data['non_cf_questions'][question_category.id] = questions
        
        cf_questions = Question.objects.filter(category=question_category, accepted=1, form_type__exact='CF')

        for question in cf_questions:
            display_order = display_order + 1
            question.display_order = display_order
            question.save()

        cf_questions = Question.objects.filter(category=question_category, accepted=1, form_type__exact='CF')
        data['cf_questions'][question_category.id] = cf_questions
        
    data['question_categories'] = question_categories

    #return requestProcessor.render_to_response(request,'website/utils/patch_correct_questions_display_order.html', data, '')  
            
   
def correct_fee(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)    
    '''
            "default_value": "{\"fee_type_1\": \"fee type\", \"fee_item_1_1\": \"fee item\", 
            \"fee_formula_1_1\": \"flat_rate\", \"fee_other_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_1_1\": \"\", 
            \"fee_per_inverter_1_1\": \"0\", \"fee_flat_rate_1_1\": \"\", \"fee_per_major_components_1_1\": \"0\", \"fee_jurisdiction_cost_recovery_notes_1_1\": \"\", 
            \"fee_percentage_of_total_system_cost_1_1\": \"\", \"fee_percentage_of_total_system_cost_cap_amt_1_1\": \"\", \"fee_per_component_cap_1_1\": \"\", 
            \"fee_per_component_cap_cap_amt_1_1\": \"\", \"fee_per_module_1_1\": \"0\"}",    
            
             {"percentage_of_total_system_cost_cap": "", "fee_per_inverter": "", "flat_rate_amt": "", "fee_per_major_components": "", 
             "jurisdiction_cost_recovery_notes": "", "percentage_of_total_system_cost": "", "percentage_of_total_system_cost_cap_amt": "", 
             "value": "($100 plan review fee + permit costs). If strictly under\r\nelectrical permit:$50 inspection fee, 1.60 to 6.50 depending on kw of system,\r\nadditional fees if service needs to be rebuilt, new panels, safety switches + $100\r\nplan review fee. If building permit is required, based on valuation for review fees\r\nand building permit fee; electrical permit costs after approval of building permit.", 
             "fee_per_component_cap": "", "fee_per_component_cap_cap_amt": "", "fee_per_module": ""}                   

    '''
    question = Question.objects.get(id=16)
    #answers = AnswerReference.objects.filter(question=question).exclude(value__contains='fee_type')
    #answers = AnswerReference.objects.filter(question=question).exclude(value__contains='flat_rate_amt')    
    answers = AnswerReference.objects.filter(question=question)
    for answer in answers:
        '''
        old_value = json.loads(answer.value) 
        
        new_value = {}
        new_value['fee_type_1'] = 'fee_type'
        new_value['fee_item_1_1'] = 'fee_item'
        
        if 'percentage_of_total_system_cost_cap' in old_value:
            new_value['fee_percentage_of_total_system_cost_cap_1_1'] =  old_value['percentage_of_total_system_cost_cap']
        else:
            new_value['fee_percentage_of_total_system_cost_cap_1_1'] =  ''
            
        if 'fee_per_inverter' in old_value:
            new_value['fee_per_inverter_1_1'] =  old_value['fee_per_inverter']
        else:
            new_value['fee_per_inverter_1_1'] =  ''
            
        if 'flat_rate_amt' in old_value:
            new_value['fee_flat_rate_1_1'] =  old_value['flat_rate_amt']
        else:
            new_value['fee_flat_rate_1_1'] =  ''
          
        if 'fee_per_major_components' in old_value:
            new_value['fee_per_major_components_1_1'] =  old_value['fee_per_major_components']
        else:
            new_value['fee_per_major_components_1_1'] =  ''
            
        if 'jurisdiction_cost_recovery_notes' in old_value:
            new_value['fee_jurisdiction_cost_recovery_notes_1_1'] =  old_value['jurisdiction_cost_recovery_notes']
        else:
            new_value['fee_jurisdiction_cost_recovery_notes_1_1'] =  ''
            
        if 'percentage_of_total_system_cost' in old_value:
            new_value['fee_percentage_of_total_system_cost_1_1'] =  old_value['percentage_of_total_system_cost']
        else:
            new_value['fee_percentage_of_total_system_cost_1_1'] =  ''
         
        if 'percentage_of_total_system_cost_cap_amt' in old_value:
            new_value['fee_percentage_of_total_system_cost_cap_amt_1_1'] =  old_value['percentage_of_total_system_cost_cap_amt']
        else:
            new_value['fee_percentage_of_total_system_cost_cap_amt_1_1'] =  ''
           
        if 'fee_per_component_cap' in old_value:
            new_value['fee_per_component_cap_1_1'] =  old_value['fee_per_component_cap']
        else:
            new_value['fee_per_component_cap_1_1'] =  ''
            
            
        if 'fee_per_component_cap_cap_amt' in old_value:
            new_value['fee_per_component_cap_cap_amt_1_1'] =  old_value['fee_per_component_cap_cap_amt']
        else:
            new_value['fee_per_component_cap_cap_amt_1_1'] =  ''
         
        if 'fee_per_module' in old_value:
            new_value['fee_per_module_1_1'] =  old_value['fee_per_module']
        else:
            new_value['fee_per_module_1_1'] =  ''
           
        if 'value' in old_value:
            new_value['fee_other_1_1'] =  old_value['value']
        else:
            new_value['fee_other_1_1'] =  ''
            
            
                        
                                                                        
        
        if 'flat_rate_amt' in old_value and old_value['flat_rate_amt'] != '' and old_value['flat_rate_amt'] != None:
            formula = 'flat_rate'
        elif 'jurisdiction_cost_recovery_notes' in old_value and old_value['jurisdiction_cost_recovery_notes'] != '' and old_value['jurisdiction_cost_recovery_notes'] != None:
            formula = 'jurisdiction_cost_recovery'
        elif 'percentage_of_total_system_cost' in old_value and old_value['percentage_of_total_system_cost'] != '' and old_value['percentage_of_total_system_cost'] != None:
            formula = 'percentage_of_total_system_cost'
        elif 'value' in old_value and old_value['value'] != '' and old_value['value'] != None:
            formula = 'other'
        elif ('fee_per_inverter' in old_value and old_value['fee_per_inverter'] != '' and old_value['fee_per_inverter'] != None) or ('fee_per_module' in old_value and old_value['fee_per_module'] != '' and old_value['fee_per_module'] != None) or ('fee_per_major_components' in old_value and old_value['fee_per_major_components'] != '' and old_value['fee_per_major_components'] != None):
            formula = 'fee_per_component'   
        else:
            formula = 'flat_rate'            

        new_value['fee_formula_1_1'] =  formula
        
       
                    
        value = json.dumps(new_value)   # to convert to json
        '''
        
        fieldValidationCycleUtil = FieldValidationCycleUtil()
        value = fieldValidationCycleUtil.process_answer(question, answer.value)
                
        encoded_value = value.encode('utf-8') 
        answer.value = encoded_value
        
        answer.save()
        

        
    data['answers'] = answers

    return requestProcessor.render_to_response(request,'website/fee_correction.html', data, '')  

def prep_4_sprint_32():
    return
    question_id = 282   # forms
    question = Question.objects.get(id=question_id)
    answers = AnswerReference.objects.filter(question__exact=question)
    if len(answers) > 0:
        for answer in answers:
            if answer.value != '' and answer.value != None:
                try:
                    answer_details = json.loads(answer.value)
                    if 'link_1' in answer_details.keys():
                        if answer_details['link_1'] != '':
                            answer_details['form_option'] = 'link'
                            answer.value = json.dumps(answer_details)
                            answer.save()
                except:
                    pass
                    
    question_id = 96    # solar permitting checklist
    question = Question.objects.get(id=question_id)
    answers = AnswerReference.objects.filter(question__exact=question)
    if len(answers) > 0:
        for answer in answers:
            if answer.value != '' and answer.value != None:
                try:
                    answer_details = json.loads(answer.value)
                    if 'url' in answer_details.keys():
                        if answer_details['url'] != '':
                            answer_details['form_option'] = 'link'
                            answer_details['link_1'] = answer_details['url']
                            answer_details['url'] = ''
                            answer_details['available'] = 'yes'
                            answer.value = json.dumps(answer_details)
                            answer.save()     
                except:
                    pass  
                    
    question_id = 105 # Online inspection checklist
    question = Question.objects.get(id=question_id)
    answers = AnswerReference.objects.filter(question__exact=question)
    if len(answers) > 0:
        for answer in answers:
            if answer.value != '' and answer.value != None:
                try:
                    answer_details = json.loads(answer.value)
                    if 'value' in answer_details.keys():
                        if answer_details['value'] != '':
                            answer_details['form_option'] = 'link'
                            answer_details['link_1'] = answer_details['value']
                            answer_details['value'] = ''
                            answer_details['available'] = 'yes'
                            answer.value = json.dumps(answer_details)
                            answer.save()   
                except:
                    pass
                    
    question_id = 62 # Required spec sheets
    question = Question.objects.get(id=question_id)
    answers = AnswerReference.objects.filter(question__exact=question)
    if len(answers) > 0:
        for answer in answers:
            if answer.value != '' and answer.value != None:
                try:
                    answer_details = json.loads(answer.value)
                    if 'value' in answer_details.keys():
                        if answer_details['value'] != '':
                            answer_details['form_option'] = 'link'
                            answer_details['link_1'] = answer_details['value']
                            answer_details['value'] = ''
                            answer.value = json.dumps(answer_details)
                            answer.save()  
                except:
                    pass  
