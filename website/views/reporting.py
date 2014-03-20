# -*- coding: utf-8 -*-
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor
from django.conf import settings as django_settings
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
import hashlib
from website.models import Question, QuestionCategory, Jurisdiction, GeographicArea
from django.db import connection
from collections import OrderedDict
import json
import re
from django.db.models import Q
from django.db.models.sql import Query
from django.db import DEFAULT_DB_ALIAS
from django.contrib.localflavor.us.us_states import US_STATES
from autocomplete.widgets import MultipleAutocompleteWidget
from website.views.autocomp import autocomplete_instance

def build_query(question, field_map, geo_filter=None):
    # Yes we have two mechanisms for building queries here. We've
    # hacked out a slice of the django sql "compiler" for one of them,
    # since they specialize in where clauses, while writing a simpler
    # one of our own that specializes in select clauses. Both of them
    # bear more than a passing resemblance to lisp, of course.
    indent = "                     ";
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
        compiled_filter = where % tuple(where_params)
    return ('''
               SELECT %(fields)s
               FROM (SELECT id AS answer_id,
                            (SELECT value FROM website_answerreference WHERE id = answer_id) AS value
                     FROM (SELECT (SELECT id
                                   FROM website_answerreference
                                   WHERE id = (SELECT MAX(id)
                                               FROM website_answerreference
                                               WHERE website_answerreference.jurisdiction_id = website_jurisdiction.id AND
                                                     approval_status = 'A' AND
                                                     question_id = %(question_id)s)) AS id
                           FROM website_jurisdiction
                           WHERE website_jurisdiction.id NOT IN (1, 101105) AND
                                 website_jurisdiction.jurisdiction_type != 'u' ''' +
            ("AND\n                                %(geo_filter)s" if geo_filter else "") +
            ''') AS temp0) as temp1
            ''') % { "question_id": question.id,
                     "fields": sep.join(fields),
                     "geo_filter": compiled_filter }

def json_match(field_name, value, op="="):
    return and_match(not_null_match(json_extract(field_name)),
                     'json_get(value, "%s") %s "%s" COLLATE utf8_general_ci' % (field_name, op, value))
    return regexp_match('"%(name)s": *"%(value)s"' % { "name": escape_regex_inclusion(field_name),
                                                       "value": escape_regex_inclusion(value) })
def json_extract(field_name):
    return 'json_get(value, "%s")' % field_name
def json_valid():
    return 'json_valid(value)'

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
    return not_null_match("answer_id")

def and_match(*args):
    return parenthesize(" AND ".join(args))
def or_match(*args):
    return parenthesize(" OR ".join(args))
def not_match(match):
    return parenthesize('NOT (%s)' % match)

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
    return pie(add_count_total(summarize(spec)))

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
# also, shouldn't this go by multiples of 5? presumably it's business days…
def turn_around_report():
    bins = OrderedDict([("Same day", json_match("time_unit", "hour(s)")),
                        ("1-2 days", and_match(json_match("time_unit", "day(s)"),
                                               lte(json_extract("time_qty"), 2))),
                        ("3-7 days", or_match(and_match(json_match("time_unit", "day(s)"),
                                                        between(json_extract("time_qty"), 3, 7)),
                                              and_match(json_match("time_unit", "week(s)"),
                                                        json_match("time_qty", "1")))),
                        ("8-14 days", or_match(and_match(json_match("time_unit", "day(s)"),
                                                         between(json_extract("time_qty"), 8, 14)),
                                               and_match(json_match("time_unit", "week(s)"),
                                                         json_match("time_qty", "2")))),
                        ("15-21 days", or_match(and_match(json_match("time_unit", "day(s)"),
                                                          between(json_extract("time_qty"), 15, 21)),
                                                and_match(json_match("time_unit", "week(s)"),
                                                          json_match("time_qty", "3")))),
                        ("22+ days", or_match(and_match(json_match("time_unit", "day(s)"),
                                                        gte(json_extract("time_qty"), 22)),
                                              and_match(json_match("time_unit", "week(s)"),
                                                        gte(json_extract("time_qty"), 4))))])
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

