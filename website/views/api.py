from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor
from django.conf import settings as django_settings
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
import hashlib
import xml.sax.saxutils as saxutils



### now for imports that will actually be used
import MySQLdb ### move this to settings?


class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

def searchState(request):
    conn = MySQLdb.connect (host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    
    error = None
    
    #state = request.args.get('state')
    #parent_id = request.args.get('parent_id')
    #jurisdiction_id = request.args.get('jurisdiction_id')
    state = request.GET.get('state',False)
    parent_id = request.GET.get('parent_id',False)
    jurisdiction_id = request.GET.get('jurisdiction_id',False)
    jurisdiction_type = request.GET.get('jurisdiction_type',False)
    if state:
        if jurisdiction_type:
            query = "select id,name,jurisdiction_type,parent_id,state,latitude,longitude from website_jurisdiction where `state` = '" + conn.escape_string(str(state)) + "' AND `jurisdiction_type` = '" + conn.escape_string(str(jurisdiction_type)) + "'"
        else:
            query = "select id,name,jurisdiction_type,parent_id,state,latitude,longitude from website_jurisdiction where `state` = '" + conn.escape_string(str(state)) + "'"
        cursor.execute (query)
        
        output = "<result>\n"        
        
        # we need to account for empty result sets.
        if cursor.fetchone():
            row = cursor.fetchall()
            for value in row:
                output += "\t<jurisdiction>\n"
                for key, value2 in value.items():
                    output += "\t\t<" + saxutils.escape(saxutils.unescape(str(key))) + ">" + saxutils.escape(saxutils.unescape(str(value2))) + "</" + saxutils.escape(saxutils.unescape(str(key))) + ">\n" 
                output += "\t</jurisdiction>\n"
        else:
            output += "\t<error>Jurisdictions Matching Your Criteria Were Not Found</error>"
        
        output += "</result>"

    elif parent_id:
        cursor.execute ("SELECT * FROM website_jurisdiction where `parent_id` = " + conn.escape_string(str(parent_id)))
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
            output = "<result>\n"
            output += "\t<error>No Jurisdictions Matching Your Criteria Were Found</error>"
            output += "</result>"

    elif jurisdiction_id:
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
        queryJurisdiction = "SELECT * FROM website_jurisdiction where `id` = '" + conn.escape_string(str(jurisdiction_id)) + "'"
        cursor.execute (queryJurisdiction)
        
        jurisdictionInfo = cursor.fetchone()
        if jurisdictionInfo != None:
                    
            ##cursor.execute ("SELECT * FROM website_answerreference where `jurisdiction_id` = '" + conn.escape_string(str(jurisdiction_id)) + "'")
            #queryAnswers = "SELECT website_answerreference.id AS id, website_answerreference.question_id AS question_id, website_answerreference.value AS value, website_answerreference.file_upload AS file_upload, website_answerreference.create_datetime AS create_datetime, website_answerreference.modify_datetime AS modify_datetime, website_answerreference.jurisdiction_id AS jurisdiction_id, website_answerreference.is_current AS is_current, website_answerreference.rating AS rating, website_answerreference.is_callout AS is_callout, website_answerreference.rating_status AS rating_status, website_answerreference.approval_status AS approval_status, website_answerreference.creator_id AS creator_id, website_answerreference.migrated_answer_id AS migrated_answer_id, website_answerreference.status_datetime AS status_datetime, website_answerreference.organization_id AS organization_id FROM website_answerreference, website_question WHERE (website_question.id = website_answerreference.question_id) AND jurisdiction_id = '" + conn.escape_string(str(jurisdiction_id)) + "' AND website_question.form_type != 'CF'"
            queryAnswers = "SELECT * FROM (SELECT website_answerreference.id AS id, website_answerreference.question_id AS question_id, website_answerreference.value AS value, website_answerreference.file_upload AS file_upload, website_answerreference.create_datetime AS create_datetime, website_answerreference.modify_datetime AS modify_datetime, website_answerreference.jurisdiction_id AS jurisdiction_id, website_answerreference.is_current AS is_current, website_answerreference.rating AS rating, website_answerreference.is_callout AS is_callout, website_answerreference.rating_status AS rating_status, website_answerreference.approval_status AS approval_status, website_answerreference.creator_id AS creator_id, website_answerreference.migrated_answer_id AS migrated_answer_id, website_answerreference.status_datetime AS status_datetime, website_answerreference.organization_id AS organization_id FROM website_answerreference, website_question WHERE (website_question.id = website_answerreference.question_id) AND jurisdiction_id = '" + conn.escape_string(str(jurisdiction_id)) + "' AND approval_status = 'A' AND website_question.form_type != 'CF' ORDER BY question_id ASC, modify_datetime DESC) as tempTable GROUP BY question_id ASC"
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


            
            
#            data = {}
#            data['xml'] = jurisdictionInfo
#            cursor.close()
#            conn.close()
#            requestProcessor = HttpRequestProcessor(request)
#            return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')
            
            
            
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
                        #print "done with try"
    
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
            output = "<result>\n"
            output += "\t<error>No Jurisdictions Matching Your Criteria Were Found</error>"
            output += "</result>"
          
    else:
        cursor.execute ("SELECT DISTINCT(state) FROM website_zipcode")
        row = cursor.fetchall()
        output = "<result>\n"
        output += "\t<states>\n"
        for value in row:    
            for key, value2 in value.items():
                output += "\t\t<" + saxutils.escape(saxutils.unescape(str(key))) + ">" + saxutils.escape(saxutils.unescape(str(value2))) + "</" + saxutils.escape(saxutils.unescape(str(key))) + ">\n"
        output += "\t</states>\n" 
        output += "</result>"
     
    data = {}
    data['xml'] = output
    
    cursor.close()
    conn.close()

    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/api.xml', data, 'application/xml')

