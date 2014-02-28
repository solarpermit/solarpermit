# -*- coding: utf-8 -*-
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
import re

def build_query(question, field_map):
    # note: we're substituting directly into the query because the
    # mysql python driver adapter doesn't support real parameter
    # binding
    fields = []
    for name, match in field_map.items():
        fields.append("CONVERT(%(match)s, UNSIGNED) AS '%(name)s'" % { "name": name, "match": match })
    return '''SELECT %(fields)s
              FROM (SELECT (SELECT value
                            FROM website_answerreference
                            WHERE id = (SELECT MAX(id)
                                        FROM website_answerreference
                                        WHERE website_answerreference.jurisdiction_id = website_jurisdiction.id AND
                                        approval_status = 'A' AND
                                        question_id = %(question_id)s)) AS value
                    FROM website_jurisdiction
                    WHERE website_jurisdiction.id NOT IN (1, 101105) AND
                          website_jurisdiction.jurisdiction_type != 'u') AS temp
           ''' % { "question_id": question.id,
                   "fields": ", ".join(fields) }

def json_match(field_name, value, op="="):
    return 'json_get(value, "%s") %s "%s"' % (field_name, op, value)
    return regexp_match('"%(name)s": *"%(value)s"' % { "name": escape_regex_inclusion(field_name),
                                                       "value": escape_regex_inclusion(value) })
def json_extract(field_name):
    return 'json_get(value, "%s")' % field_name

def regexp_match(regexp):
    return 'value REGEXP \'%(regexp)s\' COLLATE utf8_general_ci' % { "regexp": regexp }
def escape_regex_inclusion(s):
    return re.sub(r'([\[\].*?{}()|$^])',
                  r'[[.\1.]]',
                  s)

def null_match(field='value'):
    return '%s IS NULL' % field
def not_null_match(field='value'):
    return '%s IS NOT NULL' % field

def sum_match(match):
    return 'SUM(%s)' % match
def count_match(match):
    return 'COUNT(%s)' % match
def count_all():
    return 'COUNT(*)'

def total():
    return not_null_match()

def and_match(*args):
    return " AND ".join(args)
def or_match(*args):
    return " OR ".join(args)
def not_match(match):
    return 'NOT (%s)' % match

def lt(a, b):
    return "%s < %s" % (a, b)
def gt(a, b):
    return "%s > %s" % (a, b)
def lte(a, b):
    return "%s <= %s" % (a, b)
def gte(a, b):
    return "%s >= %s" % (a, b)

def between(v, a, b):
    if a > b:
        (a, b) = (b, a)
    return "%s BETWEEN %s AND %s" % (v, a, b)

def parenthesize(match):
    return "("+ match +")"

def chart(type, spec):
    return {"type": type, "spec": spec}
def pie(spec):
    return chart("pie", spec)
def hist(spec):
    return chart("histogram", spec)

def add_other(spec):
    copy = OrderedDict(spec)
    conditions = [v for (k,v) in copy.iteritems()]
    copy["Other"] = not_match(or_match(*conditions))
    return copy
def summarize(spec):
    copy = OrderedDict(spec)
    for (k,v) in copy.iteritems():
        copy[k] = sum_match(v)
    return copy
def add_sum_total(spec):
    copy = OrderedDict(spec)
    copy["Total"] = sum_match(total())
    return copy
def add_count_total(spec):
    copy = OrderedDict(spec)
    copy["Total"] = count_all()
    return copy

def coverage_report():
    return pie(OrderedDict([("Answered", sum_match(not_null_match())),
                            ("Unanswered", sum_match(null_match())),
                            ("Total", count_all())]))

def yes_no_field(field_name):
    return pie(OrderedDict([("Yes", sum_match(json_match(field_name, "yes"))),
                            ("No", sum_match(json_match(field_name, "no"))),
                            ("Other", sum_match(not_match(or_match(json_match(field_name, "yes"),
                                                                   json_match(field_name, "no"))))),
                            ("Total", sum_match(total()))]))

