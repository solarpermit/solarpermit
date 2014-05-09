from website.utils.httpUtil import HttpRequestProcessor # decode_jinga_template

def maintenace_mode(request):
    data = {}
    requestProcessor = HttpRequestProcessor(request)
    
    return requestProcessor.render_to_response(request,'maintenance.html', data, '')    