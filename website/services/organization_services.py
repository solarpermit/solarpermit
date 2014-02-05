from datetime import datetime, timedelta
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.contrib.auth import authenticate, logout
from django.db.models import Q
from django.conf import settings
from django.contrib.auth.models import User
from website.utils.httpUtil import HttpRequestProcessor
from website.utils.sessionHelper import SessionHelper
from website.models import Organization, OrganizationMember, RatingCategory, OrganizationRating, Jurisdiction, JurisdictionContributor
from django.contrib.sites.models import Site
from django.contrib.sites.models import get_current_site

from django.conf import settings as django_settings

def get_organization(request):
    requestProcessor = HttpRequestProcessor(request)
    
    output = {}
    output['organizations'] = []
    
    text = requestProcessor.getParameter('text')
    if text == None: 
       return HttpResponse(json.dumps(output))
    
    #only if text is at least 2 chars
    if len(text) > 1:
        orgs = Organization.objects.filter(Q(name__icontains=text)).order_by('name')[0:20]
        for org in orgs:
            org_item = {}
            org_item['id'] = org.id
            org_item['name'] = org.name
            output['organizations'].append(org_item)
        
    return HttpResponse(json.dumps(output))
    
def set_member(request):
    requestProcessor = HttpRequestProcessor(request)
    
    output = {}
    output['e'] = False
    output['m'] = ''
    
    org_id = requestProcessor.getParameter('org_id')
    if org_id == None: 
        output['e'] = True
        output['m'] = 'No org_id provided'
        return HttpResponse(json.dumps(output))
    
    username = requestProcessor.getParameter('username')
    if username == None: 
        output['e'] = True
        output['m'] = 'No username provided'
        return HttpResponse(json.dumps(output))
    
    try:
        organization = Organization.objects.get(id=org_id)
    except:
        output['e'] = True
        output['m'] = 'Organization not found.'
        return HttpResponse(json.dumps(output))
    
    try:
        user = User.objects.get(username=username)
    except:
        output['e'] = True
        output['m'] = 'User not found.'
        return HttpResponse(json.dumps(output))
    
    organization.set_member(user)
        
    return HttpResponse(json.dumps(output))

def delete_organization(request):
    requestProcessor = HttpRequestProcessor(request)
    user = request.user
    
    output = {}
    output['e'] = False
    output['m'] = ''
    
    org_id = requestProcessor.getParameter('org_id')
    if org_id == None: 
        output['e'] = True
        output['m'] = 'No org_id provided.'
        return HttpResponse(json.dumps(output))
    
    try:
        organization = Organization.objects.get(id=org_id)
    except:
        output['e'] = True
        output['m'] = 'Organization does not exist.'
        return HttpResponse(json.dumps(output))
        
    try:
        owner = OrganizationMember.objects.get(organization=organization, role__name='Owner', status='A')
    except:
        owner = None
    
    #is user the owner or admin?
    if user.is_staff != True:
        if owner != None:
            if user != owner.user:
                output['e'] = True
                output['m'] = 'You do not have the access right to delete this organization.'
                return HttpResponse(json.dumps(output))
    
    #does org has other members besides owner
    members = OrganizationMember.objects.filter(organization=organization, status='A').exclude(user=owner.user)
    if len(members) > 0:
        output['e'] = True
        output['m'] = 'You cannot delete an organization that has other active members.'
        return HttpResponse(json.dumps(output))
        
    organization.delete()
    output['m'] = 'Organization deleted.'
    return HttpResponse(json.dumps(output))

def top_org_contributors(request):
    requestProcessor = HttpRequestProcessor(request)

    number = requestProcessor.getParameter('number')
    if number == None:
        number = 3
        
    jid = requestProcessor.getParameter('jid')
    if jid != None:
        jurisdiction = Jurisdiction.objects.get(id=jid)       

    current_site = get_current_site(request)

    logo_src = str(current_site.name) + str(django_settings.MEDIA_URL) 

    top_org_contributors = []        
    rating_category = RatingCategory.objects.get(id=1)

    
    if jid == None:
        top_org_contributors_qryset = OrganizationRating.objects.filter(category__exact=rating_category).order_by('-scale')[:number]
    else:
        top_org_contributors_qryset = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, question_category__isnull=True, user__isnull=True).order_by('-points')[:number]


    if top_org_contributors_qryset:
        for org in top_org_contributors_qryset:
            top_org_contributor = {}
            top_org_contributor['id'] = org.organization_id
            org = Organization.objects.get(id=org.organization_id)
            top_org_contributor['name'] = org.name
            top_org_contributor['logo_src'] = str(logo_src) + str(org.logo)
            top_org_contributors.append(top_org_contributor)

    return HttpResponse(json.dumps(top_org_contributors))
    
    