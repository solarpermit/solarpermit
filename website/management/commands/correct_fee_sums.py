from django.core.management.base import BaseCommand, CommandError

import json

from website.models import Question, AnswerReference
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Correct the fee summation'

    def handle(self, *args, **options):
        print 'correct fee summation started.'        
        fieldValidationCycleUtil_obj = FieldValidationCycleUtil()
        question_obj = Question.objects.get(id=16)
    
        if question_obj != None:
            AnswerReference_objs = AnswerReference.objects.filter(question = question_obj)
            if len(AnswerReference_objs) > 0:
                print str(len(AnswerReference_objs)) + " to be processed."
                
                for AnswerReference_obj in AnswerReference_objs:
                    answer = fieldValidationCycleUtil_obj.process_answer(question_obj, AnswerReference_obj.value)
                    encoded_txt = answer.encode('utf-8') 
                    AnswerReference_obj.value = encoded_txt
                    AnswerReference_obj.save()
                
        
        print 'correct fee summation completed.'
        
        
        
           
        