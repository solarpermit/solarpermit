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
from website.models import Jurisdiction, Zipcode, UserSearch, Question, AnswerReference, AnswerAttachment, OrganizationMember, QuestionCategory, Comment, UserCommentView, Template, ActionCategory, JurisdictionContributor, Action, UserDetail, OrganizationMember
from website.models import View, ViewQuestions, ViewOrgs
from website.utils.messageUtil import MessageUtil,add_system_message,get_system_message
from website.utils.miscUtil import UrlUtil
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.datetimeUtil import DatetimeHelper
from django.contrib.auth.models import User
import json
import datetime

from BeautifulSoup import BeautifulSoup
from website.utils.fileUploader import qqFileUploader



def view_AHJ(request, id, category='all_info'):
    requestProcessor = HttpRequestProcessor(request)
    layout = requestProcessor.getParameter('layout')
    data = {}
    
    # get user specific
    #define core data
        
    return requestProcessor.render_to_response(request,'website/jurisdictions/AHJ_categories_questions.html', data, '')