import os
from datetime import *
from django.utils.encoding import smart_unicode 
from django.conf import settings

class LogHelper():
    file_name = ''
    file_pointer = None
    log_buffer = '' #all the text from write, to be shown on the page
    
    def __init__(self, sub_dir, short_name):   
        objDateTimeNow = datetime.now()
        year = str(objDateTimeNow.year)
        month = str(objDateTimeNow.month)
        day = str(objDateTimeNow.day)
        hour = str(objDateTimeNow.hour)
        minute = str(objDateTimeNow.minute)
        if len(month) == 1:
            month = '0' + month
        if len(day) == 1:
            day = '0' + day
        if len(hour) == 1:
            hour = '0' + hour
        if len(minute) == 1:
            minute = '0' + minute
            
        strLogPath = settings.LOG_ROOT
        if not '/' == strLogPath[-1]:
            strLogPath += '/'
        strLogPath += sub_dir+'/'
        if not os.path.isdir(strLogPath):
            os.mkdir(strLogPath)
        self.file_name = strLogPath + short_name + year + month + day + '.html'
        self.file_pointer = file(self.file_name, 'a')
          
    def __del__(self):
        self.file_pointer.close()
    
    #write only to log, not in buffer
    def write_log(self, content):
        the_string = smart_unicode(content+'<br>\r')
        self.file_pointer.write(the_string.encode('utf-8', 'replace'))
    
    #write to log and buffer
    def write_all(self, content):
        the_string = smart_unicode(content+'<br>\r')
        self.log_buffer += the_string #collect all the text
        self.file_pointer.write(the_string.encode('utf-8', 'replace'))
    
    #write header to file with latest time
    def write_header(self):
        objDateTimeNow = datetime.now()
        self.log_buffer += 'Started_____________'+objDateTimeNow.isoformat()+'_____________<br>\r'
        self.file_pointer.write('<br>\r<br>\r')
        self.file_pointer.write('Started________________________'+objDateTimeNow.isoformat()+'________________________<br>\r<br>\r')
    
    def write_footer(self):
        objDateTimeNow = datetime.now()
        self.log_buffer += 'Ended_____________'+objDateTimeNow.isoformat()+'_____________<br>\r'
        self.file_pointer.write('<br>\r')
        self.file_pointer.write(objDateTimeNow.isoformat()+'<br>\r')
        self.file_pointer.write('Ended________________________'+objDateTimeNow.isoformat()+'________________________<br>\r<br>\r')
