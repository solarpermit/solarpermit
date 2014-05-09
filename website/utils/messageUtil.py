from website.utils.httpUtil import HttpRequestProcessor
class MessageUtil():
    system_message_key = '' 
    
    
    def __init__(self, system_message_key):
        self.system_message_key = system_message_key
        
    def get_system_message_type(self):
        system_message_conf = self.get_system_message_conf()
        if self.system_message_key in system_message_conf:
            return system_message_conf[self.system_message_key]['system_message_type']  # what returns here is the appropriate suffix for the name of the image to be displayed on the message next to the message itself.
        else:
            return ''
    
    def get_system_message_text(self):
        system_message_conf = self.get_system_message_conf()
        if self.system_message_key in system_message_conf:
            return system_message_conf[self.system_message_key]['system_message_text']
        else:
            return ''
    
    def get_system_message_conf(self):
        system_message_conf = {}
        system_message_conf['success_create_account'] = {}
        system_message_conf['success_create_account']['system_message_type'] = 'success'
        system_message_conf['success_create_account']['system_message_text'] = 'Account created. Thank you for joining the National Solar Permitting Database.'       
        system_message_conf['success_reset_password'] = {}        
        system_message_conf['success_reset_password']['system_message_type'] = 'success'
        system_message_conf['success_reset_password']['system_message_text'] = 'Password has been reset.'   
        system_message_conf['success_create_org'] = {}
        system_message_conf['success_create_org']['system_message_type'] = 'success'
        system_message_conf['success_create_org']['system_message_text'] = 'Organization created.'         
        system_message_conf['notification_setting_updated'] = {}
        system_message_conf['notification_setting_updated']['system_message_type'] = 'success'
        system_message_conf['notification_setting_updated']['system_message_text'] = 'Notification preferences updated.'         
        system_message_conf['join_organization'] = {}
        system_message_conf['join_organization']['system_message_type'] = 'success'
        system_message_conf['join_organization']['system_message_text'] = 'A request to join has been sent to the company or organization administrator..'         
        
        return system_message_conf   
    
def add_system_message(request,system_message_key):
    message_list = request.session.get('message_list', [])
    if message_list ==  None:
        message_list = []
    message_list.append(system_message_key)
    request.session['message_list'] = message_list
    
def get_system_message(request):
    requestProcessor = HttpRequestProcessor(request)
    message_list = request.session.get('message_list', [])
    if message_list == None:
        message_list = []
    message_key = requestProcessor.getParameter('message_key')
    if message_key !=None:
        message_list.append(message_key)
    request.session['message_list'] = None
    
    data = {}
    data['system_message_type'] = ''
    data['system_message_text'] = ''
    if len(message_list) > 0:
        messageUtil = MessageUtil(message_list[0])
        data['system_message_type'] = messageUtil.get_system_message_type()   # optional
        data['system_message_text'] = messageUtil.get_system_message_text() 
    return data
        
        