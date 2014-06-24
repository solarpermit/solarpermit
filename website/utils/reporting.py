from django.db import connection
from collections import OrderedDict
import json
import re
from django.db.models import Q
from django.db.models.sql import Query
from django.db import DEFAULT_DB_ALIAS
from website.models import Jurisdiction

def run_reports(question, **kwargs):
    return [run_report(question, report, **kwargs) for report in get_reports(question)]

def run_report(question, report, **kwargs):
    output = report.copy()
    output['question_id'] = question.id
    query = build_query(question, report['spec'], **kwargs)
    cursor = connection.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    output['table'] = [{'key': k, 'value': v} for (k,v) in zip(columns, cursor.fetchone())]
    return output

def get_reports(question):
    return (question.id in reports_by_qid and reports_by_qid[question.id]) or \
           (question.display_template in reports_by_type and reports_by_type[question.display_template])

def add_temporal_reports(reports):
    temporal = [make_temporal(r) for r in reports if 'name' in r]
    return reports + temporal

def make_temporal(report):
    return { 'type': "temporal",
             'name': report['name'] if 'name' in report else None,
             'question_id': report['question_id'],
             'statsd_metrics': [row['key'] for row in report['table']]
           }

def build_query(question, field_map, geo_filter=None, before=None):
    # Yes we have two mechanisms for building queries here. We've
    # hacked out a slice of the django sql "compiler" for one of them,
    # since they specialize in where clauses, while writing a simpler
    # one of our own that specializes in select clauses. Both of them
    # bear more than a passing resemblance to lisp, of course.
    indent = "                      ";
    sep = ",\n"+indent
    # convert everything to unsigned, even though they are already
    # unsigned. This prevents django from occasionally thinking that
    # the values are Decimals
    fields = ["CONVERT(%(match)s, UNSIGNED) AS '%(name)s'" % { "name": n, "match": m }
              for (n, m) in field_map.items()]
    compiled_filter = None
    if geo_filter:
        fake_query = Query(Jurisdiction)
        fake_query.add_q(geo_filter)
        compiler = fake_query.get_compiler(DEFAULT_DB_ALIAS)
        where, where_params = fake_query.where.as_sql(compiler.connection.ops.quote_name, #might break postgres
                                                      compiler.connection)
        compiled_filter = where % tuple(["'%s'" % p for p in where_params])
    return ('''
               SELECT %(fields)s
               FROM (SELECT id AS answer_id,
                            (SELECT value FROM website_answerreference WHERE id = answer_id) AS value
                     FROM (SELECT (SELECT MAX(id)
                                   FROM website_answerreference
                                   WHERE website_answerreference.jurisdiction_id = website_jurisdiction.id AND
                                         approval_status = 'A' AND''' +
            ("\n                                         modify_datetime <= '%(before)s' AND" if before else "") + '''
                                         question_id = %(question_id)s) AS id
                           FROM website_jurisdiction
                           WHERE website_jurisdiction.id NOT IN (1, 101105) AND
                                 website_jurisdiction.jurisdiction_type != 'u' ''' +
            ("AND\n                                 %(geo_filter)s" if geo_filter else "") +
            ("AND\n                                 create_datetime <= '%(before)s'" if before else "") +
            ''') AS temp0) as temp1
            ''') % { "question_id": question.id,
                     "fields": sep.join(fields),
                     "geo_filter": compiled_filter,
                     "before": before.strftime("%Y-%m-%d %H:%M:%S") if before else None }

def json_match(field_name, value, op="="):
    # BUG: this should be utf8mb4_unicode_ci; our connection to the database must be using the wrong encoding
    return and_match(not_null_match(json_extract(field_name)),
                     'json_get(value, "%s") %s "%s" COLLATE utf8_unicode_ci' % (field_name, op, value))
def json_extract(field_name):
    return 'json_get(value, "%s")' % field_name
def json_valid():
    return 'json_valid(value)'

def regexp_match(regexp):
    return 'value REGEXP \'%(regexp)s\'' % { "regexp": regexp }
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
    return not_null_match("answer_id")

def and_match(*args):
    return parenthesize(" AND ".join(args))
def or_match(*args):
    return parenthesize(" OR ".join(args))
def not_match(match):
    return parenthesize('NOT (%s)' % match)

