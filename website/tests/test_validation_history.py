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
      1  approved with downvotes
      2  approved without downvotes
      3  approved with no votes
      4  approved multi value with downvotes
      5  approved multi value without downvotes
      6  rejected with downvotes
      7  rejected with downvotes and upvotes
      8  rejected multi value with downvotes
      9  rejected multi value with downvotes and upvotes
      10 approved by superuser
        rejected after already approved?? I don't think i need to test this feature.
        
    create sample answers (multianswer questions will have 3 answers, pending, approved, reject)
    superuser add answer?? waiting for db48x to reply. yes we are to test this

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
            self.users = [User.objects.create_user("testuser%s" % id, "testuser%s@testing.solarpermit.org" % id, "testuser") for id in xrange(3)]

'''
class TestValidHistory(TestCase):
    def setUp(self):
#create a local users object for testuser1, 2, 3, out of a list build using the Django users model
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
                              for id in xrange(10)]
#lss; at first it confused me that they used the for loops in this way.#lss; interesting for statement
#thought it would be no different than
# for ahj in self.ahj:
#    for question in self.questions:
#        self.answers = [AnswerReference.objects.create(jurisdiction=ahj, question=question, value='test answer')
#But it actually is, done the way above, it would create a new object for each answer and replace everything thats in there
#Idk if this is a python thing, but i really like it, going to remember it

        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=ahj,
                                               question=question,
                                               value='test answer')
                            for ahj in self.ahj for question in self.questions]


#    tried calling TestVoting.vote()... didnt work because i was calling the class test vote, and vote is not part of the class test vote
#    def test_import(self):