reports_by_type = {
    "available_url_display.html": [coverage_report(), yes_no_field("available")],
    "radio_with_exception_display.html": [coverage_report(), yes_no_exception_field("required")],
    "plan_check_service_type_display.html": [coverage_report(), plan_check_service_type_report()],
    "radio_compliant_sb1222_with_exception.html": [coverage_report(), yes_no_exception_field("compliant")],
    "inspection_checklists_display.html": [coverage_report(), yes_no_field("value")],
    "radio_has_training_display.html": [coverage_report(), yes_no_field("value")],
    "phone_display.html": [coverage_report()],
    "url.html": [coverage_report()],
    "address_display.html": [coverage_report()],
    "radio_submit_PE_stamped_structural_letter_with_exception_display.html": [coverage_report(), yes_no_exception_field("required")],
    "hours_display.html": [coverage_report()], # histogram
    "turn_around_time_display.html": [coverage_report(), turn_around_report()],
    "available_url_display.html": [coverage_report()],
    "permit_cost_display.html": [coverage_report()], # check the spec, probably needs histograms and stuff
    "radio_required_for_page_sizes_display.html": [coverage_report(), yes_no_field("required")], # should do more for the required values
    "radio_required_for_scales_display.html": [coverage_report()], # likewise
    "radio_required_display.html": [coverage_report()],
    "radio_covered_with_exception_display.html": [coverage_report(), yes_no_exception_field("allowed")],
    "radio_studer_vent_rules_with_exception_display.html": [coverage_report(), yes_no_exception_field("allowed")],
    "radio_module_drawings_display.html": [coverage_report(), module_drawings_report()],
    "radio_allowed_with_exception_display.html": [coverage_report(), yes_no_exception_field("allowed")],
    "required_spec_sheets_display.html": [coverage_report()],
    "homeowner_requirements_display.html": [coverage_report()], # two yes/no answers in one
    "fire_setbacks_display.html": [coverage_report(), yes_no_exception_field("enforced")],
    "radio_inspection_approval_copies_display.html": [coverage_report(), inspection_approval_report()],
    "signed_inspection_approval_delivery_display.html": [coverage_report()],
    "radio_vent_spanning_rules_with_exception_display.html": [coverage_report(), yes_no_exception_field("allowed")],
    "solar_permitting_checklists_display.html": [coverage_report()],
    "radio_available_with_exception_display.html": [coverage_report(), yes_no_exception_field("available")],
    "time_window_display.html": [coverage_report(), time_window_report()],
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

    def param(p):
        s = request.GET[p]
        return s.split(",") if s else []
    def quoted_param(p):
        return ['"%s"' % s for s in param(p)]

    geo_filter = None
    if 'states' in request.GET:
        geo_filter = Q(state__in = quoted_param('states'))
    elif 'counties' in request.GET:
        geo_filter = Q(county__in = quoted_param('counties'))
    elif 'jurisdictions' in request.GET:
        geo_filter = Q(pk__in = param('jurisdictions'))

    data = {}
    data['current_nav'] = 'reporting'
    data['report_name'] = question.question
    data['question_instruction'] = question.instruction
    reports = (question.id in reports_by_qid and reports_by_qid[question_id]) or \
              (question.display_template in reports_by_type and reports_by_type[question.display_template])

    data['reports'] = []
    idx = 0
    for report in reports:
      query = build_query(question, report['spec'], geo_filter)
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

class GeographicAreaForm(forms.ModelForm):
    name = forms.CharField()
    states = forms.MultipleChoiceField(choices = US_STATES,
                                       required = False)
    counties = forms.ModelMultipleChoiceField(queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CO', 'SC', 'CC')),
                                              widget = MultipleAutocompleteWidget("counties", view=autocomplete_instance),
                                              required = False)
    cities = forms.ModelMultipleChoiceField(queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CC', 'CI', 'IC')),
                                            widget = MultipleAutocompleteWidget("cities", view=autocomplete_instance),
                                            required = False)
    def clean(self):
        cleaned_data = super(GeographicAreaForm, self).clean()
        states = cleaned_data['states']
        del cleaned_data['states']
        counties = cleaned_data['counties']
        del cleaned_data['counties']
        cities = cleaned_data['cities']
        del cleaned_data['cities']

        cleaned_data['jurisdictions'] = states or counties or cities
        from pprint import pprint
        pprint(cleaned_data)
        return cleaned_data
        
    class Meta:
        model = GeographicArea
        fields = ['name', 'description', 'states', 'counties', 'cities']

class GeographicAreaDetail(DetailView):
    queryset = GeographicArea.objects.all()
    template_name = 'geographic_area_detail.jinja'

class GeographicAreaList(ListView):
    queryset = GeographicArea.objects.all()
    template_name = 'geographic_area_list.jinja'
    
class GeographicAreaCreate(CreateView):
    model = GeographicArea
    fields = ['name']
    template_name = 'geographic_area_form.jinja'
    form_class = GeographicAreaForm

class GeographicAreaUpdate(UpdateView):
    model = GeographicArea
    fields = ['name']
    template_name = 'geographic_area_form.jinja'

class GeographicAreaDelete(DeleteView):
    model = GeographicArea
    success_url = reverse_lazy('geoarea-list')
    template_name = 'geographic_area_confirm_delete.jinja'
