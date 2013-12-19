import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from website.models import Organization, OrganizationMember, Jurisdiction, Comment, QuestionCategory#, Question, AnswerReference
from website.utils.mathUtil import MathUtil
#from website.utils.contributionHelper import ContributionHelper
#from askbot.conf import settings as askbot_settings
from django.conf import settings as django_settings

# TODO: use django comments / askbot comments / our own?

RATING_TYPE_CHOICES = (
    ('S', 'Numeric Scale'),
    ('L', 'Named Levels'), #like badges
)

class RatingCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    rating_type = models.CharField(choices=RATING_TYPE_CHOICES, max_length=8, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

# level names for the rating categories, like badge names for the badge category
class RatingLevel(models.Model):
    category = models.ForeignKey(RatingCategory, blank=True, null=True, db_index=True)
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    rank = models.PositiveSmallIntegerField(blank=True, null=True, db_index=True) #ranking of the levels, 0 is highest
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class RewardCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'
    
class ActionCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    rating_category = models.ForeignKey(RatingCategory, blank=True, null=True, db_index=True)
    points = models.IntegerField(blank=True, null=True, db_index=True) #number of points for this action, can be negative
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class Action(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    organization = models.ForeignKey(Organization, blank=True, null=True, db_index=True)
    category = models.ForeignKey(ActionCategory, blank=True, null=True, db_index=True)
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True) #jurisdiction this action is for, if any
    question_category = models.ForeignKey(QuestionCategory, blank=True, null=True, db_index=True) #question category if any
    entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #Django entity name, like "AnswerReference"
    entity_id = models.PositiveIntegerField(blank=True, null=True)
    data = models.TextField(blank=True, null=True) #convert all values to text
    scale = models.IntegerField(blank=True, null=True, db_index=True) #overall scale of this action
    level = models.ForeignKey(RatingLevel, blank=True, null=True, db_index=True) #overall level of this action
    action_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #question_type = models.CharField(max_length=16, db_index=True, default='predefined')        # to help identify which question (predefined or custom).  different tables. to avoid collision
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)   
    def __unicode__(self):
        
        output = self.user.username
        if self.category != None:
            output += ', ' + self.category.name
        if self.entity_id != None:
            output += ', ' + str(self.entity_id)
        if self.scale != None:
            output += ', ' + str(self.scale)
        if self.level != None:
            output += ', ' + self.level.name
        
        return output
    class Meta:
        app_label = 'website'
    '''        
    def get_flagged_items(self, entity_name, entity_id):
        if entity_name == 'Requirement':
            action_category_name = 'FlagRequirement'
        action_category_objs = ActionCategory.objects.filter(name__iexact=action_category_name)  
        actions = Action.objects.filter(category__exact=action_category_objs[0], entity_name__iexact=entity_name, entity_id__exact=entity_id)
        
        return actions
    '''    
    def user_name_Label(self):
        return self.user.username        
    '''    
    def get_action(self, action_category, entity_name, entity_id):
        action_category_objs = ActionCategory.objects.filter(name__iexact=action_category)  
        actions = Action.objects.filter(category__exact=action_category_objs, entity_name__iexact=entity_name, entity_id__exact=entity_id)

        if actions:
            action = actions[0]
            return action
        else:
            return False
        
    def get_actioner(self):
        if self != False and self != None:
            if self.user_id != None:
                try:
                    user_obj = User.objects.get(id=self.user_id)
                    user_name = user_obj.username
                except:
                    user_name = ''
            else:
                user_name = ''
        else:
            user_name = ''      
            
        return user_name  
        
    def get_voting_tally(self, category_name, entity_id):
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        positive_count = Action.objects.filter(category__exact=action_category, entity_id__exact=entity_id, data__iexact="Vote: Up").count()
        negative_count = Action.objects.filter(category__exact=action_category, entity_id__exact=entity_id, data__iexact="Vote: Down").count()
        print positive_count
        total_count = Action.objects.filter(category__exact=action_category, entity_id__exact=entity_id).count()
        #print neg_count
        print total_count
        if total_count > 0:
            positive_percentage = float(positive_count) / float(total_count) * float(100)
        else:
            positive_percentage = 0.0
         
        mathUtil_obj = MathUtil()
        positive_percentage = mathUtil_obj.round(positive_percentage) 
        
        vote_info = {}
        vote_info['total_votes'] = total_count
        vote_info['total_pos_votes'] = positive_count
        vote_info['total_neg_vote'] = negative_count
        vote_info['percent_pos'] =  positive_percentage  
        #print positive_percentage
        return vote_info

    def vote(self, eid, vote, user_id, entity_name, jurisdiction_id):
        if entity_name == 'Requirement':
            action_category_name = 'VoteRequirement'
        elif entity_name == 'Callout':
            action_category_name = 'VoteCallout'                  
        elif entity_name == 'Comment':
            action_category_name = 'VoteComment'  
        elif entity_name == 'Info':
            action_category_name = 'VoteInfo'
                
        user_obj = User.objects.get(pk=user_id)
        
        action_category = ActionCategory.objects.filter(name__iexact=action_category_name)  
  
        action_objs = Action.objects.filter(category__exact=action_category[0], entity_id = eid, user__exact=user_obj)

        if action_objs:
            print "updating old vote"           
            action_obj = action_objs[0]
            action_data = "Vote: " + vote.title()
            action_obj.data = str(action_data)
            action_obj.save()
        else:
            print "new vote"            
            action_obj = self.save_action(action_category_name, vote, eid, entity_name, user_id, jurisdiction_id)
            
        print "vote logged"
        rate(action_category_name, entity_name, eid, action_obj, user_id, jurisdiction_id)
        
        return action_obj
    
    def rate(self, action_category_name, entity_name, eid, action_obj, user_id, jurisdiction_id):
        if action_category_name == 'VoteRequirement' or action_category_name == 'VoteCallout'  and action_category_name == 'VoteInfo':
            vote_info = self.get_voting_tally(action_category_name, eid)
            rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
            print "rating = " + str(rating)
            #answer_reference_obj = AnswerReference.objects.get(id=eid)
            current_rating_status = answer_reference_obj.rating_status        
            question = Question.objects.get(id=answer_reference_obj.question_id)
            category = QuestionCategory.objects.get(id=question.category_id)
            entity_category_id = category.id                  
            
            answer_reference_obj.rating = rating
            answer_reference_obj.save()
            print "rating status :: " + answer_reference_obj.rating_status
            
        elif action_category_name == 'VoteComment':
            print "rate_on_comment"
            category_name = 'VoteComment'
            vote_info = self.get_voting_tally(category_name, eid)
            print "vote_info :: " 
            print vote_info
            rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
            print "rating = " + str(rating)
            comment_obj = Comment.objects.get(id=eid)
            print comment_obj
            if (rating < 0): rating = 0
            comment_obj.rating = rating
            comment_obj.save()
            
        return rating          
    '''
    
    
    
    """    
    def rate_on_answer(self, eid, action_id, user_id, jurisdiction_id):
        category_name = 'VoteRequirement'
        vote_info = self.get_voting_tally(category_name, eid)
        rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
        print "rating = " + str(rating)
        answer_reference_obj = AnswerReference.objects.get(id=eid)
        current_rating_status = answer_reference_obj.rating_status
        question = Question.objects.get(id=answer_reference_obj.question_id)
        category = QuestionCategory.objects.get(id=question.category_id)
        entity_category_id = category.id     
        
        action = Action.objects.get(id=action_id)
        data = action.data   

        print 'before setting rating status'
        print 'MIN_RATING_TO_CONFIRM :: ' + str(django_settings.MIN_RATING_TO_CONFIRM)
        print 'NEG_RATING_TO_HIDE :: ' + str(django_settings.NEG_RATING_TO_HIDE)
        
        if rating >= django_settings.MIN_RATING_TO_CONFIRM:
            answer_reference_obj.rating_status = 'C'    #status confirmed
            #if current_rating_status != 'C':
                #reaction_obj.save_reaction('RequirementConfirmed', action_id, data, entity_category_id, user_id, jurisdiction_id )        
        if rating <= django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'D'    #status disputed
            #if current_rating_status != 'D':
                #reaction_obj.save_reaction('RequirementDisputed', action_id, data, entity_category_id, user_id, jurisdiction_id )           
        if rating < django_settings.MIN_RATING_TO_CONFIRM and rating > django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'U'
            #if current_rating_status != 'U':
                #reaction_obj.save_reaction('RequirementDisputed', action_id, data, entity_category_id, user_id, jurisdiction_id )       
                       
        answer_reference_obj.rating = rating
        answer_reference_obj.save()
        print "rating status :: " + answer_reference_obj.rating_status
        return rating
    
    def rate_on_callout(self, eid, action_id, user_id, jurisdiction_id):
        category_name = 'VoteCallout'
        vote_info = self.get_voting_tally(category_name, eid)
        rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
        print "rating = " + str(rating)
        answer_reference_obj = AnswerReference.objects.get(id=eid)
        current_rating_status = answer_reference_obj.rating_status        
        question = Question.objects.get(id=answer_reference_obj.question_id)
        category = QuestionCategory.objects.get(id=question.category_id)
        entity_category_id = category.id
        
        action = Action.objects.get(id=action_id)
        data = action.data           

        print 'before setting rating status'
        print 'MIN_RATING_TO_CONFIRM :: ' + str(django_settings.MIN_RATING_TO_CONFIRM)
        print 'NEG_RATING_TO_HIDE :: ' + str(django_settings.NEG_RATING_TO_HIDE)
        if rating >= django_settings.MIN_RATING_TO_CONFIRM:
            answer_reference_obj.rating_status = 'C'    #status confirmed
            #if current_rating_status != 'C':
                #reaction_obj.save_reaction('CalloutConfirmed', action_id, data, entity_category_id, user_id, jurisdiction_id )             
        if rating <= django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'D'    #status disputed
            #if current_rating_status != 'D':
                #reaction_obj.save_reaction('CalloutDisputed', action_id, data, entity_category_id, user_id, jurisdiction_id )             
        if rating < django_settings.MIN_RATING_TO_CONFIRM and rating > django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'U'
            #if current_rating_status != 'U':
                #reaction_obj.save_reaction('CalloutUnconfirmed', action_id, data, entity_category_id, user_id, jurisdiction_id ) 
                            
        answer_reference_obj.rating = rating
        answer_reference_obj.save()
        print "rating status :: " + answer_reference_obj.rating_status
        return rating   
    
    def rate_on_info(self, eid, action_id, user_id, jurisdiction_id):
        category_name = 'VoteInfo'
        vote_info = self.get_voting_tally(category_name, eid)
        rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
        print "rating = " + str(rating)
        answer_reference_obj = AnswerReference.objects.get(id=eid)
        current_rating_status = answer_reference_obj.rating_status        
        question = Question.objects.get(id=answer_reference_obj.question_id)
        category = QuestionCategory.objects.get(id=question.category_id)
        entity_category_id = category.id       
        
        action = Action.objects.get(id=action_id)
        data = action.data            

        print 'before setting rating status'
        print 'MIN_RATING_TO_CONFIRM :: ' + str(django_settings.MIN_RATING_TO_CONFIRM)
        print 'NEG_RATING_TO_HIDE :: ' + str(django_settings.NEG_RATING_TO_HIDE)
        if rating >= django_settings.MIN_RATING_TO_CONFIRM:
            answer_reference_obj.rating_status = 'C'    #status confirmed
            if current_rating_status != 'C':
                reaction_obj.save_reaction('CalloutConfirmed', action_id, data, entity_category_id, user_id, jurisdiction_id )             
        if rating <= django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'D'    #status disputed
            if current_rating_status != 'D':
                reaction_obj.save_reaction('CalloutDisputed', action_id, data, entity_category_id, user_id, jurisdiction_id )             
        if rating < django_settings.MIN_RATING_TO_CONFIRM and rating > django_settings.NEG_RATING_TO_HIDE:
            answer_reference_obj.rating_status = 'U'
            if current_rating_status != 'U':
                reaction_obj.save_reaction('CalloutUnconfirmed', action_id, data, entity_category_id, user_id, jurisdiction_id ) 
                            
        answer_reference_obj.rating = rating
        answer_reference_obj.save()
        print "rating status :: " + answer_reference_obj.rating_status
        return rating       
    
    def rate_on_comment(self, eid):
        print "rate_on_comment"
        category_name = 'VoteComment'
        vote_info = self.get_voting_tally(category_name, eid)
        print "vote_info :: " 
        print vote_info
        rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
        print "rating = " + str(rating)
        comment_obj = Comment.objects.get(id=eid)
        print comment_obj
        if (rating < 0): rating = 0
        comment_obj.rating = rating
        comment_obj.save()
        return rating        
    """    
    
    '''    
    def check_can_vote_up(self, user, category_name='', entity_id=0):
        print 'check_can_vote_up'
        if user.is_authenticated():   
            user_rep = user.reputation

            if user_rep >= min_rep_to_vote_up:
                print 'get last vote'
                last_vote_obj = self.get_user_last_vote_on_an_item(category_name, entity_id, user.id)
                print last_vote_obj
                if last_vote_obj: 
                    print "last vote :: " + str(last_vote_obj[0].data)
                    if last_vote_obj[0].data == 'Vote: Down':            
                        return 1
                else:
                    return 1
            
        return 0    
    
    def check_can_vote_down(self, user, category_name='', entity_id=0):
        print 'check_can_vote_down'
        if user.is_authenticated():   
            user_rep = user.reputation
            print user_rep
            #min_rep_to_vote_down = askbot_settings.MIN_REP_TO_VOTE_DOWN
            print min_rep_to_vote_down
            if user_rep >= min_rep_to_vote_down:
                print 'get last vote'
                last_vote_obj = self.get_user_last_vote_on_an_item(category_name, entity_id, user.id)
                print last_vote_obj
                if last_vote_obj: 
                    if last_vote_obj[0].data == 'Vote: Up':            
                        return 1
                else:
                    return 1
            
        return 0
    
    def check_can_vote(self, user, category_name):
        can_vote_up = {}
        can_vote_down = {}    
        if user.is_authenticated():   
            user_rep = user.reputation
            #min_rep_to_vote_up = askbot_settings.MIN_REP_TO_VOTE_UP
            #min_rep_to_vote_down = askbot_settings.MIN_REP_TO_VOTE_DOWN
            
            last_vote_objs = self.get_user_last_vote_on_category_items(category_name, user.id)
            for vote_obj in last_vote_objs:
                if user_rep >= min_rep_to_vote_up and vote_obj.data == 'Vote: Down':
                    can_vote_up[vote_obj.entity_id] = 1
                else:
                    can_vote_up[vote_obj.entity_id] = 0
                
                if user_rep >= min_rep_to_vote_down and vote_obj.data == 'Vote: Up':
                    can_vote_down[vote_obj.entity_id] = 1
                else:
                    can_vote_down[vote_obj.entity_id] = 0
            
        return (can_vote_up, can_vote_down)       
    
    def get_user_last_vote_on_an_item(self, category_name, entity_id, user_id):
        user_obj = User.objects.get(pk=user_id)   
        print user_obj
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        print action_category
        vote_objs = Action.objects.filter(category__exact=action_category, entity_id__exact=entity_id, user__exact=user_obj).order_by('action_datetime')

        return vote_objs;
    
    def get_user_last_vote_on_category_items(self, category_name, user_id):
        user_obj = User.objects.get(pk=user_id)   
        action_category = ActionCategory.objects.filter(name__iexact=category_name)
        vote_objs = Action.objects.filter(category__exact=action_category, user__exact=user_obj)
        
        return vote_objs      
    '''
    def save_action(self, action_category_name, data, entity, entity_name, user_id, jurisdiction ):
       
        action_category = ActionCategory.objects.filter(name__iexact=action_category_name)
        if action_category_name == "FlagComment":           #ok
            action_data = "Report: " + data
        elif action_category_name == "FlagRequirement":     #ok
            action_data = "Report: " + data 
            
        elif action_category_name == "CommentComment":      #ok
            action_data = "Comment: " + data
        elif action_category_name == "CommentRequirement":  #ok
            action_data = "Comment: " + data       
            
        elif action_category_name == "AddRequirement":
            action_data = "Answer: " + data     
        elif action_category_name == "UpdateRequirement":
            action_data = "Answer: " + data     
                                            
        elif action_category_name == "VoteRequirement":
            action_data = "Vote: " + data.title() 
            
        elif action_category_name == "ValidateRequirement":     #ok
            action_data = data 
            
        elif action_category_name == "VoteComment":
            action_data = "Vote: " + data.title() 
        else:
            action_data = data
         
        #print "1"    
        if entity_name == 'Requirement':
            #print 'entity id :: ' + str(entity_id)
            #entity = AnswerReference.objects.get(id=entity.id)
            #print 'question id :: ' + str(entity.question_id)
            #question = Question.objects.get(id=entity.question_id)
            #print 'question category id :: ' + str(question.category_id) 
            entity_category_id = entity.question.category.id    
            organization = entity.organization
            #print entity.id
            #print organization.id
        else:
            entity_category_id = 0 # not sure here.  will need to figure out entity_category for comment and other non-requirement and non-callout entity
        #print "2"    
        
        if organization != None:    
            action_obj = Action.objects.create(category_id=action_category[0].id, entity_id=entity.id, data=action_data, entity_name=entity_name, user_id=user_id, scale=action_category[0].points, jurisdiction_id=jurisdiction.id, question_category_id=entity_category_id, organization_id=organization.id)
        else:
            action_obj = Action.objects.create(category_id=action_category[0].id, entity_id=entity.id, data=action_data, entity_name=entity_name, user_id=user_id, scale=action_category[0].points, jurisdiction_id=jurisdiction.id, question_category_id=entity_category_id)
            
        #print "track contribution :: "
        #jurisdiction_contributor_obj = JurisdictionContributor()
        #jurisdiction_contributor_obj.track_contributions(action_obj.scale, jurisdiction, entity.question.category, user_id)
        #print "3"
        return action_obj
    
class ReactionCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    rating_category = models.ForeignKey(RatingCategory, blank=True, null=True, db_index=True)
    points = models.IntegerField(blank=True, null=True, db_index=True) #number of points for this reaction, can be negative
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class Reaction(models.Model):
    action = models.ForeignKey(Action, blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, blank=True, null=True, db_index=True) #user who had the reaction, None if it is caused by multiple users, like voted down an item
    category = models.ForeignKey(ReactionCategory, blank=True, null=True, db_index=True)
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True) #jurisdiction this action is for, if any
    question_category = models.ForeignKey(QuestionCategory, blank=True, null=True, db_index=True) #question category if any
    data = models.TextField(blank=True, null=True) #convert all values to text
    scale = models.IntegerField(blank=True, null=True, db_index=True) #scale given by the reactor
    level = models.ForeignKey(RatingLevel, blank=True, null=True, db_index=True) #level given by the reactor
    reaction_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        output = self.user.username
        if self.scale != None:
            output += ', ' + str(self.scale)
        if self.level != None:
            output += ', ' + self.level.name
        return output
    class Meta:
        app_label = 'website'
        
    def save_reaction(self, reaction_category_name, action_obj, entity_category_id, user_id, jurisdiction_id ):
       
        reaction_category = ReactionCategory.objects.filter(name__iexact=reaction_category_name)

     
        #print action_data                   
        reaction_obj = Reaction.objects.create(category_id=reaction_category[0].id, action_id=action_obj.id, data=action_obj.data, user_id=user_id, scale=reaction_category[0].points, jurisdiction_id=jurisdiction_id, question_category_id=entity_category_id)
        #contributionHelper = ContributionHelper()
        #contributionHelper.track_contributions(reaction_category[0].points, jurisdiction_id, entity_category_id, user_id)        

