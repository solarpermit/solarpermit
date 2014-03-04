from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
from website.tests.test_voting import vote
import json

'''
Will get 301 status code if no trailing slash is in place.
merge to devel update to fix issue #53
cron_validate_answers

function setup
Create sample jurisdiction
Create sample question for:
        approved with downvotes
        approved without downvotes
        approved with no votes
        approved multi value with downvotes
        approved multi value without downvotes
        rejected with downvotes
        rejected with downvotes and upvotes
        rejected multi value with downvotes
        rejected multi value with downvotes and upvotes
        rejected after already approved?? I don't think i need to test this feature.
        
    create sample answers (multianswer questions will have 3 answers, pending, approved, reject)
    superuser add answer?? waiting for db48x to reply.

function vote
    downvote answer to 2 to reject
    upvote answer to 1 to approve
    downvote answer, upvote to downvote + 1 to approve
    leave answer pending for week to approve

function timepass
    simulate days passing
    call cron script every simulated day.
    assert answered questions against template
    log errors

'''
class TestValidHistory(TestCase):
    def setUp(self):
        self.users = [User.objects.create_user("testuser%s" % id, 
                                               "testuser%s@testing.solarpermit.org" % id,
                                                "testuser")
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


#    tried calling TestVoting.vote()... didnt work because i was calling the class test vote, and vote is not part of the class test vote
#    def test_import(self):
