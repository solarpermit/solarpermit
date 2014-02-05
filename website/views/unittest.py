from django.conf import settings
from website.utils.httpUtil import HttpRequestProcessor
from website.tests.model_unit_tests import ModelUnitTests



def run_test(request, test=None):
    requestProcessor = HttpRequestProcessor(request)
    #test = requestProcessor.getParameter('test')
    
    #allow run test only if DEBUG is on
    html = ''
    if settings.DEBUG == True:
        model_unit_tests = ModelUnitTests();
        if test == None:
            html += '<p>Running All Tests</p>'
            try:
                model_unit_tests.runTest() #run all tests
                html += '<p>Test Passed</p>'
            except Exception, e:
                html += '<p>' + str(e) + '</p>'
                html += '<p>Test Failed</p>'
        else:
            html += '<p>Test "' + test + '" not found.</p>'
    else:
        html += '<p>Not in debug mode, cannot run test.</p>'
    
    data = {
            'html': html
            }
    
    return requestProcessor.render_to_response(request, 'website/test/test_result.html', data, '')