#user's overall rating
class UserRating(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    category = models.ForeignKey(RatingCategory, blank=True, null=True, db_index=True)
    scale = models.IntegerField(blank=True, null=True, db_index=True) #overall scale of this user
    level = models.ForeignKey(RatingLevel, blank=True, null=True, db_index=True) #overall level of this user
    updated_datetime = models.DateTimeField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        output = self.user.username
        if self.scale != None:
            output += ', ' + str(self.scale)
        if self.level != None:
            output += ', ' + self.level.name
        return output
    class Meta:
        app_label = 'website'
    
#organization's overall rating
class OrganizationRating(models.Model):
    organization = models.ForeignKey(Organization, blank=True, null=True, db_index=True)
    category = models.ForeignKey(RatingCategory, blank=True, null=True, db_index=True)
    scale = models.IntegerField(blank=True, null=True, db_index=True) #overall scale of this org
    level = models.ForeignKey(RatingLevel, blank=True, null=True, db_index=True) #overall level of this org
    updated_datetime = models.DateTimeField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        output = self.organization.name
        if self.scale != None:
            output += ', ' + str(self.scale)
        if self.level != None:
            output += ', ' + self.level.name
        return output
    class Meta:
        app_label = 'website'

#to support things like most popular jurisdictions in the last 7 days
class JurisdictionRating(models.Model):
    RATING_TYPE_CHOICES = (
        ('V', 'Views - unique views'),
    )
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    rating_type = models.CharField(choices=RATING_TYPE_CHOICES, max_length=8, blank=True, null=True)
    rank = models.IntegerField(blank=True, null=True) #starting from 1, top
    value = models.CharField(max_length=255, blank=True, null=True) #like number of unique views
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    
    @staticmethod
    def recently_updated(): #list of jurisdictions recently updated, limited to last 7 days, up to 10
        #
        # we really just want the last 10 jurisdictions updated...
        #
        # let's refactor this code from 19 lines to 4
        #
        '''
        jurisdiction_ids = {}
        jurisdictions = []
        today = datetime.datetime.now()
        d = datetime.timedelta(days=-8)
        start_date = today + d
        excluded_jurs = Jurisdiction.objects.filter(id__in=django_settings.SAMPLE_JURISDICTIONS)
        actions = Action.objects.filter(action_datetime__gt=start_date).exclude(jurisdiction__in=excluded_jurs).order_by('-action_datetime')
        for action in actions:
            try:
                jurisdiction_ids[action.jurisdiction.id]
            except:
                jurisdiction_ids[action.jurisdiction.id] = True
        count = 0
        for id in jurisdiction_ids:
            jurisdiction = Jurisdiction.objects.get(id=id)
            jurisdictions.append(jurisdiction)
            count += 1
            if count >= 10:
                break
        '''
        
        # take advantage of lazy querysets and do it smartly
        jurisdictions = Jurisdiction.objects.filter(last_contributed_by__gt=0)
        for sample in django_settings.SAMPLE_JURISDICTIONS:
            jurisdictions = jurisdictions.exclude(id=sample)
        jurisdictions = jurisdictions.order_by('-last_contributed')[:10]
        
        return jurisdictions
        
    @staticmethod
    def most_popular(): #list of jurisdictions with most unique user views, limited to last 7 days, up to 10
        #this assumes cron for "manage.py most_popular" has been run daily
        jurisdictions = []
        excluded_jurs = Jurisdiction.objects.filter(id__in=django_settings.SAMPLE_JURISDICTIONS)        
        jurisdiction_ratings = JurisdictionRating.objects.filter(rating_type='V').exclude(jurisdiction__in=excluded_jurs).order_by('rank')
        for jurisdiction_rating in jurisdiction_ratings:
            jurisdictions.append(jurisdiction_rating.jurisdiction)
        return jurisdictions
 
class JurisdictionContributor(models.Model):
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    question_category = models.ForeignKey(QuestionCategory, blank=True, null=True, db_index=True) #if null, it is for the overall jurisdiction
    organization = models.ForeignKey(Organization, blank=True, null=True, db_index=True) #if not null, it is an org's ranking
    user = models.ForeignKey(User, blank=True, null=True, db_index=True) #if not null, it is a user's ranking
    points = models.IntegerField(blank=True, null=True) #number of points earned
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
        
        
    def get_org_entity_contributors(self, jurisdiction, entity_category, top=3):
                
        if top > 0:
            orgContributors = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, question_category__exact=entity_category, user__isnull=True).order_by('-points')[0:top]
        else:
            orgContributors = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, question_category__exact=entity_category, user__isnull=True).order_by('-points')

        return orgContributors
    
    
    def track_contributions(self, points, jurisdiction, entity_category, user_id):      #entity_category = question_category 
        #jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)
        #question_category = QuestionCategory.objects.get(id=entity_category_id)         
  
        # get org from user
        

        user = User.objects.get(id=user_id)
       
        rating_category_objs = RatingCategory.objects.filter(name__iexact='Points')
        rating_category_obj = rating_category_objs[0]
                
      
        # maintain user rating      
        user_rating_objs = UserRating.objects.filter(user__exact=user, category__exact=rating_category_obj)
        if user_rating_objs:
            user_rating_obj = user_rating_objs[0]
            user_rating_obj.scale = user_rating_obj.scale + points
            user_rating_obj.save()
        else:
            UserRating.objects.create(user_id=user_id, category_id=rating_category_obj.id, scale=points)     
                
                 
        # maintain User Contribution
        user_contributor_objs = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, question_category__exact=entity_category, user__exact=user)
        if user_contributor_objs:
            user_contributor_obj = user_contributor_objs[0]
            user_contributor_obj.points = user_contributor_obj.points + points
            user_contributor_obj.save()
        else:
            JurisdictionContributor.objects.create(jurisdiction_id=jurisdiction.id, question_category_id=entity_category.id, user_id=user_id, points=points)
                                       
                          
        if True:
            if True:
                org_members = OrganizationMember.objects.filter(user__exact=user, organization__status='A').distinct()
                
              
                # maintain org rating
                if org_members:
                    
                    for org_member in org_members:
                        #organization_id = org_id[0]
                
                        org = Organization.objects.get(id=org_member.organization_id)
                        
                        org_rating_objs = OrganizationRating.objects.filter(organization__exact=org, category__exact=rating_category_obj)
                       
                        if org_rating_objs:
                           
                            org_rating_obj = org_rating_objs[0]
                            org_rating_obj.scale = org_rating_obj.scale + points
                            org_rating_obj.save()
                        else:
                      
                            OrganizationRating.objects.create(organization_id=org.id, category_id=rating_category_obj.id, scale=points) 
                            
    

                # maintain Org Contribution
                if org_members:
                    for org_member in org_members:        
                        #organization_id = org_id[0]
                        org = Organization.objects.get(id=org_member.organization_id)
                        org_contributor_objs = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, question_category__exact=entity_category, organization__exact=org)
                        if org_contributor_objs:
                            org_contributor_obj = org_contributor_objs[0]
                            org_contributor_obj.points = org_contributor_obj.points + points
                            org_contributor_obj.save()
                        else:
                            JurisdictionContributor.objects.create(jurisdiction_id=jurisdiction.id, question_category_id=entity_category.id, organization_id=org.id, points=points) 
                    
 
                # maintain org contribution per jurisdiction
                if org_members:
                    for org_member in org_members:     
                        #organization_id = org_id[0]
                        org = Organization.objects.get(id=org_member.organization_id)                                  
                        jur_org_contributor_objs = JurisdictionContributor.objects.filter(jurisdiction__exact=jurisdiction, organization__exact=org, question_category__isnull=True, user__isnull=True)
                        if jur_org_contributor_objs:
                            jur_org_contributor_obj = jur_org_contributor_objs[0]
                            jur_org_contributor_obj.points = jur_org_contributor_obj.points + points
                            jur_org_contributor_obj.save()
                        else:
                            JurisdictionContributor.objects.create(jurisdiction_id=jurisdiction.id, organization_id=org.id, points=points)                                                   
                
      
            
        return True
    
    