def eq(a, b):
    return "%s = %s" % (a, b)
def ne(a, b):
    return "%s != %s" % (a, b)
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
    return and_match(gt(v, a),
                     lte(v, b))

def parenthesize(match):
    return "("+ match +")"

def chart(type, spec):
    return {"type": type, "spec": spec}
def pie(spec):
    return chart("pie", spec)
def hist(spec):
    return chart("histogram", spec)
def named(name, spec):
    spec['name'] = name
    return spec

def add_freeform(spec):
    not_freeform = or_match(null_match(json_extract("free-form")),
                            json_match("free-form", ""))
    copy = [(k, and_match(not_freeform, v)) for (k,v) in spec.iteritems()]
    copy.append(("Freeform", and_match(not_null_match(json_extract("free-form")),
                                       json_match("free-form", "", op="!="))))
    return OrderedDict(copy)
def add_other(spec):
    copy = OrderedDict(spec)
    conditions = [v for (k,v) in copy.iteritems()]
    copy["Other"] = and_match(not_null_match("answer_id"),
                              or_match(null_match("value"),
                                       and_match(not_null_match("value"),
                                                 not_match(json_valid())),
                                       not_match(or_match(*conditions))))
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
    spec = OrderedDict([("Answered", not_null_match("answer_id")),
                        ("Unanswered", null_match("answer_id"))])
    return named("coverage", pie(add_count_total(summarize(spec))))

def yes_no_field(field_name):
    spec = OrderedDict([("Yes", json_match(field_name, "yes")),
                        ("No", json_match(field_name, "no"))])
    return pie(add_sum_total(summarize(add_other(spec))))

def yes_no_exception_field(field_name):
    spec = OrderedDict([("Yes", json_match(field_name, "yes")),
                        ("Yes, with exceptions", json_match(field_name, "yes, with exceptions")),
                        ("No", json_match(field_name, "no"))])
    return pie(add_sum_total(summarize(add_other(spec))))

# macros, man, macros.
def turn_around_report():
    is_hours = json_match("time_unit", "hour(s)");
    is_days = json_match("time_unit", "day(s)");
    is_weeks = json_match("time_unit", "week(s)");
    qty = json_extract("time_qty")
    bins = OrderedDict([("Same day", and_match(is_hours, lte(qty, 8))),
                        ("1-2 days", or_match(and_match(is_hours, between(qty, 9, 48)),
                                              and_match(is_days, lte(qty, 2)))),
                        ("3-5 days", or_match(and_match(is_days, between(qty, 3, 5)),
                                              and_match(is_weeks, eq(qty, 1)))),
                        ("6-10 days", or_match(and_match(is_days, between(qty, 6, 10)),
                                               and_match(is_weeks, eq(qty, 2)))),
                        ("11-15 days", or_match(and_match(is_days, between(qty, 11, 15)),
                                                and_match(is_weeks, eq(qty, 3)))),
                        ("16-20 days", or_match(and_match(is_days, between(qty, 16, 20)),
                                                and_match(is_weeks, eq(qty, 4)))),
                        ("21+ days", or_match(and_match(is_days, gte(qty, 21)),
                                              and_match(is_weeks, gte(qty, 5))))])
    return hist(add_sum_total(summarize(add_other(add_freeform(bins)))))

def plan_check_service_type_report():
    spec = OrderedDict([("Over the Counter",
                         json_match("plan_check_service_type",
                                    "over the counter")),
                        ("In-House (not same day)",
                         json_match("plan_check_service_type",
                                    "in-house")),
                        ("Outsourced",
                         json_match("plan_check_service_type",
                                    "outsourced"))])
    return pie(add_sum_total(summarize(add_other(spec))))

def module_drawings_report():
    spec = OrderedDict([("Yes", json_match("value", "must draw individual modules")),
                        ("No", json_match("value", "n in series in a rectangle allowed"))])
    return pie(add_sum_total(summarize(add_other(spec))))

def inspection_approval_report():
    spec = OrderedDict([("In person", json_match("apply", "in person")),
                        ("Remotely", json_match("apply", "remotely"))])
    return pie(add_sum_total(summarize(add_other(spec))))

