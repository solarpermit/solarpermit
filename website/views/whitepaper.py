import datetime
import hashlib
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor#, decode_jinga_template
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.db.models import Q
from django.conf import settings
from jinja2 import FileSystemLoader, Environment

from website.utils.mathUtil import MathUtil
from website.models import Organization, RoleType, OrganizationMember, UserDetail
from sorl.thumbnail import get_thumbnail
from website.utils.fileUploader import qqFileUploader

from website.utils.messageUtil import MessageUtil

ORGANIZATION_PAGE_SIZE = 20

def papers(request):
    requestProcessor = HttpRequestProcessor(request)  
    data = {}
    dajax = Dajax()
    user = request.user
    data['user'] = user
    ajax = requestProcessor.getParameter('ajax')
    if ajax == 'open_papers':         
        body = requestProcessor.decode_jinga_template(request, 'website/whitepapers/whitepapers.html', data, '') 
        dajax.assign('#fancyboxformDiv','innerHTML', body)
        script = requestProcessor.decode_jinga_template(request, 'website/whitepapers/whitepapers.js', data, '')
        dajax.script(script)

    #add script to open fancybox if command starts with 'open'
    if ajax.startswith('open'):
        dajax.script('controller.showModalDialog("#fancyboxformDiv");')
        
    return HttpResponse(dajax.json())
            