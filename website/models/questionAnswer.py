import datetime
from django.db import models
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.conf import settings
from website.models import Jurisdiction, OrganizationMember, Organization#, JurisdictionContributor
import json
from django.core import serializers
from website.utils.mathUtil import MathUtil
from website.utils.datetimeUtil import DatetimeHelper
#from django.db.models import Count, Sum
import datetime

class Template(models.Model):
    TEMPLATE_TYPE_CHOICES = (
        ('CT', 'Callouts Template'), #there's only one callouts template in the system, for all jurisdictions
        ('RT', 'Requirements Template'),
        ('IT', 'Information Template'), #for jurisdiction's general info
        ('AT', 'Application Template'),
        #('JR', 'Jurisdiction Requirements'), #jurisdiction no longer has requirement templates
        ('JA', 'Jurisdiction Application'),
        ('CF', 'Jurisdiction Custom Field'),        
    )
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    template_type = models.CharField(choices=TEMPLATE_TYPE_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="")
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    reviewed = models.BooleanField(default=False, db_index=True)
    accepted = models.BooleanField(default=False, db_index=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'
        
    def get_jurisdiction_question_templates(self, jurisdiction):
        templates = Template.objects.filter(template_type__exact='RT')
        custom_templates = Template.objects.filter(template_type__exact='CF', jurisdiction = jurisdiction)
        
        jurisdiction_templates = []
        for template in templates:
            jurisdiction_templates.append(template.id)
            
        for template in custom_templates:
            jurisdiction_templates.append(template.id)   
            
        return jurisdiction_templates          

FORM_TYPE_CHOICES = (
    ('N', 'Number'),
    ('D', 'Date'),
    ('TI', 'Time'),
    ('C', 'Currency'),
    ('TE', 'Text'),
    ('TA', 'Text Area'),
    ('R', 'Radio Button'),
    ('DD', 'Dropdown'),
    ('AC', 'Auto Complete'),
    ('F', 'File Upload'),
    ('CF', 'Custom Field'),
    ('MF', 'Multiple Field'),    
)

class AnswerChoiceGroup(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class AnswerChoice(models.Model):
    answer_choice_group = models.ForeignKey(AnswerChoiceGroup, db_index=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'

class QuestionCategory(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.name
    
    def questionsNumber(self):
        questions = Question.objects.filter(category = self)
  
        return len(questions)
    class Meta:
        app_label = 'website'

#certain criteria that determines if an item is applicable or not
class Applicability(models.Model):
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'
    
        
class Question(models.Model):
    category = models.ForeignKey(QuestionCategory, blank=True, null=True, db_index=True)
    label = models.TextField(blank=True, null=True) #label to display if it is shown in field format
    question = models.TextField(blank=True, null=True) #question to display if it is show as a question
    instruction = models.TextField(blank=True, null=True)
    category = models.ForeignKey(QuestionCategory, blank=True, null=True, db_index=True)
    applicability = models.ForeignKey(Applicability, blank=True, null=True)
    form_type = models.CharField(choices=FORM_TYPE_CHOICES, max_length=8, blank=True, null=True)
    answer_choice_group = models.ForeignKey(AnswerChoiceGroup, blank=True, null=True)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True) #display order within the category
    default_value = models.TextField(blank=True, null=True) #in JSON format
    reviewed = models.BooleanField(default=False, db_index=True)
    accepted = models.BooleanField(default=False, db_index=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    template = models.TextField(blank=True, null=True)
    validation_class = models.TextField(blank=True, null=True)
    js = models.TextField(blank=True, null=True)
    field_attributes = models.TextField(blank=True, null=True)
    terminology = models.TextField(blank=True, null=True)
    has_multivalues = models.BooleanField(default=False) 
    qtemplate = models.ForeignKey(Template, null=True, db_index=True)  
    display_template = models.TextField(blank=True, null=True)    
    field_suffix = models.CharField(max_length=32, blank=True, null=True)
    migration_type = models.CharField(max_length=64, blank=True, null=True) #type of migration that's needed to convert the answer
    creator = models.ForeignKey(User, blank=True, null=True)
    state_exclusive = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    support_attachments = models.BooleanField(default=False) # 1 to support file upload    
        
    def __unicode__(self):
        if self.question != None:
            return self.question[:64] + '...'
        else:
            return str(self.id)
    class Meta:
        app_label = 'website'
        
    def get_addresses_for_map(self, jurisdiction):
        answers = AnswerReference.objects.filter(question=self, jurisdiction=jurisdiction, approval_status__exact='A').order_by('-status_datetime')
        if answers != None and len(answers) > 0:
            answer = answers[0] # only one approved
            answer_value = json.loads(answer.value)    
            str_addr = jurisdiction.get_formatted_jurisdiction_address(answer_value)  
        else:
            if jurisdiction.jurisdiction_type == 'CI':
                if jurisdiction.county == None:
                    str_addr = jurisdiction.city + ', ' + jurisdiction.state
                else:
                    str_addr = jurisdiction.city + ', ' + jurisdiction.county
            elif jurisdiction.jurisdiction_type == 'CO':
                str_addr = jurisdiction.county + ' county, ' + jurisdiction.state
            else:
                str_addr = ''  
                
        return str_addr          
        
    def get_field_label(self, jurisdiction):
        if self.label != None and self.label != '':      
            #if self.id == 6:
            #   question_label = "Utility companies associated with [AHJ name]"
            
            question_label = self.label.replace('[AHJ name]', jurisdiction.name.title())
        else:
            question_label = self.question
            
        return question_label
 
                    
    def get_terminology(self):
        if self.terminology == None or self.terminology == '':
            question_terminology = 'value'
        else:
            question_terminology = self.terminology
            
        return question_terminology     
    
    def get_question_terminology(self, question_id):
        question = Question.objects.get(id=question_id)
        if question.terminology == None or question.terminology == '':
            question_terminology = 'value'
        else:
            question_terminology = question.terminology
            
        return question_terminology                    
        
    def migrate_temmplatequestion_to_question(self):
        template_questions = TemplateQuestion.objects.all()
        for template_question in template_questions:

            try:
                question = Question.objects.get(id=template_question.question_id)
             
                question.qtemplate_id = template_question.template_id
              
                question.save()
               
            except:
                print "no question for id = " + str(template_question.question_id)
        
    def get_custom_fields_by_jurisdiction_by_category(self, jurisdiction_obj, category_id):
        questions = [] #if this is none, will cause template loop to crash!!!
        templates = Template.objects.filter(template_type__iexact='CF', jurisdiction=jurisdiction_obj)
        
        if len(templates) > 0:
            #obj = objs[0]
            '''
            question_ids = TemplateQuestion.objects.filter(template=obj).values_list('question_id')
            if len(question_ids) > 0:
                category_obj = QuestionCategory.objects.get(id=category_id)
                questions = Question.objects.filter(id__in=question_ids, category=category_obj)
            '''    
            category_obj = QuestionCategory.objects.get(id=category_id)   
            #questions = Question.objects.filter(id__in=all_template_question_ids, category__exact=category_obj, accepted__exact=1).exclude(form_type__iexact='CF').order_by('display_order')
            questions = Question.objects.filter(qtemplate__in=templates, category__exact=category_obj, accepted__exact=1).order_by('display_order')
                           
           
        return questions
            
    def get_org_question_categories(self):
        wanted_categories = ('Jurisdiction Informations', 'Organization Contact Information')
        template = 'IT'
                
        found_categories = []
        template_objs = Template.objects.filter(template_type__iexact=template)
        categories = self.get_categories_of_questions(template_objs)
        for category in categories:
            if category.name in wanted_categories:
                found_categories.append(category)
                
        return found_categories
          
    
    def get_answer_jurisdiction_numbers(self):
        usage_count = AnswerReference.objects.filter(question__exact=self, is_current__exact=1).values_list('jurisdiction_id').distinct().count()
        math_util_obj = MathUtil()
        if math_util_obj.is_number(usage_count):
            return usage_count
        else:
            return 0
        

                        
    def get_questions_with_no_answers(self, templates, jurisdiction_id, is_callout):
        juris = Jurisdiction.objects.get(id=jurisdiction_id)

        answer_question_ids = AnswerReference.objects.filter(is_callout__exact=is_callout, jurisdiction__exact=juris).values_list('question_id'); 
         
        # all the questions in the template
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id') 
           
        no_answer_questions = Question.objects.filter(id__in=all_template_question_ids).exclude(id__in=answer_question_ids)   
   
        return no_answer_questions        
        
    def get_questions_with_no_answers_by_category(self, templates, jurisdiction_id, cid, is_callout):
        juris = Jurisdiction.objects.get(id=jurisdiction_id)
        #templates = Template.objects.filter(template_type__iexact=template_type_str, jurisdiction__isnull=True) #look for callout template
        answer_question_ids = AnswerReference.objects.filter(is_callout__exact=is_callout, jurisdiction__exact=juris).exclude(rating_status__iexact="D").values_list('question_id'); 
 
        # all the questions in the template
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id') 
                 
        #get categories of all the questions that have no answers"
        category_obj = QuestionCategory.objects.get(id=cid)   
        no_answer_questions = Question.objects.filter(id__in=all_template_question_ids, category__exact=category_obj).exclude(id__in=answer_question_ids).order_by('display_order')   
                   
        return no_answer_questions   
        
    def get_categories_of_questions_with_no_answers(self,templates, jurisdiction_id, is_callout):
        juris = Jurisdiction.objects.get(id=jurisdiction_id)
        #templates = Template.objects.filter(template_type__iexact=template_type_str, jurisdiction__isnull=True) #look for callout template
        answer_question_ids = AnswerReference.objects.filter(is_callout__exact=is_callout, jurisdiction__exact=juris).exclude(rating_status__iexact="D").values_list('question_id'); 
        
        # all the questions in the template
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id')
        
        #get categories of all the questions that have no answers"
        category_ids = Question.objects.filter(id__in=all_template_question_ids).exclude(id__in=answer_question_ids).distinct('category_id').values_list('category_id')
        category = QuestionCategory.objects.filter(id__in=category_ids).order_by('name')      
        
        return category
    
    def get_categories_of_questions(self, templates):
        # all the questions in the template
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id')
        
        #get categories of all the questions that have no answers"
        category_ids = Question.objects.filter(id__in=all_template_question_ids).distinct('category_id').values_list('category_id')
        category = QuestionCategory.objects.filter(id__in=category_ids).order_by('display_order')      
        
        return category
    
    def get_template_question_categories(self, template_type, jurisdiction_id):
        juris = Jurisdiction.objects.get(id=jurisdiction_id)
        templates = Template.objects.filter(template_type__iexact=template_type)
        # all the questions in the template
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id')
        
        #get categories of all the questions"
        category_ids = Question.objects.filter(id__in=all_template_question_ids).distinct('category_id').values_list('category_id')
        categories = QuestionCategory.objects.filter(id__in=category_ids).order_by('name')      
        
        return categories    
    '''
    def get_questions_by_category(self, templates, cid):
        all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id') 
                
        #get categories of all the questions that have no answers"
        category_obj = QuestionCategory.objects.get(id=cid)   
        questions = Question.objects.filter(id__in=all_template_question_ids, category__exact=category_obj, accepted__exact=1).order_by('display_order')
        
        return questions
    '''
    def get_non_cf_questions_by_category(self, templates, cid):
        #all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id') 
                
        category_obj = QuestionCategory.objects.get(id=cid)   
        questions = Question.objects.filter(id__in=all_template_question_ids, category__exact=category_obj, accepted__exact=1).exclude(form_type__iexact='CF').order_by('display_order')
        #questions = Question.objects.filter(qtemplate__in=templates, category__exact=category_obj, accepted__exact=1).order_by('display_order')
        
        return questions
    
    def get_questions_by_category(self, templates, cid):
        #all_template_question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id') 
                
        category_obj = QuestionCategory.objects.get(id=cid)   
        #questions = Question.objects.filter(id__in=all_template_question_ids, category__exact=category_obj, accepted__exact=1).exclude(form_type__iexact='CF').order_by('display_order')
        questions = Question.objects.filter(qtemplate__in=templates, category__exact=category_obj, accepted__exact=1).order_by('display_order')
        
        return questions         
    
    def get_answer_choices_for_question(self, qid):
        question_obj = Question.objects.get(id=qid)
        try:
            answer_choice_group_obj = AnswerChoiceGroup.objects.get(id=question_obj.answer_choice_group_id)
            answer_choices = AnswerChoice.objects.filter(answer_choice_group__exact=answer_choice_group_obj).order_by('display_order').values_list('id', 'label')                   
            return answer_choices;
        except: #in case it has no answer choice group
            return []    
        
    def get_answer_by_question(self, question,jurisdiction_id):
        
        answers = AnswerReference.objects.filter(question = question, is_current = 1, jurisdiction__id = jurisdiction_id).order_by('-modify_datetime', '-create_datetime')
       
        try:
            answer = answers[0]
            if answer.value == None:
                #if question.default_value != None:
                #    return question.default_value
                return ''

            return answer.value
        except:
            #if question.default_value != None:
            #    return question.default_value
            return ''  
        
    def get_question_dependencies(self):
        dependencies = {}
    
        first_levels = QuestionDependency.objects.filter(question1__exact=self)
       
        if first_levels:
            for dependency1 in first_levels:
                
                question = Question.objects.get(id=dependency1.question2_id)        
                
                dependencies[dependency1.id] = {}  
                dependencies[dependency1.id]['answer_text'] = dependency1.answer_text
                dependencies[dependency1.id]['question'] = question.question
                dependencies[dependency1.id]['dependency_id'] = dependency1.id
                dependencies[dependency1.id]['question2_id'] = dependency1.question2_id 
                question2 = Question.objects.get(id=dependency1.question2_id)
                dependencies[dependency1.id]['next_level_depenencies'] = question2.get_question_dependencies()

        return dependencies
        
        
        
#questions in a template, questions are reusable for multiple templates
class TemplateQuestion(models.Model):
    template = models.ForeignKey(Template, db_index=True)
    question = models.ForeignKey(Question, db_index=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.template.name + ' - ' + str(self.question.id)
    class Meta:
        app_label = 'website'

RATING_STATUS_CHOICES = (
    ('U', 'Unconfirmed'),
    ('C', 'Confirmed'),
    ('D', 'Disputed'),
)

APPROVAL_STATUS_CHOICES = (
    ('P', 'Pending'),
    ('F', 'Flagged'),
    ('A', 'Approved'),
    ('R', 'Rejected'),
    ('C', 'Cancelled'),    
)

#answers for a reference template, like the template for electrical requirements in San Jose
class AnswerReference(models.Model):
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    is_callout = models.BooleanField(default=False) #this is for the callouts section
    question = models.ForeignKey(Question, db_index=True)
    value = models.TextField(blank=True, null=True) #convert all values to text
    file_upload = models.FileField(upload_to='answer_ref_files', blank=True, null=True)
    is_current = models.BooleanField(default=True, db_index=True) #should be the highest rating, or most recent if equal ratings
    rating = models.IntegerField(blank=True, null=True, db_index=True) #rating of this answer
    rating_status = models.CharField(choices=RATING_STATUS_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="U")
    approval_status = models.CharField(choices=APPROVAL_STATUS_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="P")
    creator = models.ForeignKey(User, blank=True, null=True)
    organization = models.ForeignKey(Organization, blank=True, null=True) #org that the creator belongs to at the time
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    status_datetime = models.DateTimeField(blank=True, null=True)    
    migrated_answer_id = models.IntegerField(blank=True, null=True) # to indicate source #not really used, see MigrationHistory!
    #support_attachments = models.BooleanField(default=False) # 1 to support file upload
    #question_type = models.CharField(max_length=16, db_index=True, default='predefined')   
    def __unicode__(self):
        return self.value
    class Meta:
        app_label = 'website'
          
        
    def get_answers_by_template_and_categories(self, jurisdiction_id, templates, categories, is_current, is_callout):
        juris = Jurisdiction.objects.get(id=jurisdiction_id)
        #templates = Template.objects.filter(template_type__iexact=template_type)
    
        if len(categories) > 0:
            category_objs = QuestionCategory.objects.filter(name__in=categories)
            questions_by_categories = Question.objects.filter(category__in=category_objs)
            question_ids = TemplateQuestion.objects.filter(template__in=templates, question__in=questions_by_categories).values_list('question_id')            
        else:
            question_ids = TemplateQuestion.objects.filter(template__in=templates).values_list('question_id')  

        questions = Question.objects.filter(id__in=question_ids)
        answers = AnswerReference.objects.filter(is_callout__exact=is_callout, jurisdiction__exact=juris, question__in=questions, is_current__exact=is_current).exclude(rating_status__iexact="D", approval_status__iexact='R'); 

        return answers           
        
    def set_approval_status(self, entity_id, action_category):
        if action_category == 'RequirementFlag':
            approval_status = 'F'
            
        answer_reference_obj = AnswerReference.objects.get(id=entity_id)
        answer_reference_obj.approval_status = 'F'          # Flagged
        answer_reference_obj.save()
        
        return answer_reference_obj
        
    def get_visibility_matrix(self, login, has_previously_visible_answer):
        
        visibility_matrix = {}
        if login == False and has_previously_visible_answer == False:
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'               
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'               
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'               
            visibility_matrix['D'] = by_approal_status    
            
        elif login == False and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'               
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'               
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'               
            visibility_matrix['D'] = by_approal_status              
    
   
        elif login == True and has_previously_visible_answer == False:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_as_unconfirmed'
            by_approal_status['A'] = 'show_as_unconfirmed'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show_as_unconfirmed'                 
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'                 
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['D'] = by_approal_status                
                               
        elif login == True and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}            
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'            
            visibility_matrix['D'] = by_approal_status             
                
        return visibility_matrix
    
    def get_callout_visibility_matrix(self, login, has_previously_visible_answer):
        
        visibility_matrix = {}
        if login == False and has_previously_visible_answer == False:
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['D'] = by_approal_status    
            
        elif login == False and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'            
            visibility_matrix['D'] = by_approal_status              
    
   
        elif login == True and has_previously_visible_answer == False:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_as_unconfirmed'
            by_approal_status['A'] = 'show_as_unconfirmed'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show_as_unconfirmed'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['D'] = by_approal_status                
                               
        elif login == True and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}            
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'            
            visibility_matrix['D'] = by_approal_status             
                
        return visibility_matrix
    
    def get_info_visibility_matrix(self, login, has_previously_visible_answer):
        
        visibility_matrix = {}
        if login == False and has_previously_visible_answer == False:
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['D'] = by_approal_status    
            
        elif login == False and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'            
            visibility_matrix['D'] = by_approal_status              
    
   
        elif login == True and has_previously_visible_answer == False:
            
            visibility_matrix['U'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_as_unconfirmed'
            by_approal_status['A'] = 'show_as_unconfirmed'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show_as_unconfirmed'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'hide'
            by_approal_status['A'] = 'hide'
            by_approal_status['R'] = 'hide'
            by_approal_status['F'] = 'hide'            
            visibility_matrix['D'] = by_approal_status                
                               
        elif login == True and has_previously_visible_answer == True:
            
            visibility_matrix['U'] = {}            
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['A'] = 'show_previous_answer_with_vopu_link'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer_with_vopu_link'            
            visibility_matrix['U'] = by_approal_status

            visibility_matrix['C'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show'
            by_approal_status['A'] = 'show'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show'            
            visibility_matrix['C'] = by_approal_status            
            
            visibility_matrix['D'] = {}
            by_approal_status = {}
            by_approal_status['P'] = 'show_previous_answer'
            by_approal_status['A'] = 'show_previous_answer'
            by_approal_status['R'] = 'show_previous_answer'
            by_approal_status['F'] = 'show_previous_answer'            
            visibility_matrix['D'] = by_approal_status             
                
        return visibility_matrix
    
    
            
    def check_requirement_visibility(self, login, ans_ref_id):
        
        ans_ref_obj = AnswerReference.objects.get(id=ans_ref_id)
        rating_status = ans_ref_obj.rating_status
        approval_status = ans_ref_obj.approval_status
                        
        has_previously_visible_answer = self.check_if_has_previously_visible_answer(ans_ref_obj)   
      
        visibility_matrix = self.get_visibility_matrix(login, has_previously_visible_answer)
        
        try:
            visibility = visibility_matrix[rating_status][approval_status]
        except:
     
            visibility = "hide"
        
        return visibility
    
    def check_callout_visibility(self, login, ans_ref_id):
        
        ans_ref_obj = AnswerReference.objects.get(id=ans_ref_id)
        rating_status = ans_ref_obj.rating_status
        approval_status = ans_ref_obj.approval_status
                        
        has_previously_visible_answer = self.check_if_has_previously_visible_answer(ans_ref_obj)   
         
        visibility_matrix = self.get_callout_visibility_matrix(login, has_previously_visible_answer)
        
        try:
            visibility = visibility_matrix[rating_status][approval_status]
        except:
        
            visibility = "hide"
        
        return visibility
    
    def check_info_visibility(self, login, ans_ref_id):
        
        ans_ref_obj = AnswerReference.objects.get(id=ans_ref_id)
        rating_status = ans_ref_obj.rating_status
        approval_status = ans_ref_obj.approval_status
                        
        has_previously_visible_answer = self.check_if_has_previously_visible_answer(ans_ref_obj)   
      
        visibility_matrix = self.get_info_visibility_matrix(login, has_previously_visible_answer)
        
        try:
            visibility = visibility_matrix[rating_status][approval_status]
        except:
       
            visibility = "hide"
        
        return visibility            
    
    def check_if_has_previously_visible_answer(self, ans_ref_obj):
        jurisdiction_id = ans_ref_obj.jurisdiction_id
        question_id = ans_ref_obj.question_id
        is_callout = ans_ref_obj.is_callout
        jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)        
        question = Question.objects.get(id=question_id)
        ans_ref_objs = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, is_callout__exact=is_callout, rating_status__exact='C').exclude(approval_status__exact='R')

        if ans_ref_objs:
            return True
        else:
            # no confirmed answer.  let's look at the unconfirmed, per later request not to replace the unconfirmed answer by any unconfirmed answer.
            ans_ref_objs = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, is_callout__exact=is_callout, rating_status__exact='U').exclude(approval_status__exact='R').exclude(id=ans_ref_obj.id)
            if len(ans_ref_objs) > 0:
                return True
            else:
                return False
            
        return False
        
    def get_previously_visible_answer(self, ans_ref_obj):
        jurisdiction_id = ans_ref_obj.jurisdiction_id
        question_id = ans_ref_obj.question_id
        is_callout = ans_ref_obj.is_callout
        jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)        
        question = Question.objects.get(id=question_id)
        ans_ref_objs = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, is_callout__exact=is_callout, rating_status__exact='C').exclude(approval_status__exact='R').order_by('create_datetime')

        if ans_ref_objs:
            return ans_ref_objs[0]
        else:
            # no confirmed answer.  let's look at the unconfirmed, per later request not to replace the unconfirmed answer by any unconfirmed answer.
            ans_ref_objs = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question, is_callout__exact=is_callout, rating_status__exact='U').exclude(approval_status__exact='R').exclude(id=ans_ref_obj.id).order_by('create_datetime')
            if len(ans_ref_objs) > 0:   # to eleminate itself
                return ans_ref_objs[0]
            else:
                return False    
            
        return False    
        
    def get_rating_status_change_message(self, entity_name, entity_id, prev_msg, new_msg, action_category):
        msg = ''

        if entity_name.lower() == 'requirement' and action_category.lower() == 'voterequirement':
        
            if prev_msg.lower() != 'c' and new_msg.lower() == 'c':
       
                msg = "There are now enough votes for this item and it is now Confirmed.  Thank you!"
                
            if prev_msg.lower() != 'd' and new_msg.lower() == 'd':
                msg = "There are enough votes to dispute this item and it is now hidden.  Thank you!"
                
        if entity_name.lower() == 'callout' and action_category.lower() == 'votecallout':
            
            if prev_msg.lower() != 'c' and new_msg.lower() == 'c':
              
                msg = "There are now enough votes for this item and it is now Confirmed.  Thank you!"
                
            if prev_msg.lower() != 'd' and new_msg.lower() == 'd':
                msg = "There are enough votes to dispute this item and it is now hidden.  Thank you!"       
                
        if entity_name.lower() == 'info' and action_category.lower() == 'voteinfo':
           
            if prev_msg.lower() != 'c' and new_msg.lower() == 'c':
               
                msg = "There are now enough votes for this item and it is now Confirmed.  Thank you!"
                
            if prev_msg.lower() != 'd' and new_msg.lower() == 'd':
                msg = "There are enough votes to dispute this item and it is now hidden.  Thank you!"                   
                
        return msg
                
        
    def save_answer(self, question_obj, answer, juris, action_category_obj, user, is_callout):
        
        #juris = Jurisdiction.objects.get(id=jid)
       
        #question_obj = Question.objects.get(id=qid)
        answerreferences = AnswerReference.objects.filter(question__exact=question_obj, jurisdiction__exact=juris, is_callout__exact=is_callout, is_current__exact=1)  
        if answerreferences:
            for answer_ref_obj in answerreferences:
                answer_ref_obj.is_current = 0
                answer_ref_obj.modify_datetime = datetime.datetime.now()
              
                answer_ref_obj.save()

        encoded_txt = answer.encode('utf-8')           
       
        save_n_approved = False
        if user.is_superuser == 1:
            if question_obj.has_multivalues == 1:
                save_n_approved = True
            elif len(answerreferences) == 0:   # if entered by superadmin and if there is no existing suggestion -> automatic approval
                save_n_approved = True
            else:
                save_n_approved = False
        else:     
            save_n_approved = False
            
        if save_n_approved == True:
            approval_status = 'A'
        else:
            approval_status = 'P'
            
        answerreference = AnswerReference(question_id = question_obj.id, value = encoded_txt, jurisdiction_id = juris.id, is_callout = is_callout, rating_status='U', approval_status=approval_status, is_current=1, creator_id=user.id, status_datetime = datetime.datetime.now(), modify_datetime = datetime.datetime.now())            
        
        answerreference.save()
      
        #category_name = action_key
        #entity_name='AnswerReference'
        #data = str(answer)
        action_obj = Action()
        action_obj.save_action(category_name, data, answerreference, entity_name, user.id, juris)      
        
        org_members = OrganizationMember.objects.filter(user=user, status = 'A', organization__status = 'A')
        if len(org_members) > 0:
            org = org_members[0].organization
            juris.last_contributed_by_org = org
                
        juris.last_contributed = datetime.datetime.now()
        juris.last_contributed_by = user
        juris.save()
   
        return answerreference      
    
    def save_question_n_value(self, question_txt, value, jid, cid, user):
        # save to Question
        encoded_txt = question_txt.encode('utf-8')        
       
        question = Question(question=encoded_txt, form_type="TA", category_id=cid)
        question.save()
  
        # save to template question
        #template_question = TemplateQuestion(template_id=tid, question_id=question.id)
        #template_question.save()
    
        # save to answer refereence
        action_key = "AddRequirement"
        is_callout = 0
        #answer_reference_class_obj = AnswerReference()
        answerreference = self.save_answer(question.id, value, jid, action_key, user, is_callout)
        # save to AnswerReference
      
        return answerreference
    
    def answer_file_type(self):
        if self.question.form_type == 'F':
            import os
            asw = str(self.file_upload)
            filename, extension = os.path.splitext(asw)
            image_type_array = ['.jpg', '.jpeg', '.gif', '.bmp', '.png', '.tiff']
     
            if image_type_array.count(extension) > 0:
                return True
            return False
        return False      
    
    def get_jurisdiction_data(self,jurisdiction_id, question):
        answer = {} 
        jurisdiction = Jurisdiction.objects.get(id=jurisdiction_id)
        questions = Question.objects.filter(question__iexact=question)
        answer['has_answer'] = False
        if questions and jurisdiction:
            question = questions[0]
            answer['question'] = question
            answer_references = AnswerReference.objects.filter(jurisdiction__exact=jurisdiction, question__exact=question).order_by('-create_datetime') # temp solution: order by desc, then use the last one.  in the future must use the confirmed/approval logic 
        
            if answer_references:
                answer_reference = answer_references[0]
                answer_value = answer_reference.value
                answer = json.loads(answer_value)
                answer['contributor'] = answer_reference.creator
                answer['contributor_id'] = answer_reference.creator_id              
                answer['question'] = question
                datetime_util_obj = DatetimeHelper(jurisdiction.last_contributed)
                answer['contribution_date'] = datetime_util_obj.showStateTimeFormat(jurisdiction.state)                  
                #answer['contribution_date'] = answer_reference.create_datetime
                answer['has_answer'] = True
            else:
                answer = {}
                answer['question'] = question
                answer['has_answer'] = False
    
        return answer
    
    def get_attachment_num(self):
        aacs = AnswerAttachment.objects.filter(answer_reference = self)
        return len(aacs)
        
        #def save(self, *args, **kwargs):
        #    super(AnswerReference, self).save(*args, **kwargs)

