import json
from django.http import HttpRequest

# for jinja2
from django.http import HttpResponse
from django.conf import settings
from jinja2 import FileSystemLoader, Environment
from jinja2.ext import WithExtension
from compressor.contrib.jinja2ext import CompressorExtension
from django.template import RequestContext, Template, Context
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from website.models import UserFavorite, UserSearch

from website.utils.datetimeUtil import DatetimeHelper
import datetime
# this class help to handle missing url parameters gracefully
class HttpRequestProcessor():
    request = HttpRequest #copy of the HttpRequest instance
    loadedAjaxParam = False
    ajaxParamObj = {}
    
    # create with or without an instance of HttpRequest
    def __init__(self, incomingRequest = None):
        if incomingRequest:
            self.request = incomingRequest
            
    def get_form_field_values(self, field_prefix=''):
        form_field_values = {}
        if field_prefix != '':
            for key in self.request.POST.keys():
                if field_prefix in key:
                    field_name = key.replace('field_', '');
                    form_field_values[field_name] = self.request.POST.get(key)
        else:
            for key in self.request.POST.keys():
                form_field_values[key] = self.request.POST.get(key)      
        
        return form_field_values      
        
    def getParameter(self, parameter):
        try:
            return self.request.REQUEST[parameter]
        except KeyError:
            return None #set to None if no such parameter

    def getParameterList(self, parameter):
        try:
            return self.request.REQUEST.getlist(parameter)
        except KeyError:
            return None #set to None if no such parameter

    def getAjaxParam(self, name):
        #parse ajax parameters only if has not done it
        if self.loadedAjaxParam == False:
            ajaxParamJson = self.getParameter('_ajax_param')
            if (ajaxParamJson != None):
                self.ajaxParamObj = json.loads(ajaxParamJson)
            self.loadedAjaxParam = True
        try:
            value = self.ajaxParamObj[name]
            return value
        except KeyError:
            return '' #return blank to avoid processing at the view
    
    # for jinja2
    def render_to_response(self, request, filename, context={},mimetype=''):
        #add recent items to context
        print 'start time of template rendering' + str(datetime.datetime.now().strftime("%d %b %Y %I:%M:%S %p"))        
        user = request.user
        context['user_searches'] = UserSearch.get_user_recent(user)
        context['INTERNAL_IPS'] = settings.INTERNAL_IPS   
        context['ENABLE_GOOGLE_ANALYTICS'] = settings.ENABLE_GOOGLE_ANALYTICS   
        context['SOLARPERMIT_VERSION'] = "?v="+str(settings.SOLARPERMIT_VERSION)                 
        context['FORUM_INTEGRATION'] = settings.FORUM_INTEGRATION   
                
        template_dirs = settings.TEMPLATE_DIRS
        if mimetype == '':
            mimetype = settings.DEFAULT_CONTENT_TYPE
        env = Environment(loader=FileSystemLoader(template_dirs),
                          extensions=[CompressorExtension, WithExtension])
        env.globals['url'] = lambda view, **kwargs: reverse(view, kwargs=kwargs)
        
        request_context = RequestContext(request, context)
        csrf = request_context.get('csrf_token')
 
        context['csrf_token'] = csrf
        context['request'] = request
        template = env.get_template(filename)
        rendered = template.render(**context)
        print 'end time of template rendering' + str(datetime.datetime.now().strftime("%d %b %Y %I:%M:%S %p")) 
        return HttpResponse(rendered,mimetype=mimetype)
    
    def decode_jinga_template(self, request, filename, context={}, mimetype=''):
        template_dirs = settings.TEMPLATE_DIRS
        if mimetype == '':
            mimetype = settings.DEFAULT_CONTENT_TYPE
        env = Environment(loader=FileSystemLoader(template_dirs),
                          extensions=[CompressorExtension, WithExtension])
        env.globals['url'] = lambda view, **kwargs: reverse(view, kwargs=kwargs)
        
        context['INTERNAL_IPS'] = settings.INTERNAL_IPS  
        context['ENABLE_GOOGLE_ANALYTICS'] = settings.ENABLE_GOOGLE_ANALYTICS   
        context['SOLARPERMIT_VERSION'] = "?v="+str(settings.SOLARPERMIT_VERSION)  
        context['FORUM_INTEGRATION'] = settings.FORUM_INTEGRATION                    
                            
        request_context = RequestContext(request, context)
        csrf = request_context.get('csrf_token')
      
        context['csrf_token'] = csrf
        context['request'] = request        
        template = env.get_template(filename)
        rendered = template.render(**context)        


                
        return rendered
        
