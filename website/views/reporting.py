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
from django.db import connection
from collections import OrderedDict
import json

def build_query(question, field_map):
    # note: we're substituting directly into the query because the
    # mysql python driver adapter doesn't support real parameter
    # binding
    fields = []
    for name, match in field_map.items():
        fields.append("CONVERT(%(match)s, UNSIGNED) AS '%(name)s'" % { "name": name, "match": match })
    return '''SELECT %(fields)s
              FROM website_jurisdiction LEFT OUTER JOIN website_answerreference
              ON website_jurisdiction.id = website_answerreference.jurisdiction_id
              WHERE (question_id = %(question_id)s OR question_id IS NULL) AND
                    website_jurisdiction.id NOT IN (1, 101105) AND
                    website_jurisdiction.jurisdiction_type != 'u' AND
                    (approval_status = 'A' OR approval_status IS NULL);''' % { "question_id": question.id,
                                                                               "fields": ", ".join(fields) }

def json_match(field_name, value):
    return 'value LIKE \'%%%%"%(name)s"%%%%"%(value)s"%%%%\' COLLATE utf8_general_ci' % { "name": field_name,
                                                                                          "value": value }

def regexp_match(regexp):
    return 'value REGEXP \'%(regexp)s\'' % { "regexp": regexp }

def null_match():
    return 'value IS NULL'

def not_null_match():
    return 'value IS NOT NULL'

def sum_match(match):
    return 'SUM(%s)' % match

def count_match(match):
    return 'COUNT(%s)' % match

def count_all():
    return 'COUNT(*)'

def total():
    return not_null_match()

def or_match(*args):
    return " OR ".join(args)

def not_match(match):
    return 'NOT (%s)' % match

def coverage_report():
    return OrderedDict([("Answered", sum_match(not_null_match())),
                        ("Unanswered", sum_match(null_match())),
                        ("Total", count_all())])

def yes_no_field(field_name):
    return OrderedDict([("Yes", sum_match(json_match(field_name, "yes"))),
                        ("No", sum_match(json_match(field_name, "no"))),
                        ("Other", sum_match(not_match(or_match(json_match(field_name, "yes"),
                                                               json_match(field_name, "no"))))),
                        ("Total", sum_match(total()))])

def yes_no_exception_field(field_name):
    return OrderedDict([("Yes", json_match(field_name, "yes")),
                        ("Yes, with exceptions", json_match(field_name, "yes, with exceptions")),
                        ("No", json_match(field_name, "no")),
                        ("Total", total())])

reports_by_type = {
    "available_url_display.html": yes_no_field("available"),
    "radio_with_exception_display.html": yes_no_exception_field("required"),
    "plan_check_service_type_display.html": OrderedDict([("Over the Counter", json_match("plan_check_service_type", "over the counter")),
                                                         ("In-House (not same day)", json_match("plan_check_service_type", "in-house")),
                                                         ("Outsourced", json_match("plan_check_service_type", "outsourced")),
                                                         ("Total", total())]),
    "radio_compliant_sb1222_with_exception.html": yes_no_exception_field("compliant"),
    "inspection_checklists_display.html": yes_no_field("value"),
    "radio_has_training_display.html": yes_no_field("value"),
    "phone_display.html": coverage_report(),
    "url.html": coverage_report(),
    "address_display.html": coverage_report(),
    "radio_submit_PE_stamped_structural_letter_with_exception_display.html": yes_no_exception_field("required"),
    "hours_display.html": coverage_report(),
    "turn_around_time_display.html": coverage_report(), # check spec, can do more here
    "available_url_display.html": coverage_report(),
    "permit_cost_display.html": coverage_report(), # check the spec, probably needs histograms and stuff
    "radio_required_for_page_sizes_display.html": yes_no_field("required"), # should do more for the required values
    "radio_required_for_scales_display.html": yes_no_field("required"), # likewise
    "radio_required_display.html": yes_no_field("required"),
    "radio_covered_with_exception_display.html": yes_no_exception_field("required"),
    "radio_studer_vent_rules_with_exception_display.html": yes_no_exception_field("allowed"),
    "radio_module_drawings_display.html": OrderedDict([("Yes", json_match("value", "must draw individual modules")),
                                                       ("No", json_match("value", "n in series in a rectangle allowed")),
                                                       ("Total", total())]),
    "radio_allowed_with_exception_display.html": yes_no_exception_field("allowed"),
    "required_spec_sheets_display.html": coverage_report(),
    "homeowner_requirements_display.html": coverage_report(), # two yes/no answers in one
    "fire_setbacks_display.html": yes_no_exception_field("enforced"),
    "radio_inspection_approval_copies_display.html": OrderedDict([("In person", json_match("apply", "in person")),
                                                                  ("Remotely", json_match("apply", "remotely")),
                                                                  ("Total", total())]),
    "signed_inspection_approval_delivery_display.html": coverage_report(),
    "radio_vent_spanning_rules_with_exception_display.html": yes_no_exception_field("allowed"),
    "solar_permitting_checklists_display.html": coverage_report(),
    "radio_available_with_exception_display.html": yes_no_exception_field("available"),
    "time_window_display.html": OrderedDict([("Exact time given", json_match("time_window", "0")),
                                             ("2 hours (or less)", json_match("time_window", "2")),
                                             ("Half Day (2 to 4 hours)", json_match("time_window", "4")),
                                             ("Full Day (greater than 4 hours)", json_match("time_window", "8")),
                                             ("Total", total())]),
    "radio_has_training_display.html": yes_no_field("value"),
    "radio_licensing_required_display.html": yes_no_field("required"),
    "online_forms.html": coverage_report(),
    None: coverage_report()
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

    questions = Question.objects.filter(accepted='1').exclude(form_type="CF").order_by("category", "display_order")

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
    print(query)
    cursor = connection.cursor()
    cursor.execute(query)
    #print cursor.fetchall()
    result = dict(zip([col[0] for col in cursor.description], cursor.fetchone()))

    data['table'] = []
    for key in report.keys():
        data['table'].append({'key': key, 'value': result[key]})
    data['table_json'] = json.dumps(data['table'])

    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reporting/report_on.html', data, '')
