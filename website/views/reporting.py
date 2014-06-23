# -*- coding: utf-8 -*-
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django import forms
from django.core.urlresolvers import reverse, reverse_lazy
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
from website.models.reporting import where_clause_for_area, matches_for_area
from django.db import connection
from collections import OrderedDict
import json
import re
from django.db.models import Q
from django.db.models.sql import Query
from django.db import DEFAULT_DB_ALIAS
from django.contrib.localflavor.us.us_states import US_STATES
import urllib
from django.shortcuts import render_to_response
import autocomplete_light
autocomplete_light.autodiscover()
from website.utils import reporting

##############################################################################
#
# Display an individual report on a question_id
#
##############################################################################
def report_on(request, question_id=None, filter_id=None):
    # Check request for validity
    data = { 'current_nav': 'reporting',
             'reports': [] }
    reports = None
    if question_id:
      question_id = int(question_id)
      question = Question.objects.get(id=question_id)
      if not (question.id in reporting.reports_by_qid or question.display_template in reporting.reports_by_type):
          raise Http404
      data['question_id'] = question_id
      data['name'] = question.question
      data['description'] = question.description

    geo_filter = None
    if filter_id:
        data['geo_filter'] = GeographicArea.objects.get(pk=filter_id)
        geo_filter = data['geo_filter'].where()
    else:
        data['geo_filter'] = {}
        for key in ['states', 'jurisdictions']:
            p = request.GET.getlist(key)
            if p:
              data['geo_filter'][key] = p
        if data['geo_filter']:
            geo_filter = where_clause_for_area(**data['geo_filter'])
            data['geo_filter_matches'] = matches_for_area(**data['geo_filter']).count()

    if question_id:
        data['reports'] = [dict(r, **{'idx': idx})
                           for (idx, r) in enumerate(reporting.add_temporal_reports(reporting.run_reports(question,
                                                                                                          geo_filter=geo_filter)))]

    if 'HTTP_ACCEPT' in request.META and 'json' in request.META['HTTP_ACCEPT']: #hack
        return HttpResponse(json.dumps(data))
    data['reports_json'] = json.dumps(data['reports'])

    questions = Question.objects.filter(accepted='1').exclude(form_type="CF").order_by("category", "display_order")
    reports_index = []
    category_last_encountered = ''
    for question in questions:
        if question.category.name != category_last_encountered:
            category_last_encountered = question.category.name
            # the category level does not exist create it.
            reports_index.append({ "category": question.category.name.replace('_', ' ').title(),
                                   "reports_in_category": [] })
        # append this report's data to the list - with a link if it exists
        reports_index[-1]['reports_in_category'].append(question)
    data['reports_index'] = reports_index
    data['report_types'] = reporting.reports_by_type.keys()
    data['report_qids'] = reporting.reports_by_qid.keys()
    data['form'] = GeographicAreaForm()
    data['request'] = request
    return render_to_response('reporting/report_on.jinja', data)

class GeographicAreaForm(forms.ModelForm):
    filter_name = forms.CharField()
    states = forms.MultipleChoiceField(choices = US_STATES,
                                       required = False)
    jurisdictions = forms.ModelMultipleChoiceField(queryset = Jurisdiction.objects.all(),
                                                   widget = autocomplete_light.MultipleChoiceWidget('JurisdictionAutocomplete'),
                                                   required = False)
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        initial = kwargs.get('initial', {})
        if instance:
            initial['states'] = instance.states
            initial['jurisdictions'] = instance.jurisdictions
        kwargs['initial'] = initial
        super(GeographicAreaForm, self).__init__(*args, **kwargs)
    def save(self, commit=True):
        area = super(GeographicAreaForm, self).save(commit)
        if commit and 'jurisdictions' in self.cleaned_data:
            area.jurisdictions.add(*self.cleaned_data['jurisdictions'])
            area.save()
        return area
    class Meta:
        model = GeographicArea
        fields = ['filter_name', 'description', 'states', 'jurisdictions']

class GeographicAreaDetail(DetailView):
    queryset = GeographicArea.objects.all()
    template_name = 'geographic_area_detail.jinja'

class GeographicAreaList(ListView):
    queryset = GeographicArea.objects.all()
    template_name = 'geographic_area_list.jinja'
    
class GeographicAreaCreate(CreateView):
    model = GeographicArea
    template_name = 'geographic_area_form.jinja'
    form_class = GeographicAreaForm
    def get(self, request, *args, **kwargs):
        self.initial = {key: ",".join(request.GET.getlist(key, "")).split(",") for key in set(request.GET.keys()) & set(['states', 'jurisdictions'])}
        return super(GeographicAreaCreate, self).get(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        if 'question_id' in self.kwargs:
            kwargs['question_id'] = self.kwargs['question_id']
        return super(GeographicAreaCreate, self).get_context_data(**kwargs)
    def form_valid(self, form):
        response = super(GeographicAreaCreate, self).form_valid(form)
        if 'question_id' in self.kwargs:
            self.kwargs.update({'filter_id': form.instance.pk})
            return HttpResponseRedirect(reverse('report-with-filter',
                                                kwargs = self.kwargs))
        else:
            return response
    def form_invalid(self, form):
        if 'question_id' in self.kwargs:
            params = {}
            if 'states' in form.cleaned_data and form.cleaned_data['states']:
                params['states'] = ",".join(form.cleaned_data['states'])
            elif 'jurisdictions' in form.cleaned_data and form.cleaned_data['jurisdictions']:
                params['jurisdictions'] = ",".join([str(j.pk) for j in form.cleaned_data['jurisdictions']])
            return HttpResponseRedirect(reverse('report', kwargs=self.kwargs) + '?' + \
                                        urllib.urlencode(params))
        else:
            return super(GeographicAreaCreate, self).form_invalid(form)

class GeographicAreaUpdate(UpdateView):
    model = GeographicArea
    template_name = 'geographic_area_form.jinja'
    form_class = GeographicAreaForm

class GeographicAreaDelete(DeleteView):
    model = GeographicArea
    success_url = reverse_lazy('geoarea-list')
    template_name = 'geographic_area_confirm_delete.jinja'