class AnswerAttachment(models.Model):
    answer_reference = models.ForeignKey(AnswerReference, blank=True, null=True, db_index=True)
    #entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #Django entity name, like "AnswerReference"
    #entity_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    file_upload = models.FileField(upload_to='answer_ref_attaches', blank=True, null=True)
    file_name = models.CharField(max_length=128,blank=True, null=True)
    creator = models.ForeignKey(User, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    
    class Meta:
        app_label = 'website'
        
class Comment(models.Model):
    COMMENT_TYPE_CHOICES = (
        ('JC', 'Jurisdiction Comment'),
        ('RC', 'Requirement Comment'),
        ('RF', 'Requirement Flag'),
        ('COF', 'Callout Flag'),    
        #('CC', 'Comment Comment'), #comment on a comment, no longer a type, use parent_comment field instead!
        ('CF', 'Comment Flag'), #flag a comment
        ('COC', 'Callout Comment'),   
    )
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #Django entity name, like "AnswerReference"
    entity_id = models.PositiveIntegerField(blank=True, null=True, db_index=True)
    user = models.ForeignKey(User, blank=True, null=True)
    comment_type = models.CharField(choices=COMMENT_TYPE_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="")
    comment = models.TextField(blank=True, null=True)
    parent_comment = models.ForeignKey('self', related_name='parent_reference', blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True, db_index=True) #rating of this comment, highest listed first
    rating_status = models.CharField(choices=RATING_STATUS_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="U")
    approval_status = models.CharField(choices=APPROVAL_STATUS_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="P")
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    
    # entity_name and entity_id represent the entity to which the comments are for.  ex: answerreference, or comment itself.
    def save_comment(self, entity_id, entity_name, comment_type, comment_txt, user):
   
        comment = Comment(entity_id = entity_id, entity_name = entity_name, comment_type = comment_type, comment=comment_txt, user_id=user.id)

        comment.save()
    

        return comment
    def get_son_comments(self):
        comments = Comment.objects.filter(parent_comment = self).order_by('create_datetime')
        return comments
    
    def comment_level(self):
        if self.parent_comment == None:
            return 1
        if self.parent_comment.parent_comment == None:
            return 2
        if self.parent_comment.parent_comment.parent_comment == None:
            return 3
        return 4
    
    def get_comment_time(self):
        datetime_util_obj = DatetimeHelper(self.create_datetime)
        return datetime_util_obj.showStateTimeFormat(self.jurisdiction.state)
    
#track viewing of comments by user
class UserCommentView(models.Model):
    user = models.ForeignKey(User, blank=True, null=True)
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)
    entity_name = models.CharField(max_length=32, blank=True, null=True, db_index=True) #Django entity name, like "AnswerReference"
    entity_id = models.PositiveIntegerField(blank=True, null=True, db_index=True) #entity id that the comment was for
    last_comment = models.ForeignKey(Comment, blank=True, null=True) #the last comment for that entity id at the time of viewing
    comments_count = models.IntegerField(blank=True, null=True) #total count of comments at the time of viewing, to calculate how many new later
    view_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True) #when the comments were viewed, need to be updated every time viewed
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    
    
