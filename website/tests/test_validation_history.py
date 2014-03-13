from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import User, RatingCategory, ActionCategory, Jurisdiction, Question, AnswerReference
from django.contrib.auth import authenticate
from django.conf import settings
from datetime import timedelta, date
import json
client = Client()
def vote(client, ahj, answer, direction):
    res = client.post('/jurisdiction/%s/' % ahj.name_for_url, #res is response of client
                      { 'ajax': 'vote', #send through ajax
                        'entity_id': answer.id, 
                        'entity_name': 'requirement',
                        'vote': direction, #direction up or down. 
                        'confirmed': '' })
    return (res.status_code, try_decode(res.content)) #return the status code, look for 200, then attempt to decode the content
def try_decode(content):
    try:
        return json.loads(content)
    except:
        return None
def dump(obj):
    for attr in dir(obj):
        if hasattr( obj, attr ):
            print( "obj.%s = %s" % (attr, getattr(obj, attr)))

class TestValidHistory(TestCase):
    def setUp(self):
        #create a local users object for testuser1, 2, 3, out of a list build using the Django users model
        self.users = [User.objects.create_user("testuser%s" % id, 
                                               "testuser%s@testing.solarpermit.org" % id,
                                                "testuser")
                          for id in xrange(10)]

        RatingCategory.objects.create(name='Points',
                                      description='Number of points',
                                      rating_type='N').save()

        ActionCategory.objects.create(name='VoteRequirement',
                                      description='Vote on Requirement',
                                      rating_category_id=1,
                                      points=2).save()

        self.ahj = Jurisdiction.objects.create(city = "foo city",
                                                name_for_url = "foo1",
                                                description = "foo",
                                                state = "CA",
                                                jurisdiction_type = "CI",
                                                name = "foo")
        ## we need 4 questions that have multiple answer possiblites. add to the end? diff object? diff object will be wayyyy easier
        self.questions = [Question.objects.create(label="test%s" % id, question="test%s" % id)
                              for id in xrange(10)]
        self.questionsMulti = [Question.objects.create(label="test%s" % id, question="test%s" % id, has_multivalues = True)
                              for id in xrange(4)]
        
        self.answers = [AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer')
                             for question in self.questions]
        self.answersMulti = [AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer multi')
                             for question in self.questionsMulti] 
        self.answersMulti.extend([AnswerReference.objects
                                       .create(jurisdiction=self.ahj,
                                               question=question,
                                               value='test answer multi 2')
                             for question in self.questionsMulti]) 
## I think this makes an answer for each, need to confirm that it doesnt overwrite its self
## need to add a couple of multi value questions to the answer ref. to do so i need to add some questions to the question object that have has_multivalues = True

        #i altered do_test_vote to not include a test against the response for jurisdiction_id since it doesnt exist.

    def do_test_vote(self, client, ahj, answer, direction, up_votes, down_votes):
        (status, commands) = vote(client, ahj, answer, direction)
        self.assertEqual(status, 200)
        self.assertTrue(len(commands) >= 1)
        val = commands[0]["val"]
        self.assertIn(str(answer.id),
                      val["answers_votes"])
        self.assertEqual(up_votes,
                         val["answers_votes"][str(answer.id)]["total_up_votes"])
        self.assertEqual(down_votes,
                         val["answers_votes"][str(answer.id)]["total_down_votes"])

    def loginUser(self, user): #feed user number
        logged_in = client.login(username='testuser%s' % user,
                            password='testuser')
        self.assertTrue(logged_in)
        
    def upVote(self,up_votes,cur_down,lastUser,answerNum,multi): #number of times to upvote, current amount of down votes, last test user we used, current test number (answer ref), multi is a boolean depicting if we use answers or answersmulti 
        userNum = lastUser + 1
        inc = 0
        cur_up = 0 #current amount of up votes
        self.loginUser(userNum) 
        while inc < up_votes: # while our incrementor is less than our total upvotes,
            if cur_up <= up_votes: # if our current amount of upvotes is less or equal to our max upvote
                cur_up = cur_up + 1 #inc current upvotes
            if multi == False:
                self.do_test_vote( client, self.ahj, self.answers[answerNum], "up", cur_up, cur_down)
            else:
                self.do_test_vote( client, self.ahj, self.answersMulti[answerNum], "up", cur_up, cur_down)
            userNum = userNum + 1
            self.loginUser(userNum)
            inc = inc + 1
        inc = 0 # null out incs

    def downVote(self,down_votes,cur_up,lastUser,answerNum,multi): #number of times to downvote, current amount of up votes, last test user we used, current test number (answer ref), multi is a boolean depicting if we use answers or answersmulti 
        userNum = lastUser + 1
        inc = 0
        cur_down = 0 #current amount of up votes
        self.loginUser(userNum) 
        while inc < down_votes:
            if cur_down <= down_votes:
                cur_down = cur_down + 1           
            if multi == False:
                self.do_test_vote( client, self.ahj, self.answers[answerNum], "down", cur_up, cur_down)
            else:
                self.do_test_vote( client, self.ahj, self.answersMulti[answerNum], "down", cur_up, cur_down)
            userNum = userNum + 1
            self.loginUser(userNum)
            inc = inc + 1
        inc = 0 # null out incs
        

    def test_validate(self):
        
