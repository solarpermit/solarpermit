import json
from django.conf import settings
from django.utils.encoding import smart_unicode 
from datetime import *
from website.models import Question, AnswerReference
from website.utils.textUtil import TextUtil

class AnswerHelper:
    QUESTION_HIERARCHY = {
        #parent question id: ids of children questions
        14: [117],
        96: [115],
        63: [64],
        105: [116],
        5: [30],
    }
    MIN_FREE_FORM_LENGTH = 30 #number of char for some string to be consider as free form
    
    def migrate_answer_value(self, question, answer_record, child_answer_records, is_special=False):
        #get the default answer object
        if question.default_value == None or question.default_value == '':
            answer_obj = {"value": ""}
        else:
            answer_obj = json.loads(question.default_value)
        
        #special handling of address_record as answer_record
        if question.migration_type == 'address' and is_special == True:
            if answer_record['address1'] != None:
                answer_obj['address1'] = answer_record['address1']
            if answer_record['address2'] != None:
                answer_obj['address2'] = answer_record['address2']
            if answer_record['city'] != None:
                answer_obj['city'] = answer_record['city']
            if answer_record['state'] != None:
                answer_obj['state'] = answer_record['state']
            if answer_record['zip_code'] != None:
                answer_obj['zip_code'] = answer_record['zip_code']
            answer_string = json.dumps(answer_obj)
            return answer_string
        
        #handling of other answer_record types
        answer_string = ''
        import_answer_value = self.format_import_answer(answer_record).strip()
        lower_value = import_answer_value.lower()
        
        if question.migration_type == 'address':
            #if it is here, this is free form address
            answer_obj['free-form'] = import_answer_value
        elif question.migration_type == 'phone':
            answer_obj['phone'] = import_answer_value
            
        elif question.migration_type == 'time_range':
            #{\"to_min\": \"00\", \"to_hour\": \"5\", \"from_am_pm\": \"am\", \"to_am_pm\": \"pm\", \"from_min\": \"00\", \"from_hour\": \"9\"}
            # TODO - parse time range
            am_count = lower_value.count('am')
            pm_count = lower_value.count('pm')
            if am_count == 1 and pm_count == 1:
                am_segments = lower_value.split('am')
                if 'pm' in am_segments[1]:
                    segment1 = am_segments[0]
                    segment2 = am_segments[1].split('pm')[0]
                    answer_obj['from_am_pm'] = 'am'
                    answer_obj['to_am_pm'] = 'pm'
                elif 'pm' in am_segments[0]:
                    segments = am_segments[0].split('pm')
                    segment1 = segments[0]
                    segment2 = segments[1]
                    answer_obj['from_am_pm'] = 'pm'
                    answer_obj['to_am_pm'] = 'am'
            elif am_count == 2 and pm_count == 0:
                segments = lower_value.split('am')
                segment1 = segments[0]
                segment2 = segments[1]
                answer_obj['from_am_pm'] = 'am'
                answer_obj['to_am_pm'] = 'am'
            elif am_count == 0 and pm_count == 2:
                segments = lower_value.split('pm')
                segment1 = segments[0]
                segment2 = segments[1]
                answer_obj['from_am_pm'] = 'pm'
                answer_obj['to_am_pm'] = 'pm'
            else:
                # TODO - can't parse yet
                segment1 = ''
                segment2 = ''
            answer_obj['from_hour'], answer_obj['from_min'] = TextUtil.get_hour_minute(segment1)
            answer_obj['to_hour'], answer_obj['to_min'] = TextUtil.get_hour_minute(segment2)
            
            #put in note also for now anyway
            answer_obj['note'] = import_answer_value #for now
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value
            
        elif question.migration_type == 'time_quantity':
            #{\"note\": \"\", \"time_unit\": \"hour(s)\", \"time_qty\": \"1\"}
            # TODO - improve time quantity and unit?
            #is there the word "day"
            if 'day' in import_answer_value:
                day_segment = import_answer_value.split('day')[0]
                time_qty = TextUtil.get_last_number(day_segment)
                if time_qty != '':
                    answer_obj['time_qty'] = time_qty
                    answer_obj['time_unit'] = 'day(s)'
            elif 'hour' in import_answer_value:
                hour_segment = import_answer_value.split('hour')[0]
                time_qty = TextUtil.get_last_number(hour_segment)
                if time_qty != '':
                    answer_obj['time_qty'] = time_qty
                    answer_obj['time_unit'] = 'hour(s)'
            
            answer_obj['note'] = import_answer_value #also put in note?
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value
            
        elif question.migration_type == 'page_size':
            #"default_value": "{\"required\": \"no\", \"size\": \"\", \"width\": \"\", \"height\": \"\"  }",
            width = TextUtil.get_first_number(import_answer_value)
            if width != '':
                segments = import_answer_value.split(width, 1) #only 1 split
                height = TextUtil.get_first_number(segments[1])
                if height != '':
                    answer_obj['width'] = width
                    answer_obj['height'] = height
            #print 'width: '+width+', height: '+height
            
            #if len(import_answer_value) > self.MIN_FREE_FORM_LENGTH:
                #answer_obj['free-form'] = import_answer_value
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'accepts_electronic_submissions':
            #{"accepts_electronic_submissions": "Yes", "url_or_email_for_submissions": "url", "url_for_online_submissions": ""}
            answer_obj['accepts_electronic_submissions'] = import_answer_value
            if len(child_answer_records) > 0:
                child_answer_record = child_answer_records[0]
                child_format_answer = self.format_import_answer(child_answer_record)
                answer_obj['url_for_online_submissions'] = child_format_answer
        
            #if len(import_answer_value) > self.MIN_FREE_FORM_LENGTH:
                #answer_obj['free-form'] = import_answer_value
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value
                
        elif question.migration_type == 'required_dead_load':
            #{\"note\": \"\", \"required\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"dead_load_calculations\": \"No\", \"url_or_email_for_submissions\": \"url\"  }",
            answer_obj['required'] = import_answer_value
            #if len(import_answer_value) > self.MIN_FREE_FORM_LENGTH:
                #answer_obj['free-form'] = import_answer_value
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value
            
            if len(child_answer_records) > 0:
                child_answer_record = child_answer_records[0]
                child_format_answer = self.format_import_answer(child_answer_record)
                answer_obj['note'] = child_format_answer
                #put all into free-form for now
                answer_obj['free-form'] += child_format_answer
            
        elif (question.migration_type == 'required_if_greater_than' 
                or question.migration_type == 'allowed_if_greater_than'
                or question.migration_type == 'available_if_greater_than'
                or question.migration_type == 'enforced_if_greater_than'):
            #{\"note\": \"\", \"required\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"url_or_email_for_submissions\": \"url\"  }",
            #{\"note\": \"\", \"enforced\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"url_or_email_for_submissions\": \"url\"  }",
            #{\"note\": \"\", \"allowed\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"url_or_email_for_submissions\": \"url\"  }",
            #{\"note\": \"\", \"available\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"url_or_email_for_submissions\": \"url\"  }",
            if 'yes' in lower_value:
                choice = 'Yes'
            elif 'no' in lower_value:
                choice = 'No'
            else:
                choice = ''
            if question.migration_type == 'required_if_greater_than':
                answer_obj['required'] = choice
            elif question.migration_type == 'allowed_if_greater_than':
                answer_obj['allowed'] = choice
            elif question.migration_type == 'available_if_greater_than':
                answer_obj['available'] = choice
            else:
                answer_obj['enforced'] = choice
                
            if lower_value != 'yes' and lower_value != 'no':
                answer_obj['note'] = import_answer_value
            quantity = TextUtil.get_first_number(import_answer_value)
            if quantity != '':
                answer_obj['kW'] = quantity
            #put all into free-form for now
            answer_obj['free-form'] = import_answer_value

        elif question.migration_type == 'additional_licensing_required':
            #{\"note\": \"\", \"additional_licensing_required\": \"no\"}
            answer_obj['additional_licensing_required'] = import_answer_value
            
        elif question.migration_type == 'available_url':
            #{\"available\":\"no\", \"url\":\"\"}
            answer_obj['available'] = import_answer_value
            if len(child_answer_records) > 0:
                child_answer_record = child_answer_records[0]
                child_format_answer = self.format_import_answer(child_answer_record)
                answer_obj['url'] = child_format_answer
        
        elif question.migration_type == 'plan_check_service':
            #{\"note\": \"\", \"plan_check_service_type\": \"Over the counter\"}
            if 'counter' in lower_value:
                answer_obj['plan_check_service_type'] = 'Over the counter'
            elif 'outsourced' in lower_value:
                answer_obj['plan_check_service_type'] = 'Outsourced'
            elif 'house' in lower_value:
                answer_obj['plan_check_service_type'] = 'In-house'
            else:
                answer_obj['plan_check_service_type'] = ''
                #answer_obj['note'] = import_answer_value
                #put all into free-form for now
                answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'utilities':
            #{\"link_1\": \"\", \"name_1\": \"\"}
            if len(import_answer_value) <= self.MIN_FREE_FORM_LENGTH:
                answer_obj['name_1'] = import_answer_value
            else:
                answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'radio_with_exception':
            #{\"note\": \"\", \"required\": \"No\", \"system_rating_method\": \"\", \"equality\": \"greater than\", \"kW\": \"\", \"url_or_email_for_submissions\": \"url\"  }",
            #there is currently no data of this type in natSolDB anyway
            answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'request_type':
            #{\"request\":\"\", \"request_by_phone\":\"\", \"request_by_fax\":\"\", \"request_by_email\":\"\",\"phone\":\"\", \"fax\":\"\", \"email\":\"\"}",
            #there is currently no data of this type in natSolDB anyway
            answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'delivery_type':
            #{\"mail\":\"\", \"email\":\"\", \"onsite\":\"\"}
            #there is currently no data of this type in natSolDB anyway
            answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'drawing_scales':
            #{\"scale\": \"any\" }
            #there is currently no data of this type in natSolDB anyway
            answer_obj['free-form'] = import_answer_value
            
        elif question.migration_type == 'required_and_note':
            #{\"note\": \"\", \"required\": \"No\"}
            if 'sometimes' in lower_value or 'yes' in lower_value:
                answer_obj['required']= 'Yes'
            elif 'no' in lower_value:
                answer_obj['required']= 'No'
            else:
                #answer_obj['note']= import_answer_value
                #put all into free-form for now
                answer_obj['free-form'] = import_answer_value
            if len(import_answer_value) <= self.MIN_FREE_FORM_LENGTH and answer_obj['note'] == '':
                answer_obj['free-form'] = import_answer_value
        
        elif question.migration_type == 'free-form':
            #free-form type for anything too difficult to parse
            answer_obj['free-form'] = import_answer_value
        
        else: #default to simple type with just value
            answer_obj['value'] = import_answer_value
        
        answer_string = json.dumps(answer_obj)
        return answer_string
        
    def is_answer_match(self, answer_record, answer):
        answer_value = self.format_import_answer(answer_record)
        answer_json = answer.value
        try:
            answer_dict = json.loads(answer_json)
        except:
            print 'Failed to parse json form answer: '+answer_json
            return False
                
        for key in answer_dict:
            if answer_dict[key].lower() == answer_value.lower():
                return True
            
        return False

    def format_import_answer(self, answer_record):
        output = ''
        if answer_record['valueType'] != None:
            try:
                output = smart_unicode(answer_record[answer_record['valueType']+'Value'])
            except:
                pass
        #handle boolean type
        if answer_record['valueType'] == 'boolean':
            if output == '1':
                output = 'Yes'
            else:
                output = 'No'
        
        output = TextUtil.clean(output)
        return output

    def is_child_answer(self, answer_record):
        for parent_id in self.QUESTION_HIERARCHY:
            if answer_record['questionID'] in self.QUESTION_HIERARCHY[parent_id]:
                return True
        return False
    
    #get the child answer records of this answer record, among the answer records
    def get_child_answers(self, answer_record, answer_records):
        child_answer_records = []
        try:
            child_ids = self.QUESTION_HIERARCHY[answer_record['questionID']]
        except:
            child_ids = []
        for child_id in child_ids:
            #look up answer to child question
            for child_record in answer_records:
                #if it is that child question id and timestamp same as parent
                if child_record['questionID'] == child_id and child_record['created'] == answer_record['created']:
                    child_answer_records.append(child_record)
                    break
        return child_answer_records
