#
# code is functional but needs enhancement to conform to DRY methodology
#

# django components
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import Context
from django.utils.safestring import mark_safe
from django.conf import settings as django_settings
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
import hashlib
from collections import OrderedDict

# specific to api
from django.views.decorators.csrf import csrf_exempt
import xml.sax.saxutils as saxutils # xml encding
import MySQLdb # database
import MySQLdb.cursors
from xml.dom import minidom
import re
import json

# use this in the future instead of template rendering
import lxml.etree
import lxml.builder
import lxml.objectify

from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.httpUtil import HttpRequestProcessor
from website.models import API_Keys, Question, AnswerReference, Comment, Jurisdiction
from django.contrib.auth.models import User

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def is_numeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
## sections

## global variables for convenience
first_jurisdiction = 1
last_jurisdiction = 146879 #147121


##############################################################################
#
# Get a list of states in the system
#
##############################################################################
@csrf_exempt
def list_states(request):
    data = {}

    conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    
    cursor.execute ("SELECT DISTINCT(state) FROM website_jurisdiction ORDER BY state ASC")
    rows = cursor.fetchall()

    output = "<result>\n"
    output += "\t<states>\n"
    for value in rows:    
        for key, value2 in value.items():
            output += "\t\t<" + saxutils.escape(saxutils.unescape(str(key))) + ">" + saxutils.escape(saxutils.unescape(str(value2))) + "</" + saxutils.escape(saxutils.unescape(str(key))) + ">\n"
    output += "\t</states>\n" 
    output += "</result>"
    
    
    #finish up
    data['xml'] = mark_safe(output)
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')
    
    
    
    
##############################################################################
#
# Get a list of jurisdictions - filtered
#
##############################################################################
@csrf_exempt
def list_jurisdictions(request):
    data = {}
    errors = []
    
    # convert POST to a string for parsing xml
    post_string = request.raw_post_data
        
    # strip extra whitespace
    while post_string != re.sub("\s<", "<", post_string):
        post_string = re.sub("\s<", "<", post_string)
    while post_string != re.sub("\s>", ">", post_string):
        post_string = re.sub("\s>", ">", post_string)
    while post_string != re.sub(">\s", ">", post_string):
        post_string = re.sub(">\s", ">", post_string)
    while post_string != re.sub("<\s", "<", post_string):
        post_string = re.sub("<\s", "<", post_string)

    try:
        xmlDoc = minidom.parseString(post_string)
    except Exception:
        errors.append("Could not Parse XML")
        
    del post_string
        
    if len(errors) > 0:
        output = '<errors>\n'
        for this_error in errors:
            output += "\t<error>" + this_error + "</error>\n"
        output += '</errors>'
    else:
    
    
        # define filters
        filters = dict()
        filter_names = [
                        'state',
                        'type',
                        'children_of',
                        'updated_after',
                        'contains_questions_any',
                        'contains_questions_all',
                        ]
        jurisdiction_types = [
                              'CC',
                              'CI',
                              'CO',
                              'IC',
                              'SC',
                              'SCFO',
                              'U',
                              ]
        
    
        
        try:
            temp = xmlDoc.getElementsByTagName('request')[0]
        except Exception:
            errors.append("Could not find 'request' node - please see documentation at https://github.com/solarpermit/solarpermit/wiki")
        else:
            temp = None
            for node in xmlDoc.getElementsByTagName('request')[0].getElementsByTagName('filters')[0].childNodes:
                if node.nodeType == 1: #element type
                    if node.localName in filter_names:
                        filters[node.localName] = node.firstChild.data.strip()
                    else:
                        errors.append(node.localName + ' is an unknown filter.')
    
        #error testing
        if int(len(filters)) == 0:
            errors.append('At lease one filter must be declared.')
        if 'state' in filters and len(filters['state']) != 2:
            errors.append('Filter state must be defined as a two letter USPS abbreviation.')
        if 'type' in filters and filters['type'].upper() not in jurisdiction_types:
            errors.append('type "' + filters['type'].upper() + '" is not a valid jurisdiction type.')
        if 'children_of' in filters and (not is_numeric(filters['children_of']) or int(filters['children_of']) < 1):
            errors.append('Filter children_of must be an integer greater than zero (' + str(filters['children_of']) + ').')
        if 'updated_after' in filters:
            if re.search('^\d\d\d\d[/-]\d\d[/-]\d\d[ ]\d\d[:]\d\d[:]\d\d$', filters['updated_after']) == None:
                errors.append('updated_after date is not properly formatted. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
            else:
                # this section can be improved no-doubt
                date_parts = dict()
                date_parts['year'] = int(filters['updated_after'][:4])
                date_parts['month'] = int(filters['updated_after'][5:7])
                date_parts['day'] = int(filters['updated_after'][8:10])
                date_parts['hour'] = int(filters['updated_after'][11:13])
                date_parts['minute'] = int(filters['updated_after'][14:16])
                date_parts['second'] = int(filters['updated_after'][17:19])
                if date_parts['month'] > 12 or date_parts['month'] < 1:
                    errors.append('Month (' + str(date_parts['month']) + ') in filter updated_after is invalid. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
                if (date_parts['day'] > 31) or (date_parts['day'] > 29 and date_parts['month'] == 2) or (date_parts['day'] > 30 and date_parts['month'] not in [1,3,5,7,8,10,12]):
                    errors.append('Day (' + str(date_parts['day']) + ') in filter updated_after is invalid. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
                if date_parts['hour'] > 23:
                    errors.append('Hour (' + str(date_parts['hour']) + ') in fitler updated_after is invalid. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
                if date_parts['minute'] > 59:
                    errors.append('Minute (' + str(date_parts['minute']) + ') in fitler updated_after is invalid. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
                if date_parts['second'] > 59:
                    errors.append('Second (' + str(date_parts['second']) + ') in fitler updated_after is invalid. Please use a naive UTC datetime string formatted as YYYY-MM-DD HH:MM:SS.')
                del date_parts
        if 'contains_questions_any' in filters and re.search('^[0-9]+(,[0-9]+)*$',filters['contains_questions_any']) == None:
            errors.append('Filter contains_questions_any must be integers seperated by commas (' + str(filters['contains_questions_any']) + ').')
        if 'contains_questions_all' in filters and re.search('^[0-9]+(,[0-9]+)*$',filters['contains_questions_all']) == None:
            errors.append('Filter contains_questions_all must be integers seperated by commas (' + str(filters['contains_questions_any']) + ').')
            
        
        # get the jurisdictions
        if len(errors) < 1:
            
            #only connect to DB after we know it's necessary
            
            # db connection needed for escaping strings
            conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                                user=settings.DATABASES['default']['USER'],
                                passwd=settings.DATABASES['default']['PASSWORD'],
                                db=settings.DATABASES['default']['NAME'],
                                cursorclass=MySQLdb.cursors.DictCursor)
            cursor = conn.cursor()
            
            
            query = "SELECT id, name, jurisdiction_type, parent_id, state, latitude, longitude, last_contributed from website_jurisdiction WHERE 1 "
            if 'state' in filters:
                query += "AND state LIKE '" + conn.escape_string(str(filters['state'])) + "' "
            if 'type' in filters:
                query += "AND jurisdiction_type LIKE '" + conn.escape_string(str(filters['type'])) + "' "
            if 'children_of' in filters:
                query += "And parent_id = '" + conn.escape_string(str(filters['children_of'])) + "' "
            if 'updated_after' in filters:
                query += "And last_contributed > TIMESTAMP('" + conn.escape_string(str(filters['updated_after'])) + "') "
            if 'contains_questions_any' in filters:
                any_questions = filters['contains_questions_any'].split(',')
                query += "AND id IN (SELECT DISTINCT jurisdiction_id FROM website_answerreference WHERE 1=0 "
                for i in any_questions:
                    query += "OR question_id = '" + conn.escape_string(str(i)) + "' "
                query += ") "
                del any_questions
            if 'contains_questions_all' in filters:
                all_questions = filters['contains_questions_all'].split(',')
                query += "AND id IN (SELECT DISTINCT jurisdiction_id FROM website_answerreference WHERE 1 "
                for i in all_questions:
                    query += "AND question_id = '" + conn.escape_string(str(i)) + "' "
                query += ") "
                del all_questions
            
            query += "ORDER BY id ASC"
            
    
        # output errors, or proceed to rendering results
        if len(errors) > 0:
            output = '<errors>\n'
            for this_error in errors:
                output += '\t<error>' + this_error + '</error>\n'
            output += '</errors>'
        else:
            # no errors, create results
            
            cursor.execute (query)
            
            if cursor.fetchone():
                row = cursor.fetchall()
                output = "<result>\n"
                for value in row:
                    output += "\t<jurisdiction>\n"
                    for key, value2 in value.items():
                        output += "\t\t<" + saxutils.escape(saxutils.unescape(str(key))) + ">" + saxutils.escape(saxutils.unescape(str(value2))) + "</" + saxutils.escape(saxutils.unescape(str(key))) + ">\n"
                    output += "\t</jurisdiction>\n"
                output += "</result>"
            else:
                output = "<errors><error>No Jurisdictions Matching Your Criteria Were Found</error></errors>"

        

    
    
    
    #finish up
    if len(errors) > 0:
        output = '<errors>\n'
        for this_error in errors:
            output += "\t<error>" + this_error + "</error>\n"
        output += '</errors>'
    data['xml'] = mark_safe(output)
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')



##############################################################################
#
# Get a specific jurisdiction with filters
#
##############################################################################
@csrf_exempt
def get_jurisdiction(request):
    data = {}
    errors = []
    
    # convert POST to a string for parsing xml
    post_string = request.raw_post_data
            
    # strip extra whitespace
    while post_string != re.sub("\s<", "<", post_string):
        post_string = re.sub("\s<", "<", post_string)
    while post_string != re.sub("\s>", ">", post_string):
        post_string = re.sub("\s>", ">", post_string)
    while post_string != re.sub(">\s", ">", post_string):
        post_string = re.sub(">\s", ">", post_string)
    while post_string != re.sub("<\s", "<", post_string):
        post_string = re.sub("<\s", "<", post_string)

    try:
        xmlDoc = minidom.parseString(post_string)
    except Exception:
        errors.append("Could not Parse XML")
    
    del post_string
        
    if len(errors) > 0:
        output = '<errors>\n'
        for this_error in errors:
            output += "\t<error>" + this_error + "</error>\n"
        output += '</errors>'
    else:

        # define filters
        filters = dict()
        filter_names = [
                        'id',
                        'limit_to_questions',
                        'first',
                        'last',
                        'next',
                        'previous',
                        ]
    
        try:
            temp = xmlDoc.getElementsByTagName('request')[0]
        except Exception:
            errors.append("Could not find 'request' node - please see documentation at https://github.com/solarpermit/solarpermit/wiki")
        else:
            temp = None
            for node in xmlDoc.getElementsByTagName('request')[0].getElementsByTagName('filters')[0].childNodes:
                if node.nodeType == 1: #element type
                    if node.localName in filter_names:
                        filters[node.localName] = node.firstChild.data.strip()
                    else:
                        errors.append(node.localName + ' is an unknown filter.')
        
        # error testng
        if int(len(filters)) == 0:
            errors.append('At lease one filter must be declared.')
        if 'id' in filters and (not is_numeric(filters['id']) or int(filters['id']) < 1):
            errors.append('Declared id must be a positive integer greater than zero.')
        if 'limit_to_questions' in filters  and re.search('^[0-9]+(,[0-9]+)*$',filters['limit_to_questions']) == None:
            errors.append('Filter limit_to_questions must be integers seperated by commas (' + str(filters['limit_to_questions']) + ').')
        
        
        
        if len(errors) > 0:
            output = '<errors>\n'
            for this_error in errors:
                output += '\t<error>' + this_error + '</error>\n'
            output += '</errors>'
        else:
            
            
            conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                                   user=settings.DATABASES['default']['USER'],
                                   passwd=settings.DATABASES['default']['PASSWORD'],
                                   db=settings.DATABASES['default']['NAME'],
                                   cursorclass=MySQLdb.cursors.DictCursor)
            cursor = conn.cursor()
        
            if 'first' in filters:
                # get the first jurisdiction (ignore sample)
                jurisdiction_id = first_jurisdiction
            elif 'last' in filters:
                # get the last jurisdiction
                jurisdiction_id = last_jurisdiction
            elif 'id' in filters:
                jurisdiction_id = filters['id']
                if 'next' in filters:
                    # get the one after the one designated
                    if jurisdiction_id == last_jurisdiction:
                        jurisdiction_id = filters['id']
                    else:
                        query = "SELECT id FROM website_jurisdiction WHERE id > '" + conn.escape_string(str(filters['id'])) + "' ORDER BY id ASC LIMIT 1"
                elif 'previous' in filters:
                    #get the one before the one designated
                    if jurisdiction_id == first_jurisdiction + 1:
                        jurisdiction_id = filters['id']
                    else:
                        query = "SELECT id FROM website_jurisdiction WHERE id < '" + conn.escape_string(str(filters['id'])) + "' ORDER BY id DESC LIMIT 1"
                if 'query' in locals():
                    #overwrite the jurisdiction_id
                    cursor.execute(query)
                    for row in cursor.fetchall():
                        jurisdiction_id = row['id']
                    del query
    
            
        
                
            
            
            
            strippedDescriptionJurisdiction = {}
            strippedDescriptionQuestions = {}
            strippedDescriptionAnswers = {}
            strippedDescriptionComments = {}
            strippedDescriptionVotes = {}
            buildDescriptionJurisdiction = {}
            buildDescriptionAnswers = {}
            buildDescriptionQuestions = {}
            buildDescriptionComments = {}
            buildDescriptionVotes = {}
            buildAnswerID = []
            buildQuestionID = []
            buildRelationID = {}
            buildJurisdictionAnswers = {}
            jurisdictionQuestions = AutoVivification() 
            oldkey = []
            newkey = []
            queryJurisdiction = "SELECT * FROM website_jurisdiction WHERE id = '" + conn.escape_string(str(jurisdiction_id)) + "' LIMIT 1"
            
            cursor.execute(queryJurisdiction)
            jurisdictionInfo = cursor.fetchone()
            if jurisdictionInfo != None:
                            
                ##cursor.execute ("SELECT * FROM website_answerreference where `jurisdiction_id` = '" + conn.escape_string(str(jurisdiction_id)) + "'")
                #queryAnswers = "SELECT website_answerreference.id AS id, website_answerreference.question_id AS question_id, website_answerreference.value AS value, website_answerreference.file_upload AS file_upload, website_answerreference.create_datetime AS create_datetime, website_answerreference.modify_datetime AS modify_datetime, website_answerreference.jurisdiction_id AS jurisdiction_id, website_answerreference.is_current AS is_current, website_answerreference.rating AS rating, website_answerreference.is_callout AS is_callout, website_answerreference.rating_status AS rating_status, website_answerreference.approval_status AS approval_status, website_answerreference.creator_id AS creator_id, website_answerreference.migrated_answer_id AS migrated_answer_id, website_answerreference.status_datetime AS status_datetime, website_answerreference.organization_id AS organization_id FROM website_answerreference, website_question WHERE (website_question.id = website_answerreference.question_id) AND jurisdiction_id = '" + conn.escape_string(str(jurisdiction_id)) + "' AND website_question.form_type != 'CF'"
                if 'limit_to_questions' in filters:
                    questions = filters['limit_to_questions'].split(',')
                    queryAnswers = "SELECT * FROM (SELECT website_answerreference.id AS id, website_answerreference.question_id AS question_id, website_answerreference.value AS value, website_answerreference.file_upload AS file_upload, website_answerreference.create_datetime AS create_datetime, website_answerreference.modify_datetime AS modify_datetime, website_answerreference.jurisdiction_id AS jurisdiction_id, website_answerreference.is_current AS is_current, website_answerreference.rating AS rating, website_answerreference.is_callout AS is_callout, website_answerreference.rating_status AS rating_status, website_answerreference.approval_status AS approval_status, website_answerreference.creator_id AS creator_id, website_answerreference.migrated_answer_id AS migrated_answer_id, website_answerreference.status_datetime AS status_datetime, website_answerreference.organization_id AS organization_id FROM website_answerreference, website_question WHERE (website_question.id = website_answerreference.question_id) AND jurisdiction_id = '" + conn.escape_string(str(jurisdiction_id)) + "' AND approval_status = 'A' AND website_question.form_type != 'CF' ORDER BY question_id ASC, modify_datetime DESC) as tempTable  WHERE 1=0 "
                    for i in questions:
                        queryAnswers += "OR question_id = '" + conn.escape_string(str(i)) + "' "
                    queryAnswers += "GROUP BY question_id ASC"
                    del questions
                else:
                    queryAnswers = "SELECT * FROM (SELECT website_answerreference.id AS id, website_answerreference.question_id AS question_id, website_answerreference.value AS value, website_answerreference.file_upload AS file_upload, website_answerreference.create_datetime AS create_datetime, website_answerreference.modify_datetime AS modify_datetime, website_answerreference.jurisdiction_id AS jurisdiction_id, website_answerreference.is_current AS is_current, website_answerreference.rating AS rating, website_answerreference.is_callout AS is_callout, website_answerreference.rating_status AS rating_status, website_answerreference.approval_status AS approval_status, website_answerreference.creator_id AS creator_id, website_answerreference.migrated_answer_id AS migrated_answer_id, website_answerreference.status_datetime AS status_datetime, website_answerreference.organization_id AS organization_id FROM website_answerreference, website_question WHERE (website_question.id = website_answerreference.question_id) AND jurisdiction_id = '" + conn.escape_string(str(jurisdiction_id)) + "' AND approval_status = 'A' AND website_question.form_type != 'CF' ORDER BY question_id ASC, modify_datetime DESC) as tempTable GROUP BY question_id ASC"
                
                #
                
                cursor.execute (queryAnswers)
                    
                jurisdictionAnswers = cursor.fetchall()        
                #find the table describers
                cursor.execute ("DESCRIBE website_jurisdiction")
                descriptionJurisdiction = cursor.fetchall()
                cursor.execute ("DESCRIBE website_answerreference")
                descriptionAnswers = cursor.fetchall()
                cursor.execute ("DESCRIBE website_comment")
                descriptionComments = cursor.fetchall()
                cursor.execute ("DESCRIBE website_question")
                descriptionQuestions = cursor.fetchall()        
                output = "<result>\n"
                output += "\t<jurisdiction>\n"
                c = 0
                i = len(descriptionJurisdiction)
                while c < i:
                    strippedDescriptionJurisdiction[descriptionJurisdiction[c]["Field"]] = descriptionJurisdiction[c]["Type"]
                    c = c + 1
                c = 0
                i = len(strippedDescriptionJurisdiction)
        
                for key, value in strippedDescriptionJurisdiction.items():
                    buildDescriptionJurisdiction[key] = "\t\t<" + str(key) + " type='" + str(value) + "'>"
                    c = c + 1
                for key in jurisdictionInfo.keys():
                    output += str(buildDescriptionJurisdiction[key]) + saxutils.escape(saxutils.unescape(str(jurisdictionInfo[key]))) + "</" + saxutils.escape(saxutils.unescape(key)) + ">\n"
                if jurisdictionAnswers:
                    for value in jurisdictionAnswers:
                        buildQuestionID.append(value.get('question_id'))        
                        buildRelationID[value.get('id')] = value.get('question_id')
                else:        
                    pass
                #build question query
                queryQuestions = "SELECT * FROM website_question WHERE "
                count = 0        
                for value in buildQuestionID:
                    if count < 1:
                        queryQuestions += "`id` = '" + conn.escape_string(str(value)) + "'"
                        count = 1
                    else:
                        queryQuestions += " OR `id` = '" + conn.escape_string(str(value)) + "'"        
                if buildQuestionID:
                    cursor.execute (queryQuestions)
                    jurisdictionQuestions = cursor.fetchall()
                else:
                    pass
                #build comment query
                queryComments = "SELECT * FROM website_comment WHERE "
                count = 0
                for value in buildRelationID:
                    if count < 1:
                        queryComments += "`entity_id` = '" + conn.escape_string(str(value)) + "'"
                        count = 1
                    else:
                        queryComments += " OR `entity_id` = '" + conn.escape_string(str(value)) + "'"
                if buildRelationID:
                    cursor.execute (queryComments)
                    jurisdictionComments = cursor.fetchall()
                else:
            
                    pass
                if buildQuestionID:
                    #print queryComments
                    c = 0
                    i = len(descriptionQuestions)
                    while c < i: 
                        strippedDescriptionQuestions[descriptionQuestions[c]["Field"]] = descriptionQuestions[c]["Type"]
                        c = c + 1
                    c = 0
                    i = len(descriptionAnswers)
                    while c < i:
                        strippedDescriptionAnswers[descriptionAnswers[c]["Field"]] = descriptionAnswers[c]["Type"]
                        c = c + 1
            
                    c = 0
                    i = len(descriptionComments)
                    while c < i: 
                        strippedDescriptionComments[descriptionComments[c]["Field"]] = descriptionComments[c]["Type"]
                        c = c + 1
        
                    c = 0
                    i = len(strippedDescriptionAnswers)
                    for key, value in strippedDescriptionAnswers.items():
                        buildDescriptionAnswers[key] = "\t\t\t\t<" + str(key) + " type='" + str(value) + "'>"
                        c = c + 1
                    c = 0
                    i = len(strippedDescriptionQuestions)
                    for key, value in strippedDescriptionQuestions.items():
                        buildDescriptionQuestions[key] = "\t\t\t<" + str(key) + " type='" + str(value) + "'>"
                        c = c + 1
            
                    c = 0
                    i = len(strippedDescriptionComments)
                    for key, value in strippedDescriptionComments.items():
                        buildDescriptionComments[key] = "\t\t\t\t\t<" + str(key) + " type='" + str(value) + "'>"
                        c = c + 1
                    buildCount = len(buildRelationID)
                    buildInc = 0
            
                    while buildCount > buildInc:
                        output += "\t\t<question>\n"
                        try:
                            #print "in the try"
                            if jurisdictionQuestions:
                                for key, value in jurisdictionQuestions[buildInc].items():
                                    raw = str(jurisdictionQuestions[buildInc][key])
                                    phased = raw.replace("&", "&amp;")
                                    output += str(buildDescriptionQuestions[key]) + saxutils.escape(saxutils.unescape(phased)) + "</" + saxutils.escape(saxutils.unescape(key)) + ">\n"
                            output += "\t\t\t<answer>\n"
                            if jurisdictionAnswers:
                                for key, value in jurisdictionAnswers[buildInc].items():
                                    if key == "id":
                                        entity_id = value
                                    raw = str(jurisdictionAnswers[buildInc][key])
                                    phased = raw.replace("&", "&amp;")
                                    output += str(buildDescriptionAnswers[key]) + saxutils.escape(saxutils.unescape(phased)) + "</" + saxutils.escape(saxutils.unescape(key)) + ">\n"
            
                            commentInc = 0
                            commentCount = len(jurisdictionComments)
                            #print commentCount
                            #print "second nasty loop"
                            while commentInc < commentCount: 
                                try:
                                    #print "in the try"
                                    if jurisdictionComments[commentInc]["entity_id"] == entity_id:
                                        output += "\t\t\t\t<comments>\n"
                                        for key, value in jurisdictionComments[commentInc].items():
                                            raw = str(jurisdictionComments[commentInc][key])
                                            phased = raw.replace("&", "&amp;")
                                            output += str(buildDescriptionComments[key]) + saxutils.escape(saxutils.unescape(phased)) + "</" + saxutils.escape(saxutils.unescape(key)) + ">\n"
                                        output += "\t\t\t\t</comments>\n"
                                    #print "finished the try"
                                except IndexError:
                                    pass
                                commentInc = commentInc + 1
                            output += "\t\t\t</answer>\n"
                        except IndexError:
                            print "passed on " + str(buildInc)
                            pass
                        output += "\t\t</question>\n"
                        buildInc = buildInc + 1
                else:
                    #print "nothing here"
                    pass
                    
                output += "\t</jurisdiction>\n"
                output += "</result>"
                output = output.replace("\t\t</question>\n\t\t<question>\n\t</jurisdiction>\n</result>", "\t\t</question>\n\t</jurisdiction>\n</result>")
                
            else:
                #jurisdiction does not exist
                output = "<errors>\n\t<error>No Jurisdictions Matching Your Criteria Were Found -- id = " + str(jurisdictionInfo) + "</error>\n</errors>"

    
    
    #finish up
    data['xml'] = mark_safe(output)
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')
    
    



    
##############################################################################
#
# Get a question details - excludes custom questions
#
##############################################################################
@csrf_exempt
def get_question(request):
    a=0

@csrf_exempt
def get_question_list(request):
    questions = Question.objects.filter(accepted=True).exclude(form_type='CF').select_related('category')
    E = lxml.builder.ElementMaker()
    result = E.result()
    for question in questions:
        result.append(E.question(E.id(str(question.id)),
                                 E.field_label(question.label if question.label else ""),
                                 E.instructions(question.instruction if question.instruction else ""),
                                 E.default_format(question.default_value if question.default_value else""),
                                 E.has_multivalues("1" if question.has_multivalues else "0"),
                                 E.terminology(question.terminology if question.terminology else ""),
                                 E.category(question.category.name if question.category.name else "")))
    return HttpResponse(xml_tostring(result),
                        content_type='application/xml')
        
@csrf_exempt
def submit_suggestion(request):
    validation_util_obj = FieldValidationCycleUtil()
    from website.models.questionAnswer import Question
    from website.models import Jurisdiction
    data = {}
    errors = []

    # convert POST to a string for parsing xml
    post_string = request.raw_post_data
            
    # strip extra whitespace
    while post_string != re.sub("\s<", "<", post_string):
        post_string = re.sub("\s<", "<", post_string)
    while post_string != re.sub("\s>", ">", post_string):
        post_string = re.sub("\s>", ">", post_string)
    while post_string != re.sub(">\s", ">", post_string):
        post_string = re.sub(">\s", ">", post_string)
    while post_string != re.sub("<\s", "<", post_string):
        post_string = re.sub("<\s", "<", post_string)

    try:
        xmlDoc = minidom.parseString(post_string)
    except Exception:
        errors.append("Could not Parse XML")
    
    del post_string
        
    if len(errors) > 0:
        output = '<errors>\n'
        for this_error in errors:
            output += "\t<error>" + this_error + "</error>\n"
        output += '</errors>'
    else:

        # define directives
        directives = dict()
        directive_names = [
                        'api_username',
                        'api_key',
                        'question_id',
                        'jurisdiction_id',
                        'answer_value',
                        ]
        try:
            temp = xmlDoc.getElementsByTagName('request')[0]
        except Exception:
            errors.append("Could not find 'request' node - please see documentation at https://github.com/solarpermit/solarpermit/wiki")    
        else:
            temp = None
            for node in xmlDoc.getElementsByTagName('request')[0].childNodes:
                if node.nodeType == 1: #element type
                    if node.localName in directive_names and node.firstChild is not None:
                        directives[node.localName] = node.firstChild.data.strip()
                    else:
                        if node.firstChild is None:
                            errors.append(node.localName + ' is empty.  Please declare a value for ' + node.localName + '.')
                        else:
                            errors.append(' is an unknown directive')
        
        
        
        # error testing
        if int(len(directives)) != 5:
            errors.append('Incorrect number of Directive values - either something is empty, or something is missing (' + str(len(directives)) + ' != 5).')
        if 'api_username' not in directives:
            errors.append('Your api_username must be provided in the request.')
        if 'api_key' not in directives:
            errors.append('Your api_key must be provided in the request.')
        if 'question_id' not in directives:
            errors.append('You must declare a question_id.')
        if 'question_id' in directives and (not is_numeric(directives['question_id']) or int(directives['question_id']) < 1):
            errors.append('QuestinID must be a positive integer greater than zero.')
        if 'jurisdiction_id' not in directives:
            errors.append('You must declare a jurisdiction_id')
        if 'jurisdiction_id' in directives and (not is_numeric(directives['jurisdiction_id']) or int(directives['jurisdiction_id']) < 1):
            errors.append('jurisdiction_id must be a positive integer greater than zero.')
        if 'answer_value' not in directives:
            errors.append('You can not suggest an answer without the data for that answer declared as an answer_value.')

        # user validation pre-work
        try:
            # get the user id of this user
            thisUser = User.objects.get(username=directives['api_username'])
        except Exception:
            errors.append('Failed to look up your username.')
        
        if len(errors) > 0:
            output = '<errors>\n'
            for this_error in errors:
                output += '\t<error>' + this_error + '</error>\n'
            output += '</errors>'
        else:
            # get the api key for this user
            apiKeys = API_Keys.objects.filter(user_id=thisUser, key=directives['api_key'], enabled=True)
            # validate user
            if not len(apiKeys):
                output = '<errors>\n\t<error>User validation failure - check api_key for accuracy</error>\n</errors>'
            else:
                ## validate jurisdiction_id
                try:
                    jurisdiction = Jurisdiction.objects.get(id=directives['jurisdiction_id'])
                except Exception:
                    errors.append('The jurisdiction_id you have declared does not exist, or is invalid.')
                if len(errors) > 0:
                    output = '<errors>\n'
                    for this_error in errors:
                        output += '\t<error>' + this_error + '</error>\n'
                    output += '</errors>'
                else:
                    ### validate question_id
                    try:
                        question = Question.objects.get(id=directives['question_id'])
                    except Exception:
                        errors.append('The question_id you have declared does not exist, or is invalid.')
                    if len(errors) > 0:
                        output = '<errors>\n'
                        for this_error in errors:
                            output += '\t<error>' + this_error + '</error>\n'
                        output += '</errors>'
                    else:
                        #### validate answer format can be parsed as json
                        if question.default_value is None or len(question.default_value) < 1:
                            default_format = json.loads('{"value":""}')
                        else:
                            default_format = json.loads(question.default_value)
                        try:
                            this_format = json.loads(directives['answer_value'])
                        except Exception:
                            errors.append('Cannot parse answer_value as JSON')
                        if len(errors) > 0:
                            output = '<errors>\n'
                            for this_error in errors:
                                output += '\t<error>' + this_error + '</error>\n'
                            output += '</errors>'
                        else:
                            output = ''
                            #### validate answer format has matching keys
                            if not ((all (key in this_format for key in default_format)) and (all (key in default_format for key in this_format))) :
                                if int(directives['question_id']) != 16:
                                    errors.append('answer_value (JSON) does not match format of default_value for this question.')
                                else:
                                    # for pricing formula
                                    # check to make sure each key is a direct, or regex match to an incremented key name.
                                    suspect_keys = []
                                    valid_keys = [
                                                  'percentage_of_total_system_cost_cap_amt',
                                                  'percentage_of_total_system_cost',
                                                  'flat_rate_amt',
                                                  ]
                                    for key in this_format:
                                        # strip trailing underscores and digits
                                        new_item = re.sub('[_]\d*[_]\d*$','',key)
                                        if new_item not in suspect_keys:
                                            suspect_keys.append(new_item)
                                    for key in default_format:
                                        # strip trailing underscores and digits
                                        new_item = re.sub('[_]\d*[_]\d*$','',key)
                                        if new_item not in valid_keys:
                                            valid_keys.append(new_item)
                                    if not ((all (item in suspect_keys for item in valid_keys)) and (all (item in valid_keys for item in suspect_keys))) :
                                        error_string = 'answer_value (JSON) has unrecognized keys for this question.'
                                        error_string += ' ... invalid keys (does not include incremented portion key names): '
                                        for item in suspect_keys:
                                            if item not in valid_keys:
                                                error_string += ' ' + item + ', '
                                        error_string += ' ... missingkeys (does not include incremented portion of key names): '
                                        for item in valid_keys:
                                            if item not in suspect_keys:
                                                error_string += item + ', '
                                        
                                        errors.append(error_string)
                                            
                            if len(errors) > 0:
                                output = '<errors>\n'
                                for this_error in errors:
                                    output += '\t<error>' + this_error + '</error>\n'
                                output += '</errors>'
                            else:
                                is_callout = 0
                                try:
                                    arcf = validation_util_obj.save_answer(question, directives['answer_value'], jurisdiction, 'AddRequirement', thisUser, is_callout)
                                    output = '<Result>' + str(arcf) + '</Result>'
                                except Exception as inst:
                                    output = '<errors>\n\t<error>Failed to save answer suggestion.</error><detail>\n'
                                    output += str(type(inst))     # the exception instance
                                    output += str(inst.args)
                                    output += '</detail></errors>'
                                
                                '''
                                question_id = 93
                                question = Question.objects.get(id=question_id)
                                
                                answer = '{"value":"Written Via API x?"}'
                            
                                jurisdiction_id = 1
                                jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)
                                
                                user_id = 3
                                user = User.objects.get(id=user_id)
                                
                                is_callout = 0
                                
                                answer_id = None
                                
                                #arcf = validation_util_obj.save_answer(question, answer, jurisdiction, 'AddRequirement', user, is_callout, answer_id)
                                arcf = 'foo'
                                
                                output = '<testing>\n\n'
                                
                                output += str(arcf)
                                
                                output += '\n\n</testing>'
                                '''
    
    #finish up
    data['xml'] = mark_safe(output)
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')

@csrf_exempt
def vote_on_suggestion(request):
    try:
        request_data = parse_api_request(request.body)
        user = get_user(request_data, 'api_username')
        api_key = get_api_key(request_data, 'api_key', user)
        validation_util_obj = FieldValidationCycleUtil()
        feedback = validation_util_obj.process_vote(user,
                                                    get_vote(request_data, 'vote'),
                                                    'requirement',
                                                    get_answer(request_data, 'answer_id').pk,
                                                    'confirmed')
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response("Unknown error.")
    return success_response()

@csrf_exempt
def comment_on_suggestion(request):
    try:
        request_data = parse_api_request(request.body)
        user = get_user(request_data, 'api_username')
        api_key = get_api_key(request_data, 'api_key', user)
        answer = get_answer(request_data, 'answer_id')
        c = Comment(jurisdiction=answer.jurisdiction,
                    entity_name='AnswerReference',
                    entity_id=answer.pk,
                    user=user,
                    comment_type='RC',
                    comment=get_comment(request_data, 'comment'),
                    approval_status='P')
        c.save()
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response("Unknown error.")
    return success_response()

@csrf_exempt
def comment_on_unincorporated(request):
    try:
        request_data = parse_api_request(request.body)
        user = get_user(request_data, 'api_username')
        api_key = get_api_key(request_data, 'api_key', user)
        jurisdiction = get_unincorporated(request_data, 'jurisdiction_id')
        c = Comment(jurisdiction=jurisdiction,
                    user=user,
                    comment_type='JC',
                    comment=get_comment(request_data, 'comment'),
                    approval_status='P')
        c.save()
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response("Unknown error.")
    return success_response()

# What I really want here is a dataflow graph, so that I can collect
# as many errors as possible at once while still having readable
# code. See the previous revision for some code that wasn't very
# readable but collected errors.

def checked_getter(func):
    def getter(obj, prop, *args):
        out = None
        if not hasattr(obj, prop):
            raise ValidationError("No %s specified" % prop)
        try:
            out = func(getattr(obj, prop), *args)
            if out is None:
                raise ValidationError("Invalid %s." % prop)
        except Exception as e:
            raise ValidationError("Invalid %s." % prop)
        return out
    return getter

def optional_getter(func):
    def getter(obj, prop, *args):
        if hasattr(obj, prop):
            return func(getattr(obj, prop), *args)
        return None
    return getter

@checked_getter
def get_prop(val):
    return val

@checked_getter
def get_user(username):
    return User.objects.get(username=username)

@checked_getter
def get_api_key(api_key, user):
    keys = user.api_keys_set.filter(key=api_key, enabled=True)
    return keys[0] if len(keys) else None

@checked_getter
def get_answer(answer_id):
    return AnswerReference.objects.get(pk=int(answer_id))

@checked_getter
def get_incorporated(jurisdiction_id):
    j = Jurisdiction.objects.get(pk=int(jurisdiction_id))
    return j if j.jurisdiction_type not in ['U', 'CINP', 'CONP'] else None

@checked_getter
def get_unincorporated(jurisdiction_id):
    j = Jurisdiction.objects.get(pk=int(jurisdiction_id))
    return j if j.jurisdiction_type == 'U' else None

@checked_getter
def get_vote(vote):
    return str(vote) if str(vote) in ["up", "down"] else None

@checked_getter
def get_comment(comment):
    return str(comment) if comment else None

def xml_tostring(xml):
    return lxml.etree.tostring(xml,
                               encoding="UTF-8",
                               xml_declaration=True,
                               pretty_print=True)

def parse_api_request(xml_str):
    try:
        return lxml.objectify.fromstring(xml_str)
    except:
        raise ValidationError("Invalid request.")

def error_response(errors=[]):
    if isinstance(errors, ValidationError):
        errors = errors.args[0]
    if not isinstance(errors, list):
        errors = [errors]
    E = lxml.builder.ElementMaker()
    return HttpResponse(xml_tostring(E.result(E.status("fail"),
                                              E.errors(*[E.error(e) for e in errors]))))

def success_response(messages=[]):
    E = lxml.builder.ElementMaker()
    return HttpResponse(xml_tostring(E.result(E.status("success"))),
                        content_type="application/xml")

class ValidationError(Exception):
    pass
