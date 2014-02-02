from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, UserDetail, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
import json

class TestFavoritesAndQuirks(TestCase):
    def setUp(self):
        self.users = [User.objects.create_user("testuser%s" % id, "testuser%s@testing.solarpermit.org" % id, "testuser")
                          for id in xrange(3)]
        self.userdetails = [UserDetail.objects.create(user=u) for u in self.users]
        RatingCategory.objects.create(name='Points',
                                      description='Number of points',
                                      rating_type='N').save()
        ActionCategory.objects.create(name='VoteRequirement',
                                      description='Vote on Requirement',
                                      rating_category_id=1,
                                      points=2).save()
        self.ahj = [Jurisdiction.objects.create(city = "foo city",
                                                name_for_url = "foo1",
                                                description = "foo",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "foo"),
                    Jurisdiction.objects.create(city = "foo city",
                                                name_for_url = "foo2",
                                                description = "foo",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "foo")]
        self.questions = [Question.objects.create(label="test%s" % id, question="test%s" % id)
                              for id in xrange(2)]
        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=ahj,
                                               question=question,
                                               value='test answer')
                            for ahj in self.ahj for question in self.questions]

    def tearDown(self):
        for user in self.users:
            user.delete()
        for detail in self.userdetails:
            detail.delete()
        for ahj in self.ahj:
            ahj.delete()
        for question in self.questions:
            question.delete()
        for answer in self.answers:
            answer.delete()

    def test_favorites(self):
        client = Client()

        # shouldn't work when we're not logged in
        (status, content) = add_to_favorites(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual(None, content)

        # but once authenticated...
        logged_in = client.login(username='testuser0',
                                 password='testuser')
        self.assertTrue(logged_in)

        # then it should work
        (status, content) = add_to_favorites(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#favfieldscount", content[0]['id'])
        self.assertEqual('1', content[0]['val'])

        # but not twice
        (status, content) = add_to_favorites(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#favfieldscount", content[0]['id'])
        self.assertEqual('1', content[0]['val'])

        # removing them should work
        (status, content) = remove_from_favorites(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#favfieldscount", content[0]['id'])
        self.assertEqual('0', content[0]['val'])

        # but twice should do no harm
        (status, content) = remove_from_favorites(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#favfieldscount", content[0]['id'])
        self.assertEqual('0', content[0]['val'])

    def test_quirks(self):
        client = Client()

        # shouldn't work when we're not logged in
        (status, content) = add_to_quirks(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual(None, content)

        # but once authenticated...
        logged_in = client.login(username='testuser0',
                                 password='testuser')
        self.assertTrue(logged_in)

        # then it should work
        (status, content) = add_to_quirks(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#quirkcount", content[0]['id'])
        self.assertEqual('1', content[0]['val'])

        # but not twice
        (status, content) = add_to_quirks(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#quirkcount", content[0]['id'])
        self.assertEqual('1', content[0]['val'])

        # removing them should work
        (status, content) = remove_from_quirks(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#quirkcount", content[0]['id'])
        self.assertEqual('0', content[0]['val'])

        # but twice should do no harm
        (status, content) = remove_from_quirks(client, self.ahj[0], self.questions[0])
        self.assertEqual(200, status)
        self.assertEqual("as", content[0]['cmd'])
        self.assertEqual("#quirkcount", content[0]['id'])
        self.assertEqual('0', content[0]['val'])

def add_to_favorites(client, ahj, question):
    return add_to_view(client, ahj, question, 'favorites')
def remove_from_favorites(client, ahj, question):
    return remove_from_view(client, ahj, question, 'favorites')

def add_to_quirks(client, ahj, question):
    return add_to_view(client, ahj, question, 'quirks')
def remove_from_quirks(client, ahj, question):
    return remove_from_view(client, ahj, question, 'quirks')

def add_to_view(client, ahj, question, view_name):
    return edit_view(client, 'add_to_views', ahj, question, view_name)
def remove_from_view(client, ahj, question, view_name):
    return edit_view(client, 'remove_from_views', ahj, question, view_name)

def edit_view(client, ajax, ahj, question, view_name):
    res = client.post('/jurisdiction/%s/' % ahj.name_for_url,
                      { 'ajax': ajax,
                        'jurisdiction_id': ahj.id,
                        'question_id': question.id,
                        'entity_name': view_name })
    return (res.status_code, try_decode(res.content))

def try_decode(content):
    try:
        return json.loads(content)
    except:
        return None
