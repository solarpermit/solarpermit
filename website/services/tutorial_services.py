from datetime import datetime, timedelta
from django.http import HttpRequest, HttpResponse
from django.utils import simplejson as json
from django.contrib.auth import authenticate, logout
from django.conf import settings
from django.contrib.auth.models import User
from website.models import Tutorial, TutorialPage, ActionTutorial, UserTutorialHistory, UserTutorialPageHistory
from website.utils.httpUtil import HttpRequestProcessor
from website.utils.sessionHelper import SessionHelper


def getTutorial(request):
    requestProcessor = HttpRequestProcessor(request)
    
    output = {}
    output['e'] = False
    output['m'] = ''
    
    '''sid = requestProcessor.getParameter('sid')
    if sid == None: 
        output['e'] = True
        output['m'] = 'No sid provided'
        return HttpResponse(json.dumps(output))
    
    sessionHelper = SessionHelper()
    sessionHelper.checkSession(sid)
    
    if sessionHelper.error == True:
        output['e'] = True
        output['m'] = sessionHelper.message
        return HttpResponse(json.dumps(output))'''

    try: #get session user's email
        user = request.user
        userEmail = user.email
    except:
        output['e'] = True
        output['m'] = 'Invalid user.'
        return HttpResponse(json.dumps(output))
    
    action = requestProcessor.getParameter('action')
    if action == None: 
        output['e'] = True
        output['m'] = 'No action provided'
        return HttpResponse(json.dumps(output))
    
    force = requestProcessor.getParameter('force')
    
    now = datetime.now()
    dayStart = now.replace(hour=0, minute=0, second=0, microsecond=0)
    dayEnd = dayStart + timedelta(days=1)
    
    actionTutorials = ActionTutorial.objects.filter(action_identifier=action, tutorial__active=True).exclude(tutorial__start_datetime__gt=now).exclude(tutorial__end_datetime__lt=now)
    if len(actionTutorials) == 0:
        return HttpResponse(json.dumps(output))
    
    tutorial = actionTutorials[0].tutorial #just get the 1st
    
    #has this user already seen this tutorial today?
    '''histories = UserTutorialHistory.objects.filter(user_email=userEmail, tutorial=tutorial, view_datetime__gte=dayStart, view_datetime__lt=dayEnd)
    if len(histories) > 0:
        return HttpResponse(json.dumps(output))
    else:
        #now remember this use has seen this tutorial today
        history = UserTutorialHistory(user_email=userEmail, tutorial=tutorial, view_datetime=now)
        history.save()'''
    
    histories = UserTutorialHistory.objects.filter(user_email=userEmail, tutorial=tutorial)
    if len(histories) > 0:
        history = histories[0]
        if force != 'true':
        #show only if user has not seen it today
            if history.view_datetime >= dayStart and history.view_datetime < dayEnd:
                return HttpResponse(json.dumps(output))
    else:
        history = UserTutorialHistory(user_email=userEmail, tutorial=tutorial)
    #update or save history since we are going to show it
    history.view_datetime = now
    history.save()
    
    output['d'] = {}
    output['d']['tid'] = tutorial.id
    output['d']['tips'] = []    
    tutorialPages = TutorialPage.objects.filter(tutorial=tutorial).order_by('display_order')
    pages = UserTutorialPageHistory.objects.filter(user_email=userEmail, tutorial=tutorial)
    checked_pages = UserTutorialPageHistory.objects.filter(user_email=userEmail, tutorial=tutorial, checked = 1)
    all_checked = False
    if len(pages) == len(checked_pages):
        all_checked = True
    i = 0
    for page in tutorialPages:
        pageObj = {}
        pageObj['s'] = page.selector
        pageObj['t'] = page.tip
        pageObj['id'] = page.id
        
        #get page status from user tutorial page history
        try:
            pageHistory = UserTutorialPageHistory.objects.get(user_email=userEmail, tutorial=tutorial, page=page)
            if pageHistory.checked == True:
                if all_checked == True and i == 0 and force == 'true':
                    pageObj['c'] = False
                else:
                    pageObj['c'] = True
            else:
                pageObj['c'] = False
        except:
            pageObj['c'] = False
        
        output['d']['tips'].append(pageObj)
        i = i + 1
        
    return HttpResponse(json.dumps(output))

#client tell server that user has check or uncheck page checkbox
def pageStatus(request):
    requestProcessor = HttpRequestProcessor(request)
    
    output = {}
    output['e'] = False
    output['m'] = ''
    
    '''sid = requestProcessor.getParameter('sid')
    if sid == None: 
        output['e'] = True
        output['m'] = 'No sid provided'
        return HttpResponse(json.dumps(output))
    
    sessionHelper = SessionHelper()
    sessionHelper.checkSession(sid)
    
    if sessionHelper.error == True:
        output['e'] = True
        output['m'] = sessionHelper.message
        return HttpResponse(json.dumps(output))'''

    try: #get session user's email
        user = request.user
        userEmail = user.email
    except:
        output['e'] = True
        output['m'] = 'Invalid user.'
        return HttpResponse(json.dumps(output))
    
    tutorialId = requestProcessor.getParameter('tid')
    if tutorialId == None: 
        output['e'] = True
        output['m'] = 'No tid provided'
        return HttpResponse(json.dumps(output))
    
    pageId = requestProcessor.getParameter('pid')
    if pageId == None: 
        output['e'] = True
        output['m'] = 'No pid provided'
        return HttpResponse(json.dumps(output))
   
    checked = requestProcessor.getParameter('c')
    if checked == None: 
        output['e'] = True
        output['m'] = 'No c provided'
        return HttpResponse(json.dumps(output))
    
    try:
        tutorial = Tutorial.objects.get(id=tutorialId)
    except:
        output['e'] = True
        output['m'] = 'Tutorial does not exist.'
        return HttpResponse(json.dumps(output))
    try:
        tutorialPage = TutorialPage.objects.get(id=pageId)
    except:
        output['e'] = True
        output['m'] = 'Tutorial page does not exist.'
        return HttpResponse(json.dumps(output))
    
    #add or update user tutorial page history
    try:
        pageHistory = UserTutorialPageHistory.objects.get(user_email=userEmail, tutorial=tutorial, page=tutorialPage)
    except:
        pageHistory = UserTutorialPageHistory(user_email=userEmail, tutorial=tutorial, page=tutorialPage)
    if checked == '1':
        pageHistory.checked = True
    else:
        pageHistory.checked = False
    pageHistory.save()
   
    return HttpResponse(json.dumps(output))
    