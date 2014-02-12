import django
from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
import json
from itertools import chain
from pprint import pprint

class TestAnswering(TestCase):
    #fixtures = ['questions']
    def setUp(self):
        self.users = [User.objects.create_user("testuser%s" % id, "testuser%s@testing.solarpermit.org" % id, "testuser")
                          for id in xrange(3)]
        self.ahj = [Jurisdiction.objects.create(city = "foo city",
                                                name_for_url = "foo",
                                                description = "foo",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "foo"),
                    Jurisdiction.objects.create(city = "bar city",
                                                name_for_url = "bar",
                                                description = "bar",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "bar")]

    """
    |-----+------+--------+-----------------------------------------------------------------------|
    |  id | type | attach | display_template                                                      |
    |-----+------+--------+-----------------------------------------------------------------------|
    |   1 | T    |      0 | NULL                                                                  |
    |  15 | MF   |      0 | NULL                                                                  |
    |  25 | DD   |      0 | NULL                                                                  |
    |  34 | R    |      0 | NULL                                                                  |
    |  51 | TA   |      0 | NULL                                                                  |
    | 285 | CF   |      0 | NULL                                                                  |
    |   4 | MF   |      0 | address_display.html                                                  |
    |  14 | MF   |      0 | available_url_display.html                                            |
    |  69 | MF   |      0 | fire_setbacks_display.html                                            |
    |  64 | MF   |      0 | homeowner_requirements_display.html                                   |
    |   8 | MF   |      0 | hours_display.html                                                    |
    | 105 | MF   |      1 | inspection_checklists_display.html                                    |
    | 282 | MF   |      1 | online_forms.html                                                     |
    |  16 | MF   |      0 | permit_cost_display.html                                              |
    |   2 | MF   |      0 | phone_display.html                                                    |
    |  97 | MF   |      0 | plan_check_service_type_display.html                                  |
    |  43 | MF   |      0 | radio_allowed_with_exception_display.html                             |
    | 104 | MF   |      0 | radio_available_with_exception_display.html                           |
    | 283 | MF   |      0 | radio_compliant_sb1222_with_exception.html                            |
    |  33 | MF   |      0 | radio_covered_with_exception_display.html                             |
    | 111 | MF   |      0 | radio_has_training_display.html                                       |
    |  81 | MF   |      0 | radio_inspection_approval_copies_display.html                         |
    | 112 | MF   |      0 | radio_licensing_required_display.html                                 |
    |  36 | MF   |      1 | radio_module_drawings_display.html                                    |
    |  22 | MF   |      0 | radio_required_display.html                                           |
    |  17 | MF   |      0 | radio_required_for_page_sizes_display.html                            |
    |  18 | MF   |      0 | radio_required_for_scales_display.html                                |
    |  35 | MF   |      0 | radio_studer_vent_rules_with_exception_display.html                   |
    |   5 | MF   |      0 | radio_submit_PE_stamped_structural_letter_with_exception_display.html |
    |  92 | MF   |      0 | radio_vent_spanning_rules_with_exception_display.html                 |
    |  19 | MF   |      0 | radio_with_exception_display.html                                     |
    |  62 | MF   |      1 | required_spec_sheets_display.html                                     |
    |  85 | MF   |      0 | signed_inspection_approval_delivery_display.html                      |
    |  96 | MF   |      1 | solar_permitting_checklists_display.html                              |
    | 107 | MF   |      0 | time_window_display.html                                              |
    |   9 | MF   |      0 | turn_around_time_display.html                                         |
    |   3 | T    |      0 | url.html                                                              |
    |   6 | MF   |      0 | url.html                                                              |
    |-----+------+--------+-----------------------------------------------------------------------|
    """

    def test_answering(self):
        q1 = Question.objects.get(id=1)
        self.assertIsNotNone(q1)
        self.assertIsNone(q1.display_template)
        (status_code, content) = post(self.client, self.ahj[0], q1,
                                      { 'field_value': 'test answer' })
        self.assertEqual(401, status_code)
        logged_in = self.client.login(username='testuser0',
                                      password='testuser')
        self.assertTrue(logged_in)
        (status_code, content) = post(self.client, self.ahj[0], q1,
                                      { 'field_value': 'test answer' })
        self.assertEqual(200, status_code)
        self.assertTemplateUsed('single_field_display.html')
        self.assertNotEqual(-1, content[0]['val'].find('Test answer')) # capitalization

    def do_answer(self, client, ahj, question, scenario):
        (status, commands) = post(client, ahj, question, scenario)
        self.assertEqual(status, 200)
        self.assertTrue(len(commands) >= 1)
        val = commands[0]["val"]

def post(client, ahj, question, data):
    res = client.post('/jurisdiction/%s/' % ahj.name_for_url,
                      dict(chain(data.iteritems(),
                                 { 'ajax': 'suggestion_submit',
                                   'jurisdiction_id': ahj.id,
                                   'question_id': question.id }.iteritems())))
    return (res.status_code, try_decode(res.content))

def try_decode(content):
    try:
        return json.loads(content)
    except:
        return None