def time_window_report():
    spec = OrderedDict([("Exact time given", json_match("time_window", "0")),
                        ("2 hours (or less)", json_match("time_window", "2")),
                        ("Half Day (2 to 4 hours)", json_match("time_window", "4")),
                        ("Full Day (greater than 4 hours)", json_match("time_window", "8"))])
    return hist(add_sum_total(summarize(add_other(add_freeform(spec)))))

def size_cap_report():
    spec = OrderedDict([("<5 kW", lt(json_extract("value"), 5)),
                        ("5-10 kW", between(json_extract("value"), 5, 10)),
                        ("10-15 kW", between(json_extract("value"), 10, 15)),
                        ("15-20 kW", between(json_extract("value"), 15, 20)),
                        (">20 kW", gte(json_extract("value"), 20))])
    return hist(add_sum_total(summarize(add_other(spec))))

def sb1222_report():
    spec = OrderedDict([("Yes", json_match("compliant", "yes")),
                        ("Yes, with evidence", json_match("compliant", "yes, with exceptions")),
                        ("No", json_match("compliant", "no"))])
    return pie(add_sum_total(summarize(add_other(spec))))

reports_by_type = {
    "available_url_display": [coverage_report(), yes_no_field("available")],
    "radio_with_exception_display": [coverage_report(), yes_no_exception_field("required")],
    "plan_check_service_type_display": [coverage_report(), plan_check_service_type_report()],
    "radio_compliant_sb1222_with_exception": [coverage_report(), sb1222_report()],
    "inspection_checklists_display": [coverage_report(), yes_no_field("available")],
    "radio_has_training_display": [coverage_report(), yes_no_field("value")],
    "phone_display": [coverage_report()],
    "url": [coverage_report()],
    "address_display": [coverage_report()],
    "radio_submit_PE_stamped_structural_letter_with_exception_display": [coverage_report(), yes_no_exception_field("required")],
    "hours_display": [coverage_report()], # histogram
    "turn_around_time_display": [coverage_report(), turn_around_report()],
    "permit_cost_display": [coverage_report()], # check the spec, probably needs histograms and stuff
    "radio_required_for_page_sizes_display": [coverage_report(), yes_no_field("required")], # should do more for the required values
    "radio_required_for_scales_display": [coverage_report()], # likewise
    "radio_required_display": [coverage_report()],
    "radio_covered_with_exception_display": [coverage_report(), yes_no_exception_field("allowed")],
    "radio_studer_vent_rules_with_exception_display": [coverage_report(), yes_no_exception_field("allowed")],
    "radio_module_drawings_display": [coverage_report(), module_drawings_report()],
    "radio_allowed_with_exception_display": [coverage_report(), yes_no_exception_field("allowed")],
    "required_spec_sheets_display": [coverage_report()],
    "homeowner_requirements_display": [coverage_report()], # two yes/no answers in one
    "fire_setbacks_display": [coverage_report(), yes_no_exception_field("enforced")],
    "radio_inspection_approval_copies_display": [coverage_report(), inspection_approval_report()],
    "signed_inspection_approval_delivery_display": [coverage_report()],
    "radio_vent_spanning_rules_with_exception_display": [coverage_report(), yes_no_exception_field("allowed")],
    "solar_permitting_checklists_display": [coverage_report(), yes_no_field("available")],
    "radio_available_with_exception_display": [coverage_report(), yes_no_exception_field("available")],
    "time_window_display": [coverage_report(), time_window_report()],
    "radio_has_training_display": [coverage_report(), yes_no_field("value")],
    "radio_licensing_required_display": [coverage_report(), yes_no_field("required")],
    "online_forms": [coverage_report()],
    None: [coverage_report()],
}

reports_by_qid = {
#    15: { #
#        'query': '''SELECT (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp1 WHERE value LIKE '%value"%"yes%') as Yes, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp2 WHERE value LIKE '%value"%"no%' ) as No, (SELECT count(*) FROM (SELECT value FROM `website_answerreference` WHERE question_id = '15' AND jurisdiction_id NOT IN ('1','101105') AND approval_status LIKE 'A' GROUP BY jurisdiction_id ASC, create_datetime DESC) AS tmp3) as Total FROM website_answerreference LIMIT 1''',
#        'keys_in_order': ['Yes', 'No', 'Total'],
#    },
    15: [coverage_report(), yes_no_field("value")],
    71: [coverage_report(), size_cap_report()],
}
