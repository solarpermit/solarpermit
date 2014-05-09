import re
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.localflavor.us.us_states import US_STATES
from django.contrib import messages
from django.template.loader import get_template as django_get_template
from django.template import Context, RequestContext
from website.utils.httpUtil import HttpRequestProcessor
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render

from django.shortcuts import render_to_response, redirect
from website.utils.mathUtil import MathUtil
from website.utils.geoHelper import GeoHelper
from website.models import Jurisdiction, Zipcode, UserSearch, Question, AnswerReference, OrganizationMember, QuestionCategory, Comment, UserCommentView, Template, ActionCategory, JurisdictionContributor, Action, UserDetail, OrganizationMember
from website.models import View, ViewQuestions, ViewOrgs
from website.models import ServerVariable
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from website.utils.miscUtil import UrlUtil
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.datetimeUtil import DatetimeHelper
from django.contrib.auth.models import User
import json
import datetime
from website.models import UserPageView 

from BeautifulSoup import BeautifulSoup

def task_list(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    data = {}

    return requestProcessor.render_to_response(request,'website/siteadmin/task_list.html', data, '')          
    

def user_page_views(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    data = {}    
    
    # get orgs that have members
    members_orgs = OrganizationMember.objects.filter(status__iexact='A', organization__status__iexact='A').values('organization__id', 'organization__name').order_by('organization__name')
    data['members_orgs'] = members_orgs
    
    
    # get members for each org
    org_members = {}
    orgs_members = OrganizationMember.objects.filter(status__iexact='A', organization__status__iexact='A').values('organization__id', 'user__id', 'user__username').order_by('organization__name', 'user__username')
        
    for org in orgs_members:
        if org['organization__id'] not in org_members:
            org_members[org['organization__id']] = {}
            
        org_members[org['organization__id']][org['user__id']]= org['user__username']    
    
    data['org_members'] = org_members
    
    # get user page viewings
    user_pages = {}
    user_page_views = UserPageView.objects.all().order_by('user__username', 'url', 'last_page_view_date')
    for user_page_view in user_page_views:
        user_pages[user_page_view.user_id] = user_page_views
    

    data['user_pages'] = user_pages
    #orgmembers = OrganizationMember.objects.filter(status__iexact='A', organization__status__iexact='A').order_by('organization__name', 'user__username')
    
    # get non-affiliated users
    members = OrganizationMember.objects.filter(status__iexact='A', organization__status__iexact='A').values_list('user__id')  
    users_with_orgs = User.objects.filter(id__in=members)  
    users = User.objects.exclude(id__in=users_with_orgs).order_by('username')

    data['users'] = users
    
    return requestProcessor.render_to_response(request,'website/siteadmin/user_page_views.html', data, '')      