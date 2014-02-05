from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
import json

class TestVoting(TestCase):
    def setUp(self):
        self.users = [User.objects.create_user("testuser%s" % id, "testuser%s@testing.solarpermit.org" % id, "testuser")
                          for id in xrange(3)]
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
        for ahj in self.ahj:
            ahj.delete()
        for question in self.questions:
            question.delete()
        for answer in self.answers:
            answer.delete()

    def test_voting(self):
        client = Client()
        # must not be able to vote while unauthorized
        (status, commands) = vote(client, self.ahj[0], self.questions[0], 'up')
        self.assertEqual(status, 200)
        self.assertIs(None, commands)

        # but once authenticated...
        logged_in = client.login(username='testuser0',
                                 password='testuser')
        self.assertTrue(logged_in)

        # must be able to vote up
        self.do_test_vote(client, self.ahj[0], self.answers[0], 'up', 1, 0)
        # but not more than once
        self.do_test_vote(client, self.ahj[0], self.answers[0], 'up', 1, 0)

        # must be able to vote down
        self.do_test_vote(client, self.ahj[1], self.answers[1], 'down', 0, 1)
        # but not more than once
        self.do_test_vote(client, self.ahj[1], self.answers[1], 'down', 0, 1)

        # votes from other users add up
        logged_in = client.login(username='testuser1',
                                 password='testuser')
        self.assertTrue(logged_in)
        self.do_test_vote(client, self.ahj[0], self.answers[0], 'down', 1, 1)
        self.do_test_vote(client, self.ahj[1], self.answers[1], 'up', 1, 1)

        ## votes from other users add up
        logged_in = client.login(username='testuser2',
                                 password='testuser')
        self.assertTrue(logged_in)
        self.do_test_vote(client, self.ahj[0], self.answers[0], 'up', 2, 1)
        self.do_test_vote(client, self.ahj[1], self.answers[1], 'down', 1, 2)

        ## votes on one question don't get counted for others
        self.do_test_vote(client, self.ahj[0], self.answers[2], 'up', 1, 0)
        self.do_test_vote(client, self.ahj[1], self.answers[3], 'down', 0, 1)

    def do_test_vote(self, client, ahj, answer, direction, up_votes, down_votes):
        (status, commands) = vote(client, ahj, answer, direction)
        self.assertEqual(status, 200)
        self.assertTrue(len(commands) >= 1)
        val = commands[0]["val"]
        self.assertIn(str(answer.id),
                      val["answers_votes"])
        self.assertEqual(ahj.id,
                         val["jurisdiction_id"])
        self.assertEqual(up_votes,
                         val["answers_votes"][str(answer.id)]["total_up_votes"])
        self.assertEqual(down_votes,
                         val["answers_votes"][str(answer.id)]["total_down_votes"])

def vote(client, ahj, answer, direction):
    res = client.post('/jurisdiction/%s/' % ahj.name_for_url,
                      { 'ajax': 'vote',
                        'entity_id': answer.id,
                        'entity_name': 'requirement',
                        'vote': direction,
                        'confirmed': '' })
    return (res.status_code, try_decode(res.content))

def try_decode(content):
    try:
        return json.loads(content)
    except:
        return None
