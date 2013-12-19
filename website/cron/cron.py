from django.http import HttpResponse
from django.conf import settings
from website.utils.cronHelper import CronHelper
from website.utils.httpUtil import HttpRequestProcessor
from website.utils.cleanCommentViewsHelper import CleanCommentViews
from website.utils.notificationSentHelper import NotificationHelper
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil
from website.utils.templateUtil import TemplateUtil

def run_cron(request, forceRun):
    objCronHelper = CronHelper()
    objCronHelper.WriteHTML('Cron at ')
    objCronHelper.WriteCurrentTime()
    objCronHelper.WriteHTML('<br/><br/>')
    if forceRun == 'cl':
        runCleanUserCommentViewsCron(objCronHelper)
    
    if forceRun == 'immediate': 
        runImmediateNotificationCron(objCronHelper)
        return HttpResponse(objCronHelper.OutputLogs())
    
    if forceRun == 'daily':
        runDailyNotificationCron(objCronHelper)
    
    if forceRun == 'weekly':
        runWeeklyNotificationCron(objCronHelper)
    
    if forceRun == 'monthly': #
        runMonthlyNotificationCron(objCronHelper)
    
    if forceRun == 'validate': # 
        runValidateAnswersCron(objCronHelper)
        
    if forceRun == 'sitemap': # 
        runSiteMapCron(objCronHelper)
        
    if objCronHelper.EveryXHours(24, -1):
        runCleanUserCommentViewsCron(objCronHelper)
    
    if objCronHelper.EveryXMinutes(1):
        runImmediateNotificationCron(objCronHelper)
    
    if objCronHelper.EveryXHours(24, 6):
        runDailyNotificationCron(objCronHelper)
        
    if objCronHelper.EveryXHours(24, -4):
        runValidateAnswersCron(objCronHelper)
        
    if objCronHelper.EveryXHours(24, 2):
        runSiteMapCron(objCronHelper)
        
    return HttpResponse(objCronHelper.OutputLogs())
    
def runCleanUserCommentViewsCron(objCronHelper):
    objCronHelper.WriteHTML('Server Update Cron<br/>')
    aaa = CleanCommentViews()
    objCronHelper.WriteHTML(aaa.strMsg)
    objCronHelper.WriteHTML('<br/><br/>')

def runImmediateNotificationCron(objCronHelper):    
    objCronHelper.WriteHTML('Immediately Sent<br/>')
    aaa = NotificationHelper('I')
    objCronHelper.WriteHTML(aaa.strMsg)
    objCronHelper.WriteHTML('<br/><br/>')
  
def runDailyNotificationCron(objCronHelper):    
    objCronHelper.WriteHTML('Daily Sent<br/>')
    aaa = NotificationHelper('D')
    objCronHelper.WriteHTML(aaa.strMsg)
    objCronHelper.WriteHTML('<br/><br/>')

def runWeeklyNotificationCron(objCronHelper):    
    objCronHelper.WriteHTML('Weekly Sent<br/>')
    aaa = NotificationHelper('W')
    objCronHelper.WriteHTML(aaa.strMsg)
    objCronHelper.WriteHTML('<br/><br/>')
    
def runMonthlyNotificationCron(objCronHelper):    
    objCronHelper.WriteHTML('Monthly Sent<br/>')
    aaa = NotificationHelper('M')
    objCronHelper.WriteHTML(aaa.strMsg)
    objCronHelper.WriteHTML('<br/><br/>') 
    
def runValidateAnswersCron(objCronHelper):
    objCronHelper.WriteHTML('Validate Answers<br/>')
    aaa = FieldValidationCycleUtil()
    aaa.cron_validate_answers()
    objCronHelper.WriteHTML('<br/>Validate Answers Done!<br/>')

def runSiteMapCron(objCronHelper):
    objCronHelper.WriteHTML('Generate Site Map<br/>')
    template_util = TemplateUtil()
    template_util.update_site_map()
    objCronHelper.WriteHTML(template_util.strMsg)
    objCronHelper.WriteHTML('Generate Site Map Done!<br/>')