class View(models.Model):
    VIEW_TYPE_CHOICES = (
        ('a', 'Attachments'),                         
        ('f', 'Favorite Fields'),
        ('q', 'Quirks'),
        ('v', 'Views'),        
    )    
    view_type = models.CharField(choices=VIEW_TYPE_CHOICES, max_length=8, blank=True, null=False, db_index=True, default="") 
    user = models.ForeignKey(User, blank=True, null=True)
    jurisdiction = models.ForeignKey(Jurisdiction, blank=True, null=True, db_index=True)       
    name = models.CharField(max_length=128, blank=True, null=True, db_index=True)   # quirks for quirks view type; favorite_fields for favorite fields
    description = models.TextField(blank=True, null=True)
    reviewed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.name        
    class Meta:
        app_label = 'website'
        
# to be deprecated when ViewAccess is implemented.
class ViewOrgs(models.Model):
    view = models.ForeignKey(View, db_index=True)
    organization = models.ForeignKey(Organization, db_index=True) 
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)  
    def __unicode__(self):
        return self.view.name + ' - ' + str(self.organization.name)
    class Meta:
        app_label = 'website'        
        
    def get_user_accessible_views(self, user):
        accessible_views = []
        try:
            user = User.objects.get(id=user.id)
            user_orgs = OrganizationMember.objects.filter(status = 'A', organization__status = 'A', user = user)

            if len(user_orgs) > 0:
                orgs = []
                for user_org in user_orgs:
                    orgs.append(user_org.organization)
                    
                view_orgs = ViewOrgs.objects.filter(organization__in=orgs)
                if len(view_orgs) > 0:
                    for view_org in view_orgs:
                       accessible_views.append(view_org.view.name.lower())            
        except:
            pass   
        
        return  accessible_views    
        
