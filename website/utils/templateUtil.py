import os
import datetime
import math
from django.contrib.localflavor.us.us_states import US_STATES
from django.conf import settings
from website.models import Jurisdiction, JURISDICTION_TYPE_CHOICES

class TemplateUtil():
    GENERATED_DIR = '/website/generated/' #directory for generated templates
    WARNING_HTML = '<!-- This file is updated automatically.  Do not manually modify. -->\n'
    
    strMsg = ''
    
    def update_site_map(self):
        
        datetime_now = datetime.datetime.now()
        datetime_now_text = datetime_now.strftime('%Y-%m-%d %H:%M:%S')
        
        for abbreviation, name in US_STATES:
            
            templatePath = settings.TEMPLATE_DIRS[0] + self.GENERATED_DIR + 'site_map_list_' + abbreviation + '.html'
            filePointer = file(templatePath, 'w')
            
            filePointer.write(self.WARNING_HTML)
            filePointer.write('<!-- Updated: ' + datetime_now_text + ' -->\n') #record updated datetime in template
            
            jurisdiction_type_groups = []
            jurisdiction_type_group = {'name': 'State',
                                       'ids': ['S'],
                                       'label': 'State Locations'}
            jurisdiction_type_groups.append(jurisdiction_type_group)
            jurisdiction_type_group = {'name': 'County',
                                       'ids': ['CO', 'SC', 'CONP', 'CC'],
                                       'label': 'County Locations'}
            jurisdiction_type_groups.append(jurisdiction_type_group)
            jurisdiction_type_group = {'name': 'County Field Offices',
                                       'ids': ['SCFO'],
                                       'label': 'County Field Offices'}
            jurisdiction_type_groups.append(jurisdiction_type_group)
            jurisdiction_type_group = {'name': 'Cities',
                                       'ids': ['CI', 'CINP', 'IC'],
                                       'label': 'City Locations'}
            jurisdiction_type_groups.append(jurisdiction_type_group)
            jurisdiction_type_group = {'name': 'Unincorporated',
                                       'ids': ['U'],
                                       'label': 'Unincorporated Locations'}
            jurisdiction_type_groups.append(jurisdiction_type_group)
            
            
            #for type_id, type_name in JURISDICTION_TYPE_CHOICES:
            for jurisdiction_type_group in jurisdiction_type_groups:
        
                jurisdictions = Jurisdiction.objects.filter(state=abbreviation, jurisdiction_type__in=jurisdiction_type_group['ids']).order_by('name')
                #jurisdictions = Jurisdiction.objects.filter().order_by('state', 'city')[0:100] #limit it for testing
                
                if len(jurisdictions) > 0:
                    filePointer.write('<h3>' + jurisdiction_type_group['label'] + '</h3>\n')
                    
                    filePointer.write('<ul class="cssTable fullSpace">\n')
                    
                    items_per_column = math.ceil(float(len(jurisdictions)) / settings.PAGE_COLUMNS)
                    '''if abbreviation == 'IL':
                        print str(len(jurisdictions)) + ' items_per_column: ' + str(items_per_column)'''
                    
                    count = 0
                    for jurisdiction in jurisdictions:
                        if count == 0: #start a column
                            filePointer.write('<li class="cssCell">\n')
                            filePointer.write('<ul>\n')
                        output_line = '<li><a href="/jurisdiction/' + jurisdiction.name_for_url + '">' + jurisdiction.show_jurisdiction() + '</a></li>\n'
                        filePointer.write(output_line)
                        count += 1
                        if count >= items_per_column: #end a column
                            filePointer.write('</ul>\n')
                            filePointer.write('</li>\n')
                            count = 0
                    if count > 0: #if there's remaining items in last column
                        filePointer.write('</ul>\n')
                        filePointer.write('</li>\n')
                    filePointer.write('</ul>\n')
                
            filePointer.close()
        
            self.strMsg += str(len(jurisdictions)) + ' jurisdictions saved into ' + self.GENERATED_DIR + 'site_map_list_' + abbreviation + '.html<br>'
    
    def generated_template_exist(self, filename):
        templatePath = settings.TEMPLATE_DIRS[0] + self.GENERATED_DIR + filename
        return os.path.isfile(templatePath)
    
    def generated_state_exist(self, abbreviation):
        templatePath = settings.TEMPLATE_DIRS[0] + self.GENERATED_DIR + 'site_map_list_' + abbreviation + '.html'
        return os.path.isfile(templatePath)
    
    def generated_state_template_path(self, abbreviation):
        templatePath = self.GENERATED_DIR + 'site_map_list_' + abbreviation + '.html'
        return templatePath