def yes_no_exception_field(field_name):
    return pie(OrderedDict([("Yes", sum_match(json_match(field_name, "yes"))),
                            ("Yes, with exceptions", sum_match(json_match(field_name, "yes, with exceptions"))),
                            ("No", sum_match(json_match(field_name, "no"))),
                            ("Other", sum_match(not_match(or_match(json_match(field_name, "yes"),
                                                                   json_match(field_name, "yes, with exceptions"),
                                                                   json_match(field_name, "no"))))),
                            ("Total", sum_match(total()))]))

# macros, man, macros.
# also, shouldn't this go by multiples of 5? presumably it's business days…
def turn_around_report():
    not_freeform = parenthesize(or_match(null_match(json_extract("free-form")),
                                         json_match("free-form", "")))
    bins = OrderedDict([("Same day", and_match(not_freeform,
                                               json_match("time_unit", "hour(s)"))),
                        ("1-2 days", and_match(not_freeform,
                                               json_match("time_unit", "day(s)"),
                                               lte(json_extract("time_qty"), 2))),
                        ("3-7 days", and_match(not_freeform,
                                               or_match(and_match(json_match("time_unit", "day(s)"),
                                                                  between(json_extract("time_qty"), 3, 7)),
                                                        and_match(json_match("time_unit", "week(s)"),
                                                                  json_match("time_qty", "1"))))),
                        ("8-14 days", and_match(not_freeform,
                                                or_match(and_match(json_match("time_unit", "day(s)"),
                                                                   between(json_extract("time_qty"), 8, 14)),
                                                         and_match(json_match("time_unit", "week(s)"),
                                                                   json_match("time_qty", "2"))))),
                        ("15-21 days", and_match(not_freeform,
                                                 or_match(and_match(json_match("time_unit", "day(s)"),
                                                                    between(json_extract("time_qty"), 15, 21)),
                                                          and_match(json_match("time_unit", "week(s)"),
                                                                    json_match("time_qty", "3"))))),
                        ("22+ days", and_match(not_freeform,
                                               or_match(and_match(json_match("time_unit", "day(s)"),
                                                                  gte(json_extract("time_qty"), 22)),
                                                        and_match(json_match("time_unit", "week(s)"),
                                                                  gte(json_extract("time_qty"), 4))))),
                        ("Freeform", json_match("free-form", "", op="!="))])
    return hist(add_sum_total(summarize(add_other(bins))))


