import re
import json
import inspect
import traceback

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import lxml.etree
import lxml.builder
import lxml.objectify

import website
from website.views.api2 import parse_api_request, get_prop, get_user, get_api_key, get_incorporated, checked_getter, ValidationError, xml_tostring, error_response

@csrf_exempt
def verify(request):
    try:
        request_data = parse_api_request(request.body)
        directives = get_prop(request_data, 'directives')
        user = get_user(directives, 'api_username')
        api_key = get_api_key(directives, 'api_key', user)
        jurisdiction = get_incorporated(directives, 'jurisdiction_id')
        code = get_code(directives, 'override_code', jurisdiction)
        system = get_prop(request_data, 'system')
        ac = get_prop(system, 'ac')
        dc = get_prop(system, 'dc')
        ground = get_prop(system, 'ground')
        tests = [f[1] for f in inspect.getmembers(code) if inspect.isfunction(f[1])]
        def dotest(f):
            try:
                f(request_data)
            except ValidationError as e:
                return (False, f.__name__, e.args[0])
            except Exception:
                return (False, f.__name__, "Unknown error.")
            return (True, f.__name__)
        results = [dotest(f) for f in tests]
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        print e
        return error_response(traceback.print_exc())
    return testcase_response(results=results)

@checked_getter
def get_code(override, jurisdiction):
    # TODO: look it up from the jurisdiction
    mod = getattr(website.utils.engineering_verification, str(override))
    return mod if inspect.ismodule(mod) else None

def parse_verification_request(xml_str):
    parser = lxml.etree.XMLParser(remove_blank_text=True)
    lookup = lxml.objectify.ObjectifyElementClassLookup(tree_class=ElectricalElement)
    parser.set_element_class_lookup(lookup)
    try:
        return lxml.objectify.fromstring(xml_str, parser)
    except:
        raise ValidationError("Invalid request.")

class ElectricalElement(lxml.objectify.ObjectifiedElement):
    # if our caller is looking for a specifications node and we don't
    # have one of our own, then find the element indicated by our
    # defintion_id and use its specifications node
    def __getattr__(self, tag):
        try:
            return super(ElectricalElement, self).__getattr__(tag)
        except AttributeError as e:
            if tag != 'specifications':
                raise e
            try:
                parent = self.getparent()
                definition_id = super(ElectricalElement, self).__getattr__('definition')
                root = [n for n in self.iterancestors()][-1]
                definition = next(r for r in root.iter()
                                  if r.tag == self.tag and \
                                     hasattr(r, 'id') and \
                                     super(ElectricalElement, r).__getattr__('id') == definition_id)
                return definition.specifications
            except:
                raise AttributeError

def testcase_response(results=[]):
    E = lxml.builder.ElementMaker()
    status = "success"
    for result in results:
        if not result[0]:
            status = "failure"
            break
    def getnode(result):
        if result[0]:
            return getattr(E, "pass")(E.testcase(result[1]))
        return E.fail(E.testcase(result[1]),
                      E.message(result[2]))
    return HttpResponse(xml_tostring(E.result(E.status(status),
                                              E.results(*[getnode(r) for r in results]))),
                        content_type="application/xml")
