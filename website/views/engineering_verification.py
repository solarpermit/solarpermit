import re
import json
import inspect
import traceback
import importlib

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import lxml.etree
import lxml.builder
import lxml.objectify

import website
from website.views.api2 import parse_api_request, get_prop, get_user,         \
                               get_api_key, get_incorporated, checked_getter, \
                               optional_getter, ValidationError, xml_tostring,\
                               error_response

@csrf_exempt
def verify(request):
    try:
        request_data = parse_verification_request(request.body)
        directives = get_prop(request_data, 'directives')
        user = get_user(directives, 'api_username')
        api_key = get_api_key(directives, 'api_key', user)
        jurisdiction = get_incorporated(directives, 'jurisdiction_id')
        system = get_prop(request_data, 'system')
        ac = get_prop(system, 'ac')
        dc = get_prop(system, 'dc')
        ground = get_prop(system, 'ground')
        code = get_code(jurisdiction, get_override_code(directives, 'override_code'))
        tests = [f[1] for f in inspect.getmembers(code) if inspect.isfunction(f[1])]
        def dotest(f):
            try:
                f(directives=directives, ac=ac, dc=dc, ground=ground)
            except ValidationError as e:
                return (False, f.__name__, e.args[0])
            except Exception:
                return (False, f.__name__, "Unknown error.")
            return (True, f.__name__)
        results = [dotest(f) for f in tests]
    except ValidationError as e:
        return error_response(e)
    except Exception as e:
        return error_response(traceback.print_exc())
    return testcase_response(results=results)

def get_code(jurisdiction, override):
    code_name = override
    if override is None:
        try:
            year = json.loads(jurisdiction.answerreference_set
                                          .filter(question_id = 1,
                                                  approval_status = 'A')
                                          .order_by("-create_datetime")[0]
                                          .value)['value']
            code_name = "nec%s" % year
        except:
            raise ValidationError("No NEC code version for this jurisdiction, use override_code.")
    try:
        mod = importlib.import_module("website.utils.engineering_verification."+ str(code_name))
    except:
        if override is not None:
            raise ValidationError("Invalid override_code.")
        raise ValidationError("This jurisdiction has an invalid or unsupported NEC code version, use override_code.")
    if not inspect.ismodule(mod):
        if override is not None:
            raise ValidationError("Invalid override_code.")
        raise ValidationError("This jurisdiction has an invalid or unsupported NEC code version, use override_code.")
    return mod

@optional_getter
def get_override_code(override):
    return str(override)

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
                definition_id = super(ElectricalElement, self).__getattr__('definition')
                root = [n for n in self.iterancestors()][-1]
                definition = next(r for r in root.iter()
                                  if r.tag == self.tag and \
                                     hasattr(r, 'id') and \
                                     super(ElectricalElement, r).__getattr__('id') == definition_id)
                return definition.specifications
            except Exception as e:
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