reports_by_type = {
    "available_url_display.html": [coverage_report(), yes_no_field("available")],
    "radio_with_exception_display.html": [coverage_report(), yes_no_exception_field("required")],
    "plan_check_service_type_display.html": [coverage_report(),
                                             pie(OrderedDict([("Over the Counter",
                                                               sum_match(json_match("plan_check_service_type",
                                                                                    "over the counter"))),
                                                              ("In-House (not same day)",
                                                               sum_match(json_match("plan_check_service_type",
                                                                                    "in-house"))),
                                                              ("Outsourced",
                                                               sum_match(json_match("plan_check_service_type",
                                                                                    "outsourced"))),
                                                              ("Other",
                                                               sum_match(not_match(or_match(json_match("plan_check_service_type",
                                                                                                       "over the counter"),
                                                                                            json_match("plan_check_service_type",
                                                                                                       "in-house"),
                                                                                            json_match("plan_check_service_type",
                                                                                                       "outsourced"))))),
                                                              ("Total", sum_match(total()))]))],
    "radio_compliant_sb1222_with_exception.html": [coverage_report(),
                                                   yes_no_exception_field("compliant")],
    "inspection_checklists_display.html": [coverage_report(),
                                           yes_no_field("value")],
    "radio_has_training_display.html": [coverage_report(),
                                        yes_no_field("value")],
    "phone_display.html": [coverage_report()],
    "url.html": [coverage_report()],
    "address_display.html": [coverage_report()],
    "radio_submit_PE_stamped_structural_letter_with_exception_display.html": [coverage_report(),
                                                                              yes_no_exception_field("required")],
    "hours_display.html": [coverage_report()], # histogram
    "turn_around_time_display.html": [coverage_report(), # histogram, time_unit/time_qty
                                      turn_around_report()],
    "available_url_display.html": [coverage_report()],
    "permit_cost_display.html": [coverage_report()], # check the spec, probably needs histograms and stuff
    "radio_required_for_page_sizes_display.html": [coverage_report(),
                                                   yes_no_field("required")], # should do more for the required values
    "radio_required_for_scales_display.html": [coverage_report(),
                                               yes_no_field("required")], # likewise
    "radio_required_display.html": [coverage_report(),
                                    yes_no_field("required")],
    "radio_covered_with_exception_display.html": [coverage_report(),
                                                  yes_no_exception_field("required")],
    "radio_studer_vent_rules_with_exception_display.html": [coverage_report(),
                                                            yes_no_exception_field("allowed")],
    "radio_module_drawings_display.html": [coverage_report(),
                                           pie(OrderedDict([("Yes",
                                                             sum_match(json_match("value",
                                                                                  "must draw individual modules"))),
                                                            ("No",
                                                             sum_match(json_match("value",
                                                                                  "n in series in a rectangle allowed"))),
                                                            ("Total", sum_match(total()))]))],
    "radio_allowed_with_exception_display.html": [coverage_report(),
                                                  yes_no_exception_field("allowed")],
    "required_spec_sheets_display.html": [coverage_report()],
    "homeowner_requirements_display.html": [coverage_report()], # two yes/no answers in one
    "fire_setbacks_display.html": [coverage_report(),
                                   yes_no_exception_field("enforced")],
    "radio_inspection_approval_copies_display.html": [coverage_report(),
                                                      pie(OrderedDict([("In person", sum_match(json_match("apply",
                                                                                                          "in person"))),
                                                                       ("Remotely", sum_match(json_match("apply",
                                                                                                         "remotely"))),
                                                                       ("Total", sum_match(total()))]))],
    "signed_inspection_approval_delivery_display.html": [coverage_report()],
    "radio_vent_spanning_rules_with_exception_display.html": [coverage_report(), yes_no_exception_field("allowed")],
    "solar_permitting_checklists_display.html": [coverage_report()],
    "radio_available_with_exception_display.html": [coverage_report(), yes_no_exception_field("available")],
    "time_window_display.html": [coverage_report(), # histogram
                                 hist(OrderedDict([("Exact time given", sum_match(json_match("time_window",
                                                                                             "0"))),
                                                   ("2 hours (or less)", sum_match(json_match("time_window",
                                                                                              "2"))),
                                                   ("Half Day (2 to 4 hours)", sum_match(json_match("time_window",
                                                                                                    "4"))),
                                                   ("Full Day (greater than 4 hours)", sum_match(json_match("time_window",
                                                                                                            "8"))),
                                                   ("Other", sum_match(not_match(or_match(json_match("time_window", "0"),
                                                                                          json_match("time_window", "2"),
                                                                                          json_match("time_window", "4"),
                                                                                          json_match("time_window", "8"))))),
                                                   ("Total", sum_match(total()))]))],
    "radio_has_training_display.html": [coverage_report(), yes_no_field("value")],
    "radio_licensing_required_display.html": [coverage_report(), yes_no_field("required")],
    "online_forms.html": [coverage_report()],
    None: [coverage_report()]
}

reports_by_qid = {
#    15: { #
#        'query': '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%value"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%value"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
#        'keys_in_order': ['Yes', 'No', 'Total'],
#    },
    15: [coverage_report(), yes_no_field("value")]
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
    reports = (question.id in reports_by_qid and reports_by_qid[question_id]) or \
              (question.display_template in reports_by_type and reports_by_type[question.display_template])

    data['reports'] = []
    idx = 0
    for report in reports:
      query = build_query(question, report['spec'])
      cursor = connection.cursor()
      cursor.execute(query)
      table = [{'key': k, 'value': v } for (k,v) in zip([col[0] for col in cursor.description], cursor.fetchone())]
      data['reports'].append({ "idx": idx,
                               "table": table,
                               "type": report['type'] })
      idx += 1
    data['reports_json'] = json.dumps(data['reports'])

    requestProcessor = HttpRequestProcessor(request)
    return requestProcessor.render_to_response(request,'website/reporting/report_on.html', data, '')
