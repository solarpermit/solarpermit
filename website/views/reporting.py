#
# code is function but needs enhancement to conform to DRY methodology
#

# django components
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor
from django.conf import settings as django_settings
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
import hashlib
from website.models import Question, QuestionCategory

# specific to api
import MySQLdb # database
import MySQLdb.cursors

def build_query(question, field_map):
    # note: we're substituting directly into the query because the
    # mysql python driver adapter doesn't support real parameter
    # binding
    i = 0
    counts = []
    for name, match in field_map.items():
        if match:
            counts.append("(SELECT count(*) FROM (SELECT value FROM website_answerreference WHERE question_id = '%(qid)s' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp%(i)s WHERE value LIKE '%(match)s') as `%(name)s`" % {"qid": question.id, "name": name, "match": match, "i": i})
        else:
            counts.append("(SELECT count(*) FROM (SELECT value FROM website_answerreference WHERE question_id = '%(qid)s' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp%(i)s) as `%(name)s`" % {"qid": question.id, "name": name, "match": match, "i": i})
        i += 1

    return "SELECT %s from website_answerreference LIMIT 1" % ", ".join(counts)

def json_match(field_name, value):
    return '%%%(name)s"%%"%(value)s' % { "name": field_name, "value": value }

def yes_no_field(field_name):
    return { "Yes": json_match(field_name, "yes"),
             "No": json_match(field_name, "no"),
             "Total": None }

def yes_no_except_field(field_name):
    return { "Yes": json_match(field_name, "yes"),
             "Yes, with exceptions": json_match(field_name, "yes, with exceptions"),
             "No": json_match(field_name, "no"),
             "Total": None }

def yes_no_url_field(field_name):
    42

reports_by_type = {
    "available_url_display.html": yes_no_field("available"),
    "radio_with_exception_display.html": yes_no_except_field("required"),
    "plan_check_service_type_display.html": { "Over the Counter": json_match("plan_check_service_type", "over the counter"),
                                              "In-House (not same day)": json_match("plan_check_service_type", "in-house"),
                                              "Outsourced": json_match("plan_check_service_type", "outsourced"),
                                              "Total": None },
    "radio_compliant_sb1222_with_exception.html": yes_no_except_field("compliant"),
    "inspection_checklists_display.html": yes_no_url_field("value"),
    "radio_has_training_display.html": yes_no_field("value"),
}

reports_by_qid = {
#    15: { #
#        'query': '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%value"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%value"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
#        'keys_in_order': ['Yes', 'No', 'Total'],
#    },
    15: yes_no_field("value")
}

##############################################################################
#
# Display Index of Reports
#
##############################################################################
def report_index(request):
    # get question data
    data = {}
    data['current_nav'] = 'reporting'

    questions = Question.objects.filter(accepted='1').exclude(form_type="CF")

    reports_index = []
    category_last_encountered = ''
    first_run = True
    for question in questions:
        if question.category.name != category_last_encountered:
            category_last_encountered = question.category.name
            # the category level does not exist create it.
            reports_index.append({ "category": question.category.name.replace('_', ' ').title(),
                                   "reports_in_category": [] })
        # append this report's data to the list - with a link if it exists
        reports_index[-1]['reports_in_category'].append(question)

    data['reports_index'] = reports_index
    data['report_types'] = reports_by_type.keys()
    data['report_qids'] = reports_by_qid.keys()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reporting/report_index.html', data, '')

##############################################################################
#
# Display an individual report on a question_id
#
##############################################################################
def report_on(request, question_id):
    # Check request for validity
    question_id = int(question_id)
    question = Question.objects.get(id=question_id)
    if not question or not (question.id in reports_by_qid or question.display_template in reports_by_type):
        raise Http404

    data = {}
    data['current_nav'] = 'reporting'
    data['report_name'] = question.question
    data['question_instruction'] = question.instruction
    report = (question.id in reports_by_qid and reports_by_qid[question_id]) or (question.display_template in reports_by_type and reports_by_type[question.display_template])
    query = build_query(question, report)

    conn = MySQLdb.connect(host=settings.DATABASES['default']['HOST'],
                           user=settings.DATABASES['default']['USER'],
                           passwd=settings.DATABASES['default']['PASSWORD'],
                           db=settings.DATABASES['default']['NAME'],
                           cursorclass=MySQLdb.cursors.DictCursor)
    cursor = conn.cursor()
    cursor.execute(query)
    row = cursor.fetchone()

    data['table'] = []
    for key in report.keys():
        data['table'].append({'key': key,'value': row[key]})

    #finish up
    if 'conn' in locals() and conn.open:
        cursor.close()
        conn.close()
    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reporting/report_on.html', data, '')