class ViewQuestions(models.Model):
    view = models.ForeignKey(View, db_index=True)
    question = models.ForeignKey(Question, db_index=True)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)    
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.view.name + ' - ' + str(self.question.id)
    class Meta:
        app_label = 'website'
        
    def get_jurisdiction_quirks(self, jurisdiction):
        quirks = {}
        view_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='q')
        if len(view_objs) > 0:
            view_obj = view_objs[0]
            
            view_question_objs = ViewQuestions.objects.filter(view = view_obj).order_by('display_order')
            quirks['view_id'] = view_obj.id
            quirks['view_questions'] = view_question_objs

        return quirks
        
    def get_user_favorite_fields(self, user):
        user_fav_fields = {}
        view_objs = View.objects.filter(user = user, view_type__exact='f')
        if len(view_objs) > 0:
            view_obj = view_objs[0]
            
            view_question_objs = ViewQuestions.objects.filter(view = view_obj).order_by('display_order')
            user_fav_fields['view_id'] = view_obj.id
            user_fav_fields['view_questions'] = view_question_objs

        return user_fav_fields
    
    def get_jurisdiction_attachments(self, jurisdiction):
        attachments = {}
        view_objs = View.objects.filter(jurisdiction = jurisdiction, view_type__exact='a')
        if len(view_objs) > 0:
            view_obj = view_objs[0]
            
            view_question_objs = ViewQuestions.objects.filter(view = view_obj).order_by('display_order')
            attachments['view_id'] = view_obj.id
            attachments['view_questions'] = view_question_objs

        return attachments    
    
    def add_question_to_view(self, view_type, question, jurisdiction):
        '''
        if view_type == 'q':
            view_objs = View.objects.filter(view_type = 'q', jurisdiction = jurisdiction)
            if len(view_objs) > 0:
                view_obj = view_objs[0]
            else:
                view_obj = View()
                view_obj.name = 'quirks'
                view_obj.description = 'Quirks'
                view_obj.view_type = 'q'
                view_obj.jurisdiction_id = jurisdiction.id
                view_obj.save()
                    
        elif view_type == 'f':
            view_objs = View.objects.filter(view_type = 'f', user = user)
            if len(view_objs) > 0:
                view_obj = view_objs[0]
            else:
                view_obj = View()
                view_obj.name = 'Favorite Fields'
                view_obj.description = 'Favorite Fields'
                view_obj.view_type = 'f'
                view_obj.user_id = request.user.id
                view_obj.save()  
            
        el
        '''
        view_obj = None
        
        if view_type == 'a':
            view_objs = View.objects.filter(view_type = 'a', jurisdiction = jurisdiction)
            if len(view_objs) > 0:
                view_obj = view_objs[0]
            else:
                view_obj = View()
                view_obj.name = 'attachments'
                view_obj.description = 'Attachments'
                view_obj.view_type = 'a'
                view_obj.jurisdiction_id = jurisdiction.id
                view_obj.save()                      
            
        if view_obj != None:
            view_questions_objs = ViewQuestions.objects.filter(view = view_obj, question = question)
            if len(view_questions_objs) == 0:
                view_questions_objs = ViewQuestions.objects.filter(view = view_obj).order_by('-display_order')                
                if len(view_questions_objs) > 0:
                    highest_display_order = view_questions_objs[0].display_order
                else:
                    highest_display_order = 0
                        
                view_questions_obj = ViewQuestions()
                view_questions_obj.view_id = view_obj.id
                view_questions_obj.question_id = question.id
                view_questions_obj.display_order = int(highest_display_order) + 5
                view_questions_obj.save()
        
        return True        
    
    def remmove_question_from_view(self, view_type, question, jurisdiction):
            view_objs = View.objects.filter(view_type = 'a', jurisdiction = jurisdiction)
            if len(view_objs) > 0:
                view_obj = view_objs[0]
                view_questions_objs = ViewQuestions.objects.filter(view = view_obj, question = question)
                if len(view_questions_objs) > 0:               
                    answers = AnswerReference.objects.filter(jurisdiction = jurisdiction, question = question, approval_status__in=('A', 'P'), value__icontains='upload')
                    if len(answers) == 0:
                        for view_question_obj in view_questions_objs:
                            view_question_obj.delete()
                            
                        