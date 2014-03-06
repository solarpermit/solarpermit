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
        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=ahj,
                                               question=question,
                                               value='test answer')
                            for ahj in self.ahj for question in self.questions]
        
        
        
#lss; at first it confused me that they used the for loops in this way.#lss; interesting for statement
#thought it would be no different than
# for ahj in self.ahj:
#    for question in self.questions:
#        self.answers = [AnswerReference.objects.create(jurisdiction=ahj, question=question, value='test answer')
# But it actually is, done the way above, it would create a new object for each answer and replace everything thats in there
# Idk if this is a python thing, but i really like it, going to remember it
# tried calling TestVoting.vote()... didnt work because i was calling the class test vote, and vote is not part of the class test vote
# def test_import(self):
# the following is a successful vote, sent to the sample jur in FL. was able to upvote the permiting department name
# first I need to have the django client
# from django.test.client import Client
# c = Client()
# Then i need to make a user, (This made an actual user on the site, not just a test user in a test env)
# User.objects.create_user("testuser00001", "testuser001@testing.solarpermit.org", "testuser")
# WARNING creating a user this way does not invoke UserDetail, and will not allow the user to login on an actual browser. good catch, user detail is need inorder to have a complete test me thinks
# Must be inside a class invoking TestCase in order to use a test env, then call the User to an new object exp: 
# self.user = User.objects.create_user("testuser00001", "testuser001@testing.solarpermit.org", "testuser") for one user, or inside [] for multi users
# to login with a user
# c.login(username='testuser00001',password-'testuser')
# should return True and user should be logged in
# test to make sure user is logged in: 
# logged_in = c.login(username='testuser00001',password-'testuser')
# self.assertTrue(logged_in)
# then you can vote using:
# res = c.post('/jurisdiction/sample-jurisdiction-fl/', {'ajax': 'vote','entity_id': '26473', 'entity_name': 'requirement','vote': 'up', 'confirmed':''})
# this posts to the login page over ajax, and then assigns the response to res.
# res is an object containing res.status_code and res.content
# on the site actual user creation is handled with jquery. static/skins/templates/solarpermit/website/accounts/create_account.js'''