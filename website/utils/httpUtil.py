import json
from django.http import HttpRequest

# for jinja2
from django.conf import settings
from django.template.loader import render_to_string
from django.shortcuts import render
from django.contrib.auth.models import User
from website.models import UserSearch

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
    def render_to_response(self, request, filename, context={}, mimetype=''):
        # don't add any new callers to this; you should be calling the
        # django render_to_response directly
        user = request.user
        context['user_searches'] = UserSearch.get_user_recent(user)
        return render(request, filename.replace(".html", ".jinja"), context, content_type=mimetype)
    
    def decode_jinga_template(self, request, filename, context={}, mimetype=''):
        return render_to_string(filename.replace(".html", ".jinja"), context)
