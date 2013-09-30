from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.conf import settings
from django.db.models import Q

from website.utils.httpUtil import HttpRequestProcessor
from website.utils.geoHelper import GeoHelper
from website.utils.mathUtil import MathUtil
from website.models import Jurisdiction, AnswerReference, EntityViewCount, Zipcode
from website.views.jurisdiction import getNearbyJs

def most_recent(request):
    requestProcessor = HttpRequestProcessor(request)
    js = AnswerReference.objects.order_by('-create_datetime')
    js = js.values('jurisdiction__id', 'jurisdiction__name', 'create_datetime')
    output1 = []
    temp = []
    for j in js:
        if temp.count(j['jurisdiction__id']) == 0:
            ja = {}
            ja['id'] = j['jurisdiction__id']
            ja['name'] = Jurisdiction.objects.get(id = j['jurisdiction__id']).show_jurisdiction()
            
            #ja['time'] = str(j['create_datetime'])
            temp.append(j['jurisdiction__id'])
            output1.append(ja)
        if len(temp) == 10:
            break 
    return HttpResponse(json.dumps(output1))

def most_popular(request):
    requestProcessor = HttpRequestProcessor(request)

    most_popular_jurs = []        
    most_popular_jurs_qryset = EntityViewCount.objects.filter(entity_name__iexact='jurisdiction').order_by('-count_30_days')[:10]
    if most_popular_jurs_qryset:
        for jur in most_popular_jurs_qryset:
            most_popular_jur = {}
            most_popular_jur['id'] = jur.entity_id
            most_popular_jur['name'] = Jurisdiction.objects.get(id=jur.entity_id).show_jurisdiction()
            most_popular_jurs.append(most_popular_jur)
            #most_popular_jurs.append([jur.entity_id, Jurisdiction.objects.get(id=jur.entity_id).show_jurisdiction()])          
        
    return HttpResponse(json.dumps(most_popular_jurs))

def search_general(request):
    requestProcessor = HttpRequestProcessor(request)
    output = ''
    
    text = requestProcessor.getParameter('text')
    if text == None: 
        return HttpResponse(output)
    
    output += '<div>' #a div to enclose everything
    
    #jurisdictions
    output += '<ul id="cities">'
    jurisdictions = Jurisdiction.objects.filter(name__icontains=text).order_by('name', 'state')[:10]
    for jurisdiction in jurisdictions:
        output += '<li><a href="/jurisdiction/'+str(jurisdiction.id)+'">'+jurisdiction.show_jurisdiction()+'</a></li>'
    output += '</ul>'
    
    #zipcodes for testing
    output += '<ul id="zipcodes">'
    zipcodes = Zipcode.objects.filter(zip_code__contains=text).order_by('zip_code')[:10]
    for zipcode in zipcodes:
        output += '<li>'+zipcode.city+', '+zipcode.state+'  '+str(zipcode.zip_code)+'</li>'
    output += '</ul>'
    
    output += '</div>'
    
    return HttpResponse(output)
