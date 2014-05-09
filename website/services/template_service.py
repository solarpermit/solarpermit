from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.conf import settings
from django.db.models import Q

from website.utils.httpUtil import HttpRequestProcessor
from website.models import Jurisdiction, AnswerChoiceGroup, AnswerChoice

def j_search(request):
    requestProcessor = HttpRequestProcessor(request)
    s = requestProcessor.getParameter('s')    
    js = Jurisdiction.objects.filter(name__istartswith = s).order_by('name','city', 'county', 'state')
    if len(js) > 20:
        js = js[0:20]
    output1 = [{'label':'-----', 'value':'0'}]
    for j in js:
        ja = {}
        ja['label'] = j.show_jurisdiction()
        ja['value'] = j.id
        output1.append(ja)
    output = {'output': output1}   
    return HttpResponse(json.dumps(output))

def auto_search(request):
    requestProcessor = HttpRequestProcessor(request)
    s = requestProcessor.getParameter('s')
    gid = requestProcessor.getParameter('gid')
    if gid > 0:
        acg =  AnswerChoiceGroup.objects.get(id = gid)
        acs =  AnswerChoice.objects.filter(label__istartswith = s, answer_choice_group = acg)
    else:
        acs =  AnswerChoice.objects.filter(label__istartswith = s)
    output1 = [{'label':'-----', 'value':'0'}]
    for ac in acs:
        ja = {}
        ja['label'] = ac.label
        ja['value'] = ac.value
        output1.append(ja)
    output = {'output': output1}   
    return HttpResponse(json.dumps(output))
    