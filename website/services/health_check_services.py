from datetime import datetime
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.conf import settings
from website.utils.httpUtil import HttpRequestProcessor
from website.models import Jurisdiction

# see if server is working, no database check
def server_check(request):
    requestProcessor = HttpRequestProcessor(request)
    output = {}
    
    now = datetime.now()
    output['t'] = now.isoformat()
    
    output['e'] = False
    output['m'] = 'Server is working.'
    return HttpResponse(json.dumps(output))

# see if both server and database is working
def db_check(request):
    requestProcessor = HttpRequestProcessor(request)
    output = {}
    
    now = datetime.now()
    output['t'] = now.isoformat()
    
    jurisdictions = Jurisdiction.objects.filter(name__contains='San Francisco')
    if len(jurisdictions) == 0:
        output['e'] = True
        output['m'] = 'Database is not working!'
        return HttpResponse(json.dumps(output))
    
    output['e'] = False
    output['m'] = 'Server and database are working.'
    return HttpResponse(json.dumps(output))
    