#      test #0 answer#0 Goal: approved with downvotes
        # 3 upvotes, 1 down votes
        self.downVote(1, 0, 0, 0,False)
        self.upVote(3, 1, 1, 0,False)
#      test #1 answer#1  goal approved without downvotes 
        # 3 upvote
        self.upVote(3, 0, 0, 1, False)
#     test #2 answer#2 goal: approved with no votes #over time
        #no votes
        #####just a note that answer 2 lives here 
#      test #3 answer#3  rejected with downvotes
        #downvote 2
        self.downVote(2, 0, 0, 3, False)

#      test #4 answer#4  rejected with downvotes and upvotes
        #upvote 1 downvote 2
        self.upVote(1, 0, 0, 4, False)
        self.downVote(2, 1, 1, 4, False)
#      Test #5 answerMulti#0 & 4  approved multi value with downvotes
        # Test#5 #answer 0: downvote 2
        self.downVote(2, 0, 0, 0, True)
        # Test#5 #answer 1: downvote 1, upvote 3
        self.downVote(1, 0, 0, 4, True)
        self.upVote(3, 1, 1, 4, True)
#      test# 6 answerMulti# 1 & 5 approved multi value without downvotes
        #answer 1: upvote 3
        self.upVote(3, 0, 0, 1, True)
        #answer 5: no votes        
#      test# 7  answerMulti# 2 & 6 rejected multi value with downvotes
        #answer 2 downvote 2
        self.downVote(2, 0, 0, 2, True)
        #answer 6 downvote 2
        self.downVote(2, 0, 0, 6, True)
#      test# 8 answerMulti# 3 & 7  rejected multi value with downvotes and upvotes
        #answer 3 upvote 1 downvote 2
        self.upVote(1, 0, 0, 3, True)
        self.downVote(2, 1, 1, 3, True)
        #answer 7 upvote 1 downvote 2
        self.upVote(1, 0, 0, 7, True)
        self.downVote(2, 1, 1, 7, True)
        
#      11 approved by superuser
        #login as superuser. upvote? approve? need to figure this out.

    def test_timePass(self):
        testTime = date.today()
        diff = datetime.timedelta(days=7)
        futureTime = testTime + diff
        self.cron_validate_answers(futureTime)

              #lss; this is where the cron job is   
    def cron_validate_answers(self, testTime):
        # get all 'pending' answers that is just 2 weeks old
        # today date - create date >= 2 weeks
        # assign approval_status = 'A' - answerreference, action
        today_date = testTime
        user_id = 1 # supposedly the django admin user.
        
        number_days_unchallenged_b4_approved = django_settings.NUM_DAYS_UNCHALLENGED_B4_APPROVED        
        two_weeks_before_today = today_date - timedelta(days=number_days_unchallenged_b4_approved)
        vote_action_category = ActionCategory.objects.filter(name__iexact='VoteRequirement')
        entity_name='Requirement'
        action_obj = Action()
        
        validate_action_category_name = 'ValidateRequirement'
                        
        already_processed_jurisdiction_question = []
        answers = AnswerReference.objects.filter(approval_status__iexact='P', create_datetime__lte=two_weeks_before_today).order_by('jurisdiction__id', 'question__id', 'create_datetime')  
        for answer in answers:
            jurisdiction_question_str = str(answer.jurisdiction.id) + '_'  + str(answer.question.id)
            if jurisdiction_question_str not in already_processed_jurisdiction_question:
                votes = Action.objects.filter(data__iexact='vote: down', entity_name__iexact=entity_name, entity_id=answer.id, action_datetime__gt=answer.create_datetime)
                if len(votes) == 0:
                    answer.approval_status = 'A'
                    answer.status_datetime = datetime.datetime.now()
                    answer.save()
                    already_processed_jurisdiction_question.append(jurisdiction_question_str)       
                    #action
                    data = 'approved - unchallenged for 1 week(s) after creation'
                    aobj = action_obj.save_action(validate_action_category_name, data, answer, entity_name, user_id, answer.jurisdiction)  
                    
                    # cancel all subsequent answers to the same question
                    question = answer.question
                    if question.has_multivalues == 0:
                        answers_to_be_rejected = AnswerReference.objects.filter(question = answer.question, jurisdiction = answer.jurisdiction, approval_status = 'P' )    # reject all other pending answers
                        for answer_to_be_rejected in answers_to_be_rejected:
                            answer_to_be_rejected.approval_status = 'R'
                            answer_to_be_rejected.status_datetime = datetime.datetime.now()
                            answer_to_be_rejected.save()
                        
                            #action
                            data = 'rejected - another answer was approved by the cron job'
                            action_obj.save_action(validate_action_category_name, data, answer_to_be_rejected, entity_name, user_id, answer.jurisdiction)                      

'''
cron_validate_answers
function timepass
    simulate days passing
    call cron script every simulated day.
    assert answered questions against template
    log errors

'''