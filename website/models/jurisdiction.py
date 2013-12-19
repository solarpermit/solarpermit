import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.localflavor.us.us_states import STATE_CHOICES
from django.conf import settings
from website.models import Organization, UserFavorite
from django.contrib.localflavor.us.us_states import US_STATES
import urllib
from htmlentitiesdecode import decode as entity_decode
import re
from website.utils.datetimeUtil import DatetimeHelper 

JURISDICTION_TYPE_CHOICES = (
    ('S', 'State'),
    ('CO', 'County'),
    ('SC', 'County with Field Offices'), #county with multiple field offices
    ('CONP', 'County (does not handle permits)'), #county that do not handle permits, should refer to parent at state level
    ('SCFO', 'County Field Office'), #field office of a county
    ('CC', 'City and County'),
    ('CI', 'City'),
    ('CINP', 'City (does not handle permits)'), #city that do not handle permits, should refer to parent at county level
    ('IC', 'Independent City'),
    ('U', 'Unincorporated'), #meaning no jurisdiction, refer users to parent jurisdiction
    ('O', 'Other'),
)

class Jurisdiction(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    description = models.TextField(blank=True, null=True)
    jurisdiction_type = models.CharField(choices=JURISDICTION_TYPE_CHOICES, max_length=8, blank=True, null=True)
    parent = models.ForeignKey('self', related_name='parent_jurisdiction', blank=True, null=True) #usually for unincorporated jurisdiction
    organization = models.ForeignKey(Organization, blank=True, null=True, related_name= '_org_jurisdiction') #link to org info & structure
    city = models.CharField(max_length=64, blank=True, null=True, db_index=True) #if for a city
    county = models.CharField(max_length=64, blank=True, null=True, db_index=True) #if within a county
    state = models.CharField(choices=STATE_CHOICES, max_length=8, blank=True, null=True, db_index=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True, db_index=True)
    last_contributed = models.DateTimeField(blank=True, null=True, db_index=True)
    last_contributed_by = models.ForeignKey(User, blank=True, null=True)    
    last_contributed_by_org = models.ForeignKey(Organization, blank=True, null=True, related_name= '_org_contributor')
    name_for_url = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    
   
        
    def get_jurisdiction_type(self):
        jurisdiction_type = ''
        
        if self.jurisdiction_type == 'CI':
            jurisdiction_type = 'City'
        elif self.jurisdiction_type == 'CO':
            jurisdiction_type = 'County'
        elif self.jurisdiction_type == 'CC':
            jurisdiction_type = 'City and County'
        elif self.jurisdiction_type == 'S':
            jurisdiction_type = 'State'
        elif self.jurisdiction_type == 'O':
            jurisdiction_type = 'Other'
        
        return jurisdiction_type
            
    def show_jurisdiction(self, form='short'):
        str_return = ''

        if self.jurisdiction_type == 'CI' or self.jurisdiction_type == 'U' or self.jurisdiction_type == 'CINP':
            str_return += self.name
            if str_return == '' and self.city != '' and self.city != None:
                str_return +=  str(self.city)            
            if str_return == '' and self.county != '' and self.county != None:
                str_return +=  str(self.county)
                #str_return += ', '+ str(self.county)
            if self.state != '' and self.state != None:
                str_return += ', '+ str(self.get_state_display(form))
                
        elif self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'SC' or self.jurisdiction_type == 'CONP':
            county_equilvalent = self.get_county_equivalent_name()
            str_return += county_equilvalent.capitalize() + ' of ' + self.name
            if self.state != '' and self.state != None:
                str_return += ', '+ str(self.get_state_display(form))                            
                
        elif self.jurisdiction_type == 'CC':
            county_equilvalent = self.get_county_equivalent_name()
            str_return += 'City and '+county_equilvalent.capitalize()+' of ' + self.name
            '''
            if self.city != '' and self.city != None:
                str_return += ', '+ str(self.city)            
            if self.county != '' and self.county != None:
                str_return += ', '+ str(self.county)
            '''
            if self.state != '' and self.state != None:
                str_return += ', '+ str(self.get_state_display(form))

        elif self.jurisdiction_type == 'S':
            str_return += 'State of ' + self.name  
                                    
        elif self.jurisdiction_type == 'O':
            str_return += self.name 
            if self.state != '' and self.state != None:
                str_return += ', '+ str(self.get_state_display(form))
                
        elif self.jurisdiction_type == 'SCFO':
            str_return += self.name
            #county_equilvalent = self.parent.get_county_equivalent_name()
            #str_return += self.parent.name + ' ' + county_equilvalent.capitalize() + ' Field Office - ' + self.name
                                
        else:
            str_return += self.name 
            if self.state != '' and self.state != None:
                str_return += ', '+ str(self.get_state_display(form))            
                                                                                        
        return str_return
    
    def get_jurisdiction_display(self, place_of_display='title'):
        str_return = ''
        
        if place_of_display == 'title':
            if self.jurisdiction_type == 'S':
                if self.name.find(self.get_state_display('long')) > -1:
                    str_return = self.name
                else:
                    str_return = self.name + ', ' + self.get_state_display('long')
                    
            elif self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'CONP' or self.jurisdiction_type == 'SC':
                equilvalent_name = self.get_county_equivalent_name()
                str_return = self.name + ' ' + equilvalent_name.capitalize() + ', ' + self.state
                
            elif self.jurisdiction_type == 'CI' or self.jurisdiction_type == 'CINP' or self.jurisdiction_type == 'U':
                if self.parent != None:
                    county_name = self.parent.name
                    equilvalent_name = self.parent.get_county_equivalent_name()
                    str_return = self.name + ', ' + county_name.title() + ' ' + equilvalent_name.capitalize() + ', ' + self.state
                else:
                    str_return = self.name + ', ' + self.state       
                
            elif self.jurisdiction_type == 'SCFO':
                str_return = self.name + ', ' + self.state                
            else:
                str_return = self.name + ', ' + self.state 
                
        elif place_of_display == 'page_title':
            if self.jurisdiction_type == 'S':
                if self.name.find(self.get_state_display('long')) > -1:
                    str_return = self.name
                else:
                    str_return = self.get_state_display('long').capitalize() + ' ' + self.name
                    
            elif self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'CONP' or self.jurisdiction_type == 'SC':
                equilvalent_name = self.get_county_equivalent_name()
                str_return = equilvalent_name.capitalize() + ' of ' + self.name + ', ' + self.state
                
            elif self.jurisdiction_type == 'CI' or self.jurisdiction_type == 'CINP' or self.jurisdiction_type == 'U' or self.jurisdiction_type == 'SCFO':
                str_return = self.name + ', ' + self.state
            else:
                str_return = self.name + ', ' + self.state      
                        
        elif place_of_display == 'breadcrum':
            if self.jurisdiction_type == 'S':
                str_return = self.name
                    
            elif self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'CONP' or self.jurisdiction_type == 'SC':
                equilvalent_name = self.get_county_equivalent_name()
                str_return = self.name + ' ' + equilvalent_name.capitalize()
                
            elif self.jurisdiction_type == 'CI' or self.jurisdiction_type == 'CINP' or self.jurisdiction_type == 'U' or self.jurisdiction_type == 'SCFO':
                str_return = self.name
            else:
                str_return = self.name          
            
        return str_return
       
    def get_name_for_url(self):
        '''
        convert space character ' ' to dash '-'
        remove other characters that must be encoded
        append -[county equivelent word] where applicable
        append -[state abbr]
        replace multiple dash characters '--' with a single dash '-' until no multiple dashes remain
        convert string to lower case
        '''
        
        if self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'SC' or self.jurisdiction_type == 'CONP':
            equilvalent_name = self.get_county_equivalent_name()
                
            name = self.name.replace(' ', '-') + '-'+equilvalent_name+'-' + self.state
        else:
            # will need to check for same city name in same state but diff counties
            name = self.name.replace(' ', '-') + '-' + self.state
        
        name = re.sub('[^0-9a-zA-Z-]+', '', name)
        while name.find('--') >= 0:
            name = name.replace('--', '-')
         
        name = name.lower()        
        
        #return entity_decode(name)
        return name
    
    def get_county_equivalent_name(self):
        equivalent_name = ''
        
        if self.jurisdiction_type == 'CC' or self.jurisdiction_type == 'CO' or self.jurisdiction_type == 'SC' or self.jurisdiction_type == 'CONP':
            if self.state.lower() == 'ak':
                equivalent_name = 'borough'
            elif self.state.lower() == 'la':
                equivalent_name = 'parish'
            else:
                equivalent_name = 'county'
        
        return equivalent_name
        
    #change state display from long form to 2 letters
    def get_state_display(self, form='short'):
        if form == 'long':
            return dict(US_STATES)[self.state] 
        else:
            return self.state
        
    def get_city_jurisdictions_by_county(self):
        jurisdictions = Jurisdiction.objects.filter(parent = self.id, state = self.state, jurisdiction_type__in=('CI', 'U')).order_by('name')
        return jurisdictions
    
    def get_city_jurisdictions_by_county_name(self):
        jurisdictions = Jurisdiction.objects.filter(county = self.county, state = self.state, jurisdiction_type__in=('CI', 'U')).order_by('name')
        return jurisdictions    
    
    def get_formatted_jurisdiction_address(self, address):
        str_address = ''
        address1 = ''
        address2 = ''
        city = ''
        state = ''
        zip_code = ''
        
        if address:
            if 'free-form' in address:
                if address.get('free-form') != None and address.get('free-form') != '':
                    str_address = address.get('free-form')
            else:
                for address_key in address.keys():
                    if str(address_key) == 'address1':
                        address1 = address.get(address_key)
                    elif str(address_key) == 'address2':
                        address2 = address.get(address_key)                
                    elif str(address_key) == 'city':
                        city = address.get(address_key) 
                    elif str(address_key) == 'state':
                        state = address.get(address_key) 
                    elif str(address_key) == 'zip_code':
                        zip_code = address.get(address_key) 
                        
                if address2 == '' or address2 == None:
                    str_address = str(address1)  + ', ' + str(city) + ', ' + str(state) + ' ' + str(zip_code)                   
                else:
                    str_address = str(address1) + ', ' + str(address2) + ', ' + str(city) + ', ' + str(state) + ' ' + str(zip_code)         
                
        return str_address  
    
    def get_formatted_jurisdiction_dept_hours(self, dept_hours): 
        #hours = dept_hours['open_hour'] + ':' + dept_hours['open_min'] + ' ' + dept_hours['open_am_pm']
        #hours += " - " + dept_hours['close_hour'] + ':' + dept_hours['close_min'] + ' ' + dept_hours['close_am_pm']         
        hours = dept_hours['from_hour'] + ':' + dept_hours['from_min'] + ' ' + dept_hours['from_am_pm']
        hours += " - " + dept_hours['to_hour'] + ':' + dept_hours['to_min'] + ' ' + dept_hours['to_am_pm']         
        
        return hours
    
    def get_formatted_jurisdiction_permit_cost(self, permit_cost):
        permit_cost_text = ''
        if 'flat_rate_amt' in permit_cost:
            if permit_cost['flat_rate_amt'] != ''  and permit_cost['flat_rate_amt'] != None:        
                permit_cost_text +=     "Flat rate of $ "+permit_cost['flat_rate_amt']+"<br/>"

        if 'percentage_of_total_system_cost' in permit_cost:
            if permit_cost['percentage_of_total_system_cost'] != '' and permit_cost['percentage_of_total_system_cost'] != None:
                if permit_cost_text != '':
                    permit_cost_text += "plus<br/>"
                
                permit_cost_text += permit_cost['percentage_of_total_system_cost'] +"% of the total system cost "
                if 'percentage_of_total_system_cost_cap' in permit_cost and 'percentage_of_total_system_cost_cap_amt' in permit_cost: 
                    if permit_cost['percentage_of_total_system_cost_cap'] == 'yes' and permit_cost['percentage_of_total_system_cost_cap_amt'] != '':
                        permit_cost_text +=", capped at $ "+permit_cost['percentage_of_total_system_cost_cap_amt']+"<br/>"
                    
        if 'fee_per_inverter' in permit_cost and permit_cost['fee_per_inverter'] != '' and permit_cost['fee_per_inverter'] != None:                    
            if permit_cost_text != '':
                permit_cost_text += "plus<br/>"             
                    
            permit_cost_text += "$ "+permit_cost['fee_per_inverter']+" per inverter<br/>"

        if 'fee_per_module' in permit_cost and permit_cost['fee_per_module'] != '' and permit_cost['fee_per_module'] != None:                    
            if permit_cost_text != '':
                permit_cost_text += "plus<br/>"             
                    
            permit_cost_text += "$ "+permit_cost['fee_per_module']+" per module<br/>"
            
             
                                                   
        if 'fee_per_major_components' in permit_cost and permit_cost['fee_per_major_components'] != '' and permit_cost['fee_per_major_components'] != None:                    
            if permit_cost_text != '':
                permit_cost_text += "plus<br/>"    
                    
            permit_cost_text += "$ "+permit_cost['fee_per_major_components']+" per other major component<br/>"
            
        if 'fee_per_component_cap' in permit_cost and 'fee_per_component_cap_cap_amt' in permit_cost: 
            if permit_cost['fee_per_component_cap'] == 'yes' and permit_cost['fee_per_component_cap_cap_amt'] != '':
                permit_cost_text +=", capped at $ "+permit_cost['fee_per_component_cap_cap_amt']+"<br/>"           
                                        
        if 'jurisdiction_cost_recovery_notes' in permit_cost and permit_cost['jurisdiction_cost_recovery_notes'] != '' and permit_cost['jurisdiction_cost_recovery_notes'] != None:               
            if permit_cost_text != '':                
                permit_cost_text += "plus<br/>"
                 
            permit_cost_text += "Jurisdiction cost recovery:<br/>"
            permit_cost_text += permit_cost['jurisdiction_cost_recovery_notes']
        
        return permit_cost_text
    
    def get_formatted_jurisdiction_accepts_electronic_submissions(self, data):
        text = "<div>"+data['accepts_electronic_submissions']+"</div>"
        if 'accepts_electronic_submissions' in data and data['accepts_electronic_submissions'] != 'No':
            if data['url_or_email_for_submissions'] == 'url':
                if 'url_for_online_submissions' in data and data['url_for_online_submissions'] != None:
                    text += "<div>"+data['url_for_online_submissions']+"</div>"
            elif data['url_or_email_for_submissions'] == 'email':
                if 'email_address_for_online_submissions' in data and data['email_address_for_online_submissions'] != None:
                    text += "<div>"+data['email_address_for_online_submissions'] +"</div>"
                 
             
            text +="</br>"
            if 'accepts_electronic_submissions' in data and data['accepts_electronic_submissions'] == 'Yes, with exceptions' :
                text +="<div>Except for:</div>"
                if 'depends_on_system_rating' in data and data['depends_on_system_rating'] == 'yes' :
                     text +="<div>Depends on system rating</div>"

                if 'depends_on_segment' in data and data['depends_on_segment'] == 'yes' :
                     text +="<div>Depends on segment</div>"
               
                if 'accepts_electronic_submissions_note' in data and data['accepts_electronic_submissions_note'] != None:
                    text +="<p>"+data['accepts_electronic_submissions_note']+"</p>"
        return text        
    
    def user_favorite_jurisdiction(self, user):
        if user.id == None:
            return False
        uf = UserFavorite.objects.filter(user = user.pk, entity_name = 'Jurisdiction', entity_id = self.id)
        if len(uf) > 0:
            return True
        return False
    
    def getLatestUpdates(self):
        from website.models import AnswerReference
        updates = AnswerReference.objects.filter(jurisdiction = self)
        return updates
    
    def display_last_contributed(self):
        datetime_util_obj = DatetimeHelper(self.last_contributed)
        last_contributed_datetime= datetime_util_obj.showStateTimeFormat(self.state)  
              
        return last_contributed_datetime
    
    def __unicode__(self):
        return self.name_for_url
    class Meta:
        app_label = 'website'
"""        
    def rate(category_name, eid):
        vote_info = get_voting_tally(category_name, eid)
        rating = vote_info['total_pos_votes'] - vote_info['total_neg_vote']
        #print "rating = " + rating
        answer_reference_obj = AnswerReference.objects.get(id=eid)
        print answer_reference_obj
        answer_reference_obj.rating = rating
        answer_reference_obj.save()
        return True
"""
class Zipcode(models.Model):
    zip_code = models.CharField(max_length=10, blank=False, null=False, db_index=True)
    state = models.CharField(choices=STATE_CHOICES, max_length=2, blank=True, null=True, db_index=True)    
    city = models.CharField(max_length=64, blank=True, null=True, db_index=True) #if for a city
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_index=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True, db_index=True)
    #for some reason, county column is not in the db, removing from model also
    county = models.CharField(max_length=64, blank=True, null=True, db_index=True) #if within a county    
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    def __unicode__(self):
        return self.zip_code
    class Meta:
        app_label = 'website'