# Track the viewing of the entity by unique users (like for most popular jurisdiction)
class EntityView(models.Model):
    entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #like 'Jurisdiction'
    entity_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    session_key = models.CharField(max_length=40, blank=True, null=True, db_index=True) #from django session
    latest_datetime = models.DateTimeField(blank=True, null=True) #last time it was viewed
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
        
    def track_unique_view(self, entity_name, entity_id, user_id, session_key):
        unique_view = True
        if user_id != 0:    # login
            user_obj = User.objects.get(id=user_id)
            entity_view_objs = EntityView.objects.filter(entity_name__iexact=entity_name, entity_id__exact=entity_id, user__exact=user_obj)
            if entity_view_objs:
              
                unique_view = False
                entity_view_obj = entity_view_objs[0]
                entity_view_obj.session_key = session_key
                entity_view_obj.latest_datetime = datetime.datetime.now()
                entity_view_obj.save()
            else:
                # check if this is the case where the user did not log at first, view the page, then logged in. check the session.
                entity_view_objs = EntityView.objects.filter(entity_name__iexact=entity_name, entity_id__exact=entity_id, session_key__exact=session_key)
                if entity_view_objs:
             
                    unique_view = False                    
                    entity_view_obj = entity_view_objs[0]
                    entity_view_obj.user_id = user_id
                    entity_view_obj.latest_datetime = datetime.datetime.now()
                    entity_view_obj.save()                    
                else:
                    EntityView.objects.create(entity_name=entity_name, entity_id=entity_id, user_id=user_id, session_key=session_key, latest_datetime=datetime.datetime.now())
        else:               # not logged in
            entity_view_objs = EntityView.objects.filter(entity_name__iexact=entity_name, entity_id__exact=entity_id, session_key__exact=session_key)
            if entity_view_objs:
              
                unique_view = False
                entity_view_obj = entity_view_objs[0]
                entity_view_obj.latest_datetime = datetime.datetime.now()
                entity_view_obj.save()                
            else:
                EntityView.objects.create(entity_name=entity_name, entity_id=entity_id, session_key=session_key, latest_datetime=datetime.now())
                
                
        return unique_view;
            
# The total unique views for the entity
class EntityViewCount(models.Model):
    entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #like 'Jurisdiction'
    entity_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    total_count = models.PositiveIntegerField(blank=True, null=True, db_index=True) #counting of total UniqueEntityView for the entity
    count_30_days = models.PositiveIntegerField(blank=True, null=True, db_index=True) #last 30 day total count
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    
    
    