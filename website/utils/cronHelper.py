from django.conf import settings
from django.utils.encoding import smart_unicode 
from datetime import *
import os

class CronHelper:
    objDateTimeNow = None
    fileName = ''
    filePointer = None
    forceRun = False
    logBuffer = '' #all the text from WriteHTML, to be shown on the cron page

    def __init__(self, strSpecialName=''):   
        self.objDateTimeNow = datetime.now()
        Y = str(self.objDateTimeNow.year)
        M = str(self.objDateTimeNow.month)
        D = str(self.objDateTimeNow.day)
        if len(M) == 1:
            M = '0' + M
        if len(D) == 1:
            D = '0' + D

        strLogPath = settings.LOG_ROOT
        if not '/' == strLogPath[-1]:
            strLogPath += '/'
        #strLogPath += 'todo'
        if not os.path.isdir(strLogPath):
            os.mkdir(strLogPath)
        self.fileName = strLogPath + 'doe_cronLogs' + Y + M + D + strSpecialName + '.html'
        self.filePointer = file(self.fileName, 'a')
        self.forceRun = False

    def __del__(self):
        self.filePointer.close()

    def WriteHTML(self, strContent):
        theString = smart_unicode(strContent)
        self.logBuffer += theString #collect all the text
        #self.filePointer.write(theString.encode('iso-8859-1'))
        self.filePointer.write(theString.encode('utf-8', 'replace'))

    def WriteCurrentTime(self):
        self.WriteHTML(self.objDateTimeNow)
        
    def OutputLogs(self):
        strContent = self.logBuffer
        self.logBuffer = '' #clear the log buffer
        return strContent

    #run every X minutes, this assumes cron is run every minute
    #offset - only meaningful if minutes is greater than 1
    def EveryXMinutes(self, minutes, offset=0):
        if minutes == 0:
            return True
        if self.forceRun:
            return True
        if (self.objDateTimeNow.minute + offset) % minutes == 0:
            return True
        else:
            return False
        return False
    
    def WithinXYMinutes(self, minX = 0, minY = 4):
        if self.forceRun:
            return True
        i = self.objDateTimeNow.minute
        if i >= minX and i <= minY:
            return True
        return False
    
    def EveryXHours(self, hours, offset=0):
        if hours == 0:
            return False
        if self.forceRun:
            return True
        if self.objDateTimeNow.minute == 0: # same as "if self.WithinXYMinutes(minY = 0):"
            if (self.objDateTimeNow.hour + offset) % hours == 0:
                return True
            else:
                return False
        return False
