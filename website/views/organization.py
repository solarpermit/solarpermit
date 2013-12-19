import datetime
import hashlib
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template import Context
from website.utils.httpUtil import HttpRequestProcessor#, decode_jinga_template
from django.views.decorators import csrf
from dajax.core import Dajax
from django.conf import settings as django_settings
from django.core.mail.message import EmailMessage
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.template.loader import get_template
from django.template import Context, RequestContext, Template
from django.db.models import Q
from django.conf import settings
from jinja2 import FileSystemLoader, Environment

from website.utils.mathUtil import MathUtil
from website.models import Organization, RoleType, OrganizationMember, UserDetail
#from sorl.thumbnail.main import get_thumbnail
from sorl.thumbnail import get_thumbnail
from website.utils.fileUploader import qqFileUploader

from website.utils.messageUtil import MessageUtil,add_system_message, get_system_message

ORGANIZATION_PAGE_SIZE = 20

def organization(request):
    requestProcessor = HttpRequestProcessor(request)  
    data = {}
    dajax = Dajax()
    user = request.user
    data['user'] = user
    ajax = requestProcessor.getParameter('ajax')
    if (ajax != None):
        data['ajax'] = ajax #for template to use
        
        #user's active and requested membership, should only have up to one, but just in case can be more
        user_members = OrganizationMember.objects.filter(Q(user=user)&Q(organization__status = 'A')&(Q(status='A')|Q(status='P')))
        data['user_members'] = user_members
        
                    
        if ajax == 'choose_org' or ajax == 'open_choose_org':
            #organizations = Organization.objects.all().order_by('name')[0:ORGANIZATION_PAGE_SIZE]
            organizations = Organization.objects.filter(status = 'A').order_by('name')[0:ORGANIZATION_PAGE_SIZE]
            data['next_page_param'] = 'page=2'
            data['search_param'] = ''
            data['organizations'] = organizations
            
            member_orgs = OrganizationMember.objects.filter(user = user, status = 'A', organization__status = 'A')
            
            if len(member_orgs) == 0:
                data['can_create_org'] = 'true'
            else:
                data['can_create_org'] = 'false'
                
            body = requestProcessor.decode_jinga_template(request, 'website/organizations/organization_select.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/organization_select.js', data, '')
            dajax.script(script)
            #need the organization list js also
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/organization_list.js', data, '')
            dajax.script(script)
            
        if ajax == 'search_org':
            text = requestProcessor.getParameter('text')
            if text == None:
                text = ''

            sort_dir = requestProcessor.getParameter('sort_dir')  
            sort_by_date_added_dir = requestProcessor.getParameter('sort_by_date_added_dir')   
            
            if sort_dir == None and sort_by_date_added_dir == None:
                data['sort_dir']  = '&sort_dir='+str(sort_dir)
                order_by_str = 'name'
              
            if sort_dir != None and sort_by_date_added_dir == None:
                data['sort_dir']  = '&sort_dir='+str(sort_dir)
                if sort_dir == 'desc':
                    order_by_str = '-name'
                else:
                    order_by_str = 'name'      
                
            if sort_dir == None and sort_by_date_added_dir != None:
                data['sort_by_date_added_dir']  = '&sort_by_date_added_dir='+str(sort_by_date_added_dir)
                if sort_by_date_added_dir == 'desc':
                    order_by_str = '-create_datetime'
                else:
                    order_by_str = 'create_datetime'       
                    
            if sort_dir != None and sort_by_date_added_dir != None:
                data['sort_dir']  = '&sort_dir='+str(sort_dir)
                if sort_dir == 'desc':
                    order_by_str = '-name'
                else:
                    order_by_str = 'name'       
                    
            print order_by_str                                                         

            if text != '':
                organizations = Organization.objects.filter(name__icontains=text, status = 'A').order_by(order_by_str)[0:ORGANIZATION_PAGE_SIZE]
            else:
                organizations = Organization.objects.filter(status = 'A').order_by(order_by_str)[0:ORGANIZATION_PAGE_SIZE]
                
            data['next_page_param'] = 'page=2'
            data['search_param'] = '&text='+text
            #data['sort_dir']  = '&sort_dir='+str(sort_dir)
            data['organizations'] = organizations

            body = requestProcessor.decode_jinga_template(request,'website/organizations/organization_list.html', data, '')
            dajax.assign('#org_list','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/organization_list.js', data, '')
            dajax.script(script)

            return HttpResponse(dajax.json())
        
        if 'select_users' in ajax:
            data['orgid'] = requestProcessor.getParameter('orgid')
            try:
                organization = Organization.objects.get(id=data['orgid'])
            except:
                organizations = Organization.objects.all()[:1]
                organization = organizations[0]
            data['organization'] = organization
            
            data['user_list'] = get_user_list('', 1)
            data['search_param'] = ''
            data['next_page_param'] = 'page=2'
            
            body = requestProcessor.decode_jinga_template(request, 'website/organizations/users_select.html', data, '')
            dajax.assign('#secondDialogDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/users_select.js', data, '')
            dajax.script(script)
            #need the user list js also
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/users_select_list.js', data, '')
            dajax.script(script)
            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
                    
        if ajax == 'search_user':
            data['orgid'] = requestProcessor.getParameter('orgid')
            try:
                organization = Organization.objects.get(id=data['orgid'])
            except:
                organizations = Organization.objects.all()[:1]
                organization = organizations[0]
            data['organization'] = organization
            
            text = requestProcessor.getParameter('text')
            if text == None:
                text = ''
            data['user_list'] = get_user_list(text, 1)
            data['next_page_param'] = 'page=2'
            data['search_param'] = '&text='+text
            
            body = requestProcessor.decode_jinga_template(request,'website/organizations/users_select_list.html', data, '')
            dajax.assign('#user_list','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/users_select_list.js', data, '')
            dajax.script(script)
            
            return HttpResponse(dajax.json())
        
        if (ajax == 'create_org'):
            form_id = 'form_create_org'      
            data['form_create_org_id'] = form_id
            
            user = User.objects.get(id=request.user.id)
                              
            data['name'] = requestProcessor.getParameter('name')    
            data['logo'] = requestProcessor.getParameter('logo')  
            data['website'] = requestProcessor.getParameter('website')      
            data['username'] = user.username
            data['caller'] = requestProcessor.getParameter('caller') 
            
            if data['name'] == None:
                data['name'] = ''   
            if data['logo'] == None:
                data['logo'] = ''   
            if data['website'] == None:
                data['website'] = ''                                                      
            #body = decode_template('website/accounts/create_account.html', data) 
            body = requestProcessor.decode_jinga_template(request,'website/organizations/create_org.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/create_org.js', data, '')
            dajax.script(script)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            return HttpResponse(dajax.json())  
        
        if (ajax == 'create_org_submit'):  
            data = {}       

            form_id = 'form_create_org'
            data['form_create_org_id'] = form_id

            data['name'] = requestProcessor.getParameter('name')    
            data['logo'] = requestProcessor.getParameter('logo')  
            data['website'] = requestProcessor.getParameter('website')   
            
            data['caller'] = requestProcessor.getParameter('caller')                          
                               
            error_message = validate_create_org_form_data(data, form_id)
     
            if len(error_message) == 0:
                msg_key = form_id + '_fail_reason'     
         
                #try:
                
                org = Organization()
                org.name = data['name']
                #org.logo = data['logo']
                org.website = data['website']
                org.save()
                    
                role_types = RoleType.objects.filter(name__iexact='Administrator')
                if role_types:
                    owner_role_type = role_types[0]
                    org_member = OrganizationMember()
                    org_member.organization_id = org.id
                    org_member.role_id = owner_role_type.id
                    org_member.user_id = request.user.id
                    org_member.display_order = 1    
                    org_member.status = 'A'          
                    org_member.join_date = datetime.datetime.now()         
                    org_member.save()

                    #messageUtil = MessageUtil('success_create_org')
                    #data['system_message_type'] = messageUtil.get_system_message_type()   # optional
                    #data['system_message_text'] = messageUtil.get_system_message_text() 
                    #dajax.script('jQuery.fancybox.close();')  
                    #dajax.script("controller.showMessage('"+data['system_message_text']+"','"+data['system_message_type']+"');")
                    
                store_file_name = requestProcessor.getParameter('file_store_name')
                if store_file_name != '' and store_file_name != None:
                    store_file = '/upfiles/org_logos/'+store_file_name
                    org.logo = store_file
                    org.save()
                    full_path = django_settings.MEDIA_ROOT+'/upfiles/org_logos/'+store_file_name
                    try:
                        full_image = get_thumbnail(full_path,'140x140', quality=99)
                        original_image = full_image.url
       
                        #img_or = pil.open(django_settings.MEDIA_ROOT+'/'+original_image, 'r')
                  
                        #img = img_or
        
                        #img.save(django_settings.MEDIA_ROOT+'/upfiles/org_logos_scaled/'+store_file_name)
           
                    except:
                        pass


                    
                    

                user = request.user
                data['user'] = user
                org_member_obj = OrganizationMember()
                data_org_members =  org_member_obj.get_user_orgs(user)                          
                data['orgmembers'] = data_org_members['orgmembers'] 
                data['orgmembers_invite'] = data_org_members['orgmembers_invite']
                body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
                dajax.assign('#my_org_list','innerHTML', body)   
                script = requestProcessor.decode_jinga_template(request, 'website/form_fields/org.js', data, '')
                dajax.script(script)                 
                
                                                    
                user_org_in_header_body = "<a id='update_org_info_link' href='#' data-ajax='open_org_details' data-orgid='"+str(org.id)+"' >"+str(org.name)+"</a>"         
                dajax.assign('#user_org','innerHTML', user_org_in_header_body)      

                data['orgid'] = org.id                     

                data['mode'] = 'individual'
                
                org_details_data = get_data_for_org_details(org_member.organization, request)
                for key in org_details_data.keys():
                    data[key] = org_details_data.get(key)
                    
                data['form_id'] = 'form_org_details'                    
                body = requestProcessor.decode_jinga_template(request,'website/organizations/org_details.html', data, '')       
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_details.js', data, '')
                dajax.script(script)   
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
                dajax.script(script)                  

                return HttpResponse(dajax.json())                                                        
                
                #except Exception, e:
                    #print e.message
                    #error_message[msg_key] = e.message
                    #print data

            if len(error_message) > 0:
                for msg_key in error_message.keys():
                    data[msg_key] = error_message.get(msg_key)  
                    
            body = requestProcessor.decode_jinga_template(request,'website/organizations/create_org.html', data, '')             
            dajax.assign('#fancyboxformDiv','innerHTML', body)

            return HttpResponse(dajax.json())          
        
        
        if ajax == 'org_details' or ajax == 'open_org_details' or ajax == 'choose_org_details':                                  
            data['orgid'] = requestProcessor.getParameter('orgid')
            try:
                org = Organization.objects.get(id=data['orgid'])
            except:
                org = Organization() #just get a new org for now
                            
            user = request.user
            orgmembers = OrganizationMember.objects.filter(organization = org, user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R')         
            if orgmembers and len(orgmembers) > 0:
                orgmember = orgmembers[0]
            else:
                orgmember = None
                
            if org.logo != None and org.logo !='':
                full_path = django_settings.MEDIA_ROOT+ str(org.logo)
                try:
                    data['thum'] = get_thumbnail(full_path,'140x140', quality=99)
                except: #in case file missing, don't crash
                    data['thum'] = ''
            else:
                data['thum'] = ''
                
            data['orgmember'] = orgmember
            data['organization'] = org
            data['orgname'] = org.name             
            data['website'] = org.website
            data['mode'] = 'individual'
            data['access'] = get_org_access(user, org)
            data['date_type'] = 'join'
            members = get_members(org, 1)
            data['members'] = members
            data['next_page_param'] = 'page=2'
            
            org_admins = OrganizationMember.objects.filter(organization=org, role__name='Administrator').order_by('user__username')
            data['org_admins'] = org_admins   
                            
            body = requestProcessor.decode_jinga_template(request,'website/organizations/org_details.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_details.js', data, '')
            dajax.script(script)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
            dajax.script(script)
        
        if (ajax == 'org_details_submit'):      
            error_message = {}
            data['div'] = requestProcessor.getParameter('div')               
            data['orgid'] = requestProcessor.getParameter('orgid')            
            data['mode'] = requestProcessor.getParameter('mode')  
            orgname = requestProcessor.getParameter('orgname')    
            website = requestProcessor.getParameter('website')              
            logo = requestProcessor.getParameter('logo')                
    
            try:
                org = Organization.objects.get(id=data['orgid'])
            except:
                org = Organization() #just get a new org for now
                            
            user = request.user
            orgmembers = OrganizationMember.objects.filter(organization = org, user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R')         
            if orgmembers and len(orgmembers) > 0:
                orgmember = orgmembers[0]
            else:
                orgmember = None
                  
            data['orgmember'] = orgmember
                                
            if orgname != None:
                org.name = orgname
                
            if website != None:     
                org.website = website           
                
                
            store_file_name = requestProcessor.getParameter('file_store_name')
            if store_file_name != '' and store_file_name != None:
                store_file = '/upfiles/org_logos/'+store_file_name
                org.logo = store_file
                org.save()
                full_path = django_settings.MEDIA_ROOT+'/upfiles/org_logos/'+store_file_name
                try:
                    full_image = get_thumbnail(full_path,'140x140', quality=99)
                    original_image = full_image.url
                    #img_or = pil.open(django_settings.MEDIA_ROOT+'/'+original_image, 'r')

                    #img.save(django_settings.MEDIA_ROOT+'/upfiles/org_logos_scaled/'+store_file_name)
                except:
                    pass                   
                        
                                
            org.save()
            
            if org.logo != None and org.logo !='':
                full_path = django_settings.MEDIA_ROOT+ str(org.logo)
                try:
                    data['thum'] = get_thumbnail(full_path,'140x140', quality=99)
                except:
                    data['thum'] = ''
            else:
                data['thum'] = ''
                    
            data['organization'] = org            
            data['orgname'] = org.name     
            data['website'] = org.website 
            
            data['organization'] = org                                

            members = get_members(org, 1)
            data['members'] = members
            data['next_page_param'] = 'page=2'
            data['date_type'] = 'join'
            
            user = request.user
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                          
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)  
            
            user_org_in_header_body = "<a id='update_org_info_link' href='#' data-ajax='open_org_details' data-orgid='"+str(org.id)+"' >"+str(org.name)+"</a>"         
            dajax.assign('#user_org','innerHTML', user_org_in_header_body)               
            
            org_admins = OrganizationMember.objects.filter(organization=org, role__name='Administrator').order_by('user__username')
            data['org_admins'] = org_admins               
                            
            data['access'] = get_org_access(user, org)
            body = requestProcessor.decode_jinga_template(request,'website/organizations/org_details.html', data, '') 
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_details.js', data, '')
            dajax.script(script)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
            dajax.script(script)
            script = requestProcessor.decode_jinga_template(request, 'website/form_fields/org.js', data, '')
            dajax.script(script)
            return HttpResponse(dajax.json())     
        if ajax == 'org_details_members_change':
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            changed_members = requestProcessor.getParameter('changed_members')
            changed_members_list = []
            if changed_members != None and changed_members != '':
                changed_members_list = changed_members.split(',')
            admin_role = RoleType.objects.get(name='Administrator')
            member_role = RoleType.objects.get(name='Member')
            email_data = {}
            
            #handle remove members 1st
            removed_members = requestProcessor.getParameter('removed_members')
            removed_members_list = []
            if removed_members != None and removed_members != '':
                removed_members_list = removed_members.split(',')
            for remove_mid in removed_members_list:
                org_member = OrganizationMember.objects.get(id = remove_mid)
                org_member.status ='RM'
                org_member.save()
                #send email, except oneself
                if org_member.user != user:
                    try:
                        email_data = {}
                        email_data['member_me'] = org_member
                        email_data['site_url'] = settings.SITE_URL
                        to_mail = [org_member.user.email]
                        subject = 'Removed from '+ org.name
                        template = 'remove_member_org.html'
                        send_org_email(email_data, to_mail, subject,  template)
                    except:
                        print('Failed to send remove from org email to ' + org_member.user.email)
            
            role_list = []
            members_list = []
            for member_text in changed_members_list:
                member_info_list = member_text.split(':');
                member_id = member_info_list[0]
                role_name = member_info_list[1]
                role_list.append(role_name)
                members_list.append(member_id)
            
            change_access = change_right_access(members_list, role_list, org)
            
            if change_access:
                for member_text in changed_members_list:
                    member_info_list = member_text.split(':');
                    member_id = member_info_list[0]
                    role_name = member_info_list[1]
                    #if already removed earlier, don't bother
                    if member_id in removed_members_list:
                        continue #skip to next one
                    
                    member = OrganizationMember.objects.get(id=member_id)
                    if role_name == 'Administrator':
                        role_type = admin_role
                    else:
                        role_type = member_role
                    member.role = role_type
                    member.save()
                    
                    #email to users who has role changed, except oneself
                    if member.user != user:
                        try:
                            email_data = {}
                            email_data['username'] = user.username
                            email_data['member_me'] = member
                            email_data['invited_username'] = member.user.username
                            email_data['org_name'] = member.organization.name
                            email_data['site_url'] = settings.SITE_URL
                            email_data['right'] = role_type.name
                            to_mail = [member.user.email]
                            subject = 'Change right in '+ org.name
                            template = 'change_org_right.html'
                            send_org_email(email_data, to_mail, subject,  template)
                        except:
                            print('Failed to send role change email to ' + member.user.email)
                
                dajax.script('jQuery.fancybox.close();')  
                dajax.script("controller.showMessage('Changes saved.', 'success')") 
            else:
                dajax.script('jQuery.fancybox.close();') 
                dajax.script("controller.showMessage('Can not Change all Administrator to Member.', 'error')") 
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'delete_org'):
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)  
            org.status = 'D'
            org.save()              
            
            send_delete_org_email(request.user, org)
            
            user = request.user
            
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                          
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)     
            script = requestProcessor.decode_jinga_template(request, 'website/form_fields/org.js', data, '')
            dajax.script(script)             
            
            user_org_in_header_body = "<a href='#' id='update_org_info_link' data-ajax='open_choose_org' title='Tip: Help your organization gain recognition by listing it in your profile'>Update your Organization Info</a>"         
            dajax.assign('#user_org','innerHTML', user_org_in_header_body)    
            
            dajax.script('jQuery.fancybox.close();')  
  
            
            dajax.script("controller.showMessage('"+org.name+" deleted.', 'success')")                 
            return HttpResponse(dajax.json()) 
                    
                    
        if (ajax == 'add_org_to_myprofile'):
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            
            #prevent user who already requested or belong to another org
            for user_member in user_members:
                if user_member.organization != org:
                    dajax.script("controller.showAlert({title: '', message: 'You cannot join this company or organization because you are already a member or a pending member of "+user_member.organization.name+".'});")
                    return HttpResponse(dajax.json())
            
            org_members = OrganizationMember.objects.filter(organization = org, user = user)
            email_data ={}
            email_data['site_url'] = settings.SITE_URL
            subject = 'Request to Join '+ org.name
            #to_mail = get_org_admin_email(org)
            admins = get_org_admin(org)
            if len(org_members) > 0:
                org_member = org_members[0]
                if org_member.status != 'A':
                    org_member.status = 'P'
                    org_member.requested_date = datetime.datetime.now()
                    org_member.save()
                    email_data['member_me'] = org_member
                    #send email to org admin                    
                    #send_org_email(email_data, to_mail, subject,  'request_org.html')
            else:
                org_member = OrganizationMember()
                org_member.organization = org
                org_member.user = user
                org_member.status = 'P'
                role_type = RoleType.objects.get(name__iexact='Member')
                org_member.role = role_type
                org_member.requested_date = datetime.datetime.now()
                org_member.save()
                email_data['member_me'] = org_member
                #send email to org admin
                #send_org_email(email_data, to_mail, subject,  'request_org.html')
            #send email to org admin
            for admin in admins:
                to_mail = [admin.email]
                email_data['username'] = admin.username
                email_data['orgid'] = org_id
                send_org_email(email_data, to_mail, subject,  'request_org.html')
                
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                        
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body) 
            
            script = requestProcessor.decode_jinga_template(request, 'website/form_fields/org.js', data, '')
            dajax.script(script)            
                            
            '''    
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite               

            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)   
            '''
                                       
            dajax.script('jQuery.fancybox.close();')  
             
            dajax.script("controller.showMessage('A request to join "+org.name+" has been sent to the company or organization administrator.', 'success')")                
            dajax.script('controller.updateUrlAnchor("#join_organization");')
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'pending_request'):
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            org_members = OrganizationMember.objects.filter(organization = org, status = 'P')
            
            data['access'] = 'Admin'
            data['members'] =  org_members
            data['organization'] = org
            data['date_type'] = 'requested'
            
            body = requestProcessor.decode_jinga_template(request,'website/organizations/org_pending_requests.html', data, '') 
            dajax.assign('#tabs-2','innerHTML', body)    
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_pending_requests.js', data, '')
            dajax.script(script)
            #need to add js for the member list
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
            dajax.script(script)                  
            return HttpResponse(dajax.json())
        
        if (ajax == 'handle_pending_request'):
            member_id = requestProcessor.getParameter('mid')
            type = requestProcessor.getParameter('type')
            org_member = OrganizationMember.objects.get(id = member_id)
            org = org_member.organization
            email_data ={}
            email_data['site_url'] = settings.SITE_URL
            email_data['username'] = user.username
            to_mail = [org_member.user.email]
            
            if type == 'approve':
                org_member.status = 'A'
                org_member.join_date = datetime.datetime.now()
                subject = 'Approve to Join '+ org.name
                template = 'approve_request_org.html'
                text = 'Approved'
            else:
                org_member.status = 'R'
                subject = 'Reject to Join '+ org.name
                template = 'reject_member_org.html'
                text = 'Denied'
            org_member.save()
            email_data['member_me'] = org_member
            
            send_org_email(email_data, to_mail, subject,  template)
            
            dajax.assign('#action_dev_'+member_id, 'innerHTML', '<span>'+text+'</span>')
            
        if (ajax == 'cancel_org_request'):
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            email_data ={}
            try:
                org_member = temp_member = OrganizationMember.objects.get(organization = org, user = user, status = 'P')
                org_member.delete()
                email_data['member_me'] = temp_member
                subject = 'Cancel to Join '+ org.name
                template = 'cancel_org_request.html'
                admins = get_org_admin(org)
                for admin in admins:
                    to_mail = [admin.email]   
                    email_data['username'] = admin.username             
                    send_org_email(email_data, to_mail, subject,  template)
            except:
                org_member = OrganizationMember()
            
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                        
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)               
            '''
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'  
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite               

            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)             
            '''
            dajax.script('jQuery.fancybox.close();')  
  
            
            dajax.script("controller.showMessage('Request to join "+org.name+" cancelled.', 'success')")                
            return HttpResponse(dajax.json()) 
        
        if (ajax == 'remove_from_my_profile'):
            member_id = requestProcessor.getParameter('mid')
            org_member = OrganizationMember.objects.get(id = member_id)
            organization = org_member.organization
            data['organization'] = organization
            
            #is member an admin?
            if org_member.status == 'A':
                if org_member.role.name == 'Administrator':
                    other_admins = OrganizationMember.objects.filter(organization=org_member.organization, status='A', role__name='Administrator').exclude(id=member_id).order_by('user__username')
                    #if there are other admins, allow
                    if len(other_admins) == 0:
                        #if no other admin, are there other members?  then reassign admin
                        other_members = OrganizationMember.objects.filter(organization=org_member.organization, status='A', role__name='Member').exclude(id=member_id).order_by('user__username')
                        if len(other_members) == 0:
                            #cannot, no other members, but can delete
                            dajax.script("controller.showAlert({title: 'Warning', message: 'There is no one else in this organization, please delete instead.'});")
                            return HttpResponse(dajax.json())
                        else:
                            #assign to others
                            data['other_members'] = other_members
                            body = requestProcessor.decode_jinga_template(request, 'website/organizations/admin_select.html', data, '')
                            dajax.assign('#secondDialogDiv','innerHTML', body)
                            script = requestProcessor.decode_jinga_template(request, 'website/organizations/admin_select.js', data, '')
                            dajax.script(script)
                            dajax.script('controller.showSecondDialog("#secondDialogDiv");')
                            
                            return HttpResponse(dajax.json())
            
            org_member.status ='RM'
            org_member.save()          
            
            user = request.user
            
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                        
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)               
            '''
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'  
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite               

            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)    
            '''
            
            user_org_in_header_body = "<a href='#' id='update_org_info_link' data-ajax='open_choose_org' title='Tip: Help your organization gain recognition by listing it in your profile'>Update your Organization Info</a>"         
            dajax.assign('#user_org','innerHTML', user_org_in_header_body)               
            
            dajax.script('jQuery.fancybox.close();')  
            dajax.script("controller.showMessage('"+org_member.organization.name+" removed from your profile.', 'success')")                  
            return HttpResponse(dajax.json())               
            
        if ajax == 'assign_new_remove_me':
            member_id = requestProcessor.getParameter('mid')
            new_admin = OrganizationMember.objects.get(id = member_id)
            organization = new_admin.organization
            data['organization'] = organization
            
            #make this member admin
            admin_role = RoleType.objects.get(name='Administrator')
            new_admin.role = admin_role
            new_admin.save()
            
            #remove current user from org
            user = request.user
            member_me = OrganizationMember.objects.get(organization=organization, user=user)
            member_me.status ='RM'
            member_me.save()
            
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                          
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)               
            
            # send email to newly assigned admin
            email_data = {}
            email_data['invited_username'] = new_admin.user.username
            email_data['username'] = user.username
            email_data['org_name'] = organization.name
            email_data['site_url'] = settings.SITE_URL
            email_data['right'] = admin_role.name
            to_mail = [new_admin.user.email]
            subject = 'Change right in '+ organization.name
            template = 'change_org_right.html'
            send_org_email(email_data, to_mail, subject,  template)
            
            '''
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'  
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite               

            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body)    
            '''          
            
            
            dajax.script("controller.closeSecondDialog();")
            dajax.script('jQuery.fancybox.close();')  
            message = organization.name + ' removed from your profile.  The new admin is sent an email alerting them of their status.'
            dajax.script("controller.showMessage('"+message+"', 'success')")                  

            return HttpResponse(dajax.json())               
            
        if (ajax == 'decline_invite'):
            caller = requestProcessor.getParameter('caller')   
            if caller == None:
                caller = 'org_details'       
                            
            member_id = requestProcessor.getParameter('mid')           
            temp_member = org_member = OrganizationMember.objects.get(id = member_id)
            
            org_member.delete()          
            
            user = request.user
            '''
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'  
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite    
            '''
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                         
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)                        
            
            # send email to newly assigned admin
            email_data = {}
            email_data['org_name'] = temp_member.organization.name
            email_data['site_url'] = settings.SITE_URL
            email_data['user'] = user
            to_mail = [temp_member.invitor.email]
            subject = 'Decline the invite from '+ temp_member.organization.name
            template = 'decline_invite_org.html'
            send_org_email(email_data, to_mail, subject,  template)
            
            '''
            data['form_id'] = 'form_user_profile'
            body = requestProcessor.decode_jinga_template(request,'website/accounts/user_profile.html', data, '') 
            dajax.assign('#main_content','innerHTML', body) 
            '''
            if caller == 'org_details':
                org_details_data = get_data_for_org_details(org_member.organization, request)
                for key in org_details_data.keys():
                    data[key] = org_details_data.get(key)

                body = requestProcessor.decode_jinga_template(request,'website/organizations/org_details.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_details.js', data, '')
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
                dajax.script(script)        
            else:            
                dajax.script("controller.showMessage('Invitation declined.', 'success')")              
                             
            return HttpResponse(dajax.json())          
        
        if (ajax == 'accept_invite'):
            member_id = requestProcessor.getParameter('mid')           
            temp_member = org_member = OrganizationMember.objects.get(id = member_id)
            caller = requestProcessor.getParameter('caller')   
            if caller == None:
                caller = 'org_details'                  
            
            if org_member.status == 'AI':
                if org_member.role.name == 'Admin':
                    org_member.status = 'A'
                    message = 'You are now an administrator of '+org_member.organization.name+'.'
                elif org_member.role.name == 'Member':
                    org_member.status = 'A'
                    message = 'You have joined '+org_member.organization.name+'.'
            elif org_member.status == 'MI':
                org_member.status = 'P'
                message = 'A request to join '+org_member.organization.name+' has been sent to the company or organization administrator.'
                
            org_member.save()
            
            user = request.user
            # delete all remaining invites (AI and MI) how to do OR?
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A', status__iexact='AI')        
            if orgmembers:
                for orgmember in orgmembers:
                    orgmember.delete()
                    
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A', status__iexact='MI')        
            if orgmembers:
                for orgmember in orgmembers:
                    orgmember.delete()                    

            '''
            data['userid'] = user.id                
            data['username'] = user.username    
            data['email'] = user.email
            data['mode'] = 'individual'   
            
            orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
            data['orgmembers'] = orgmembers            
            orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
            data['orgmembers_invite'] = orgmembers_invite               
            '''
            org_member_obj = OrganizationMember()
            data_org_members =  org_member_obj.get_user_orgs(user)                         
            data['orgmembers'] = data_org_members['orgmembers'] 
            data['orgmembers_invite'] = data_org_members['orgmembers_invite']        
            
            body = requestProcessor.decode_jinga_template(request,'website/form_fields/org.html', data, '') 
            dajax.assign('#my_org_list','innerHTML', body)                            
                            
            # send email to inviter
            email_data = {}
            email_data['org_name'] = temp_member.organization.name
            email_data['site_url'] = settings.SITE_URL
            email_data['user'] = user
            to_mail = [temp_member.invitor.email]
            subject = 'Accept the invite from '+ temp_member.organization.name
            template = 'accept_invite_org.html'
            send_org_email(email_data, to_mail, subject,  template)
            
            if caller == 'org_details':
                org_details_data = get_data_for_org_details(org_member.organization, request)
                for key in org_details_data.keys():
                    data[key] = org_details_data.get(key)

                body = requestProcessor.decode_jinga_template(request,'website/organizations/org_details.html', data, '') 
                dajax.assign('#fancyboxformDiv','innerHTML', body)
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_details.js', data, '')
                dajax.script(script)  
                script = requestProcessor.decode_jinga_template(request, 'website/organizations/org_member_list.js', data, '')
                dajax.script(script)        
            else:            
                dajax.script("controller.showMessage('"+message+"', 'success')")   
                         
            return HttpResponse(dajax.json())               
                        
        
        if (ajax == 'remove_org_member'):  
            member_id = requestProcessor.getParameter('mid')
            org_member = OrganizationMember.objects.get(id = member_id)
            
            org_member.status ='RM'
            org_member.save()
            dajax.script('$("#id_member_'+str(org_member.id)+'").remove();') 
            
        if (ajax == 'invite_member'):
            users =  requestProcessor.getParameter('users')
            emails = requestProcessor.getParameter('emails')
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            role_type = RoleType.objects.get(name__iexact='Member')
            users_list = []
            if users != None and users != '':
                users_list = users.split(',')
            emails_list = []
            if emails != None and emails != '':
                emails_list = emails.split(',')
            email_data = {}
            email_data['site_url'] = settings.SITE_URL
            email_data['username'] = user.username
            access = get_org_access(user, org)
            
            if access == 'Admin':
                type = 'AI'
            else:
                type = 'MI'
            
            subject = 'Invitation to join '+ org.name  + ' on SolarPermit.org'
            template = 'invite_member.html'
            for uid in users_list:
                user1 = User.objects.get(id = uid)
                try:
                    org_member = OrganizationMember.objects.get(organization = org, user = user1)
                    if org_member.status == 'R' or org_member.status == 'RM':
                        org_member.status = type
                except:            
                    org_member = OrganizationMember()
                    org_member.status = type
                org_member.organization = org
                org_member.user = user1
                org_member.invitor = user                
                org_member.role = role_type
                org_member.requested_date = datetime.datetime.now()
                org_member.save()
                to_mail=[user1.email]
                email_data['member_me'] = org_member
                email_data['type'] = type
                send_org_email(email_data, to_mail, subject,  template)
            
            for mail in emails_list:
                invitation_key = get_invitation_key(mail)
                org_member = OrganizationMember()
                org_member.organization = org
                org_member.email = mail
                org_member.invitor = user
                org_member.status = type                
                org_member.role = role_type
                org_member.requested_date = datetime.datetime.now()
                org_member.invitation_key = invitation_key
                org_member.save()
                to_mail=[mail]
                email_data['to_mail'] = mail
                email_data['org_name'] = org_member.organization.name
                email_data['invitor'] = user.username
                email_data['type'] = type
                
                email_data['invitation_key'] = invitation_key              
                send_org_email(email_data, to_mail, subject,  'invite_non_member.html')                   
                
            dajax.script('controller.closeSecondDialog();')
        if (ajax == 'change_org_right'):
            org_id = requestProcessor.getParameter('orgid')
            mid = requestProcessor.getParameter('mid')
            value = requestProcessor.getParameter('value')
            org = Organization.objects.get(id = org_id)
            
            #try:
            org_member = OrganizationMember.objects.get(id = mid)
            role_type = RoleType.objects.get(name__iexact=value)
            org_member.role = role_type
            org_member.save()
            email_data['org_name'] = org_member.organization.name
            email_data['site_url'] = settings.SITE_URL
            email_data['right'] = role_type.name
            email_data['invited_username'] = org_member.user.username
            email_data['username'] = user.username
            to_mail = [invited_user.email]
            subject = 'Change right in '+ org.name
            template = 'change_org_right.html'
            send_org_email(email_data, to_mail, subject,  template)
            #except:
            #    org_member = OrganizationMember()
            
        '''
        if (ajax == 'view_org_details'):
            org_id = requestProcessor.getParameter('orgid')
            org = Organization.objects.get(id = org_id)
            org_members = OrganizationMember.objects.filter(organization = org, status = 'A')
            
            data['organization'] = org
            data['org_members'] = org_members
            data['owners'] = org.get_owners()
            body = requestProcessor.decode_jinga_template(request,'website/organizations/organization_details_view.html', data, '')
            dajax.assign('#fancyboxformDiv','innerHTML', body)
            script = requestProcessor.decode_jinga_template(request, 'website/organizations/organization_details_view.js', data, '')
            dajax.script(script)
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            return HttpResponse(dajax.json())
        '''    
        
        #add script to open fancybox if command starts with 'open'
        if ajax.startswith('open'):
            dajax.script('controller.showModalDialog("#fancyboxformDiv");')
            
        return HttpResponse(dajax.json())
                
    message_data = get_system_message(request) #get the message List
    data =  dict(data.items() + message_data.items())   #merge message list to data
            
    return requestProcessor.render_to_response(request,'website/test/test_organization.html', data, '')      

def organization_search(request):
    requestProcessor = HttpRequestProcessor(request)  
    
    data = {}
    
    search_text = requestProcessor.getParameter('text')
    if search_text == None:
        search_text = ''
    page = requestProcessor.getParameter('page')
    
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
        
    range_start = (page_number - 1) * ORGANIZATION_PAGE_SIZE
    range_end = page_number * ORGANIZATION_PAGE_SIZE
    data['next_page_param'] = 'page='+str(page_number + 1)
    
    ### ordering param ###
    sort_dir = requestProcessor.getParameter('sort_dir')  
    sort_by_date_added_dir = requestProcessor.getParameter('sort_by_date_added_dir')   
            
    if sort_dir == None and sort_by_date_added_dir == None:
        data['sort_dir']  = '&sort_dir='+str(sort_dir)
        order_by_str = 'name'
              
    if sort_dir != None and sort_by_date_added_dir == None:
        data['sort_dir']  = '&sort_dir='+str(sort_dir)
        if sort_dir == 'desc':
            order_by_str = '-name'
        else:
            order_by_str = 'name'      
                
    if sort_dir == None and sort_by_date_added_dir != None:
        data['sort_by_date_added_dir']  = '&sort_by_date_added_dir='+str(sort_by_date_added_dir)
        if sort_by_date_added_dir == 'desc':
            order_by_str = '-create_datetime'
        else:
            order_by_str = 'create_datetime'       
                    
    if sort_dir != None and sort_by_date_added_dir != None:
        data['sort_dir']  = '&sort_dir='+str(sort_dir)
        if sort_dir == 'desc':
            order_by_str = '-name'
        else:
            order_by_str = 'name'       
                    
    print order_by_str          
        
                                                   

    if search_text != '':
        organizations = Organization.objects.filter(name__icontains=text, status = 'A').order_by(order_by_str)[range_start:range_end]
        data['search_param'] = '&text='+search_text
    else:
        organizations = Organization.objects.filter(status = 'A').order_by(order_by_str)[range_start:range_end]
        data['search_param'] = '&text='
    
        
    data['organizations'] = organizations
    
    return requestProcessor.render_to_response(request,'website/organizations/organization_list.html', data, '')      
    
def organization_user_search(request):
    requestProcessor = HttpRequestProcessor(request)  
    
    data = {}
    
    search_text = requestProcessor.getParameter('text')
    if search_text == None:
        search_text = ''
    page = requestProcessor.getParameter('page')
    
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
        
    range_start = (page_number - 1) * ORGANIZATION_PAGE_SIZE
    range_end = page_number * ORGANIZATION_PAGE_SIZE
    data['next_page_param'] = 'page='+str(page_number + 1)
    
    data['user_list'] = get_user_list(search_text, page_number)
    
    if search_text != '':
        data['search_param'] = '&text='+search_text
    else:
        data['search_param'] = ''
        
    return requestProcessor.render_to_response(request,'website/organizations/users_select_list.html', data, '')      

def organization_members(request):
    requestProcessor = HttpRequestProcessor(request)  
    
    data = {}
    
    page = requestProcessor.getParameter('page')
    
    if page != None and page != '':
        page_number = int(page)
    else:
        page_number = 1
        
    data['orgid'] = requestProcessor.getParameter('orgid')
    try:
        organization = Organization.objects.get(id=data['orgid'])
    except:
        organization = Organization() #blank for now
    data['organization'] = organization
    
    user = request.user
    data['access'] = get_org_access(user, organization)
    
    date_type = requestProcessor.getParameter('date_type')
    if date_type == 'requested':
        data['date_type'] = 'requested'
    else:
        data['date_type'] = 'join'
        
    members = get_members(organization, page_number)
    data['members'] = members
    data['next_page_param'] = 'page='+str(page_number + 1)
    
    return requestProcessor.render_to_response(request,'website/organizations/org_member_list.html', data, '')      

def validate_create_org_form_data(data, form_id):
    message = {}
    for item in data.keys():
        msg_key = form_id + '_field_' + item
        if item == 'name':
            if data[item] == '':
                message[msg_key] = 'Organization name is required.'
            elif len(data[item]) > 64:
                    message[msg_key] = 'A maximum of 64 characters is allowed for organization name.'
        """            
        if item == 'logo':
            if len(data[item]) > 100:
                message[msg_key] = 'A maximum of 100 characters is allowed for organization logo.'
        """                           
        if item == 'website':
            if len(data[item]) > 200:
                message[msg_key] = 'A maximum of 200 characters is allowed for organization website.'
            
    return message

def get_user_list(search_text, page_number):
    range_start = (page_number - 1) * ORGANIZATION_PAGE_SIZE
    range_end = page_number * ORGANIZATION_PAGE_SIZE
    
    if search_text != None and search_text != '':
        users = User.objects.filter(Q(username__icontains=search_text)|Q(first_name__icontains=search_text)|Q(last_name__icontains=search_text)|Q(email__icontains=search_text)).order_by('username')[range_start:range_end]
    else:
        users = User.objects.all().order_by('username')[range_start:range_end]
        
    user_list = []
    for user in users:
        user_obj = {}
        user_obj['user'] = user
        try:
            user_detail = user.get_profile()
            if user_detail.display_preference == 'realname':
                user_obj['user_display_name'] = user.first_name + ' ' + user.last_name
            else:
                user_obj['user_display_name'] = user.username
        except:
            user_obj['user_display_name'] = user.username
        user_obj['organizations'] = []
        org_members = OrganizationMember.objects.filter(user=user, organization__status = 'A', status = 'A').order_by('organization__name')
        for org_member in org_members:
            user_obj['organizations'].append(org_member.organization)
        user_list.append(user_obj)
        
    return user_list

def get_members(organization, page_number):
    range_start = (page_number - 1) * ORGANIZATION_PAGE_SIZE
    range_end = page_number * ORGANIZATION_PAGE_SIZE
    
    members = OrganizationMember.objects.filter(organization=organization, status='A').exclude(user__isnull=True).order_by('user__username')[range_start:range_end]

    return members

def send_org_email(data, to_mail, subject='Orgnization Email', template='request_org.html'): 
    #subject = 'Request to reset password'
    tp = get_template('website/emails/' + template)
    c = Context(data)
    body = tp.render(c)

    from_mail = django_settings.DEFAULT_FROM_EMAIL
    #to_mail = []
    #to_mail = [data['email']]
    
    msg = EmailMessage( subject, body, from_mail, to_mail)

    msg.content_subtype = "html"   
    msg.send()
    
def get_org_admin_email(org):    
    emails = []
    orgmembers = OrganizationMember.objects.filter(organization = org, status = 'A', role__name = 'Administrator')
    for orgmember in orgmembers:
        emails.append(orgmember.user.email)
    return emails

def get_org_admin(org):
    users = []
    orgmembers = OrganizationMember.objects.filter(organization = org, status = 'A', role__name = 'Administrator')
    for orgmember in orgmembers:
        users.append(orgmember.user)
    return users

def get_org_access(user, org):
    try:
        org_members = OrganizationMember.objects.filter(organization = org, user = user).exclude(status__iexact='RM').exclude(status__iexact='R') 
        if org_members:
            org_member = org_members[0]
            if org_member.status == 'A':
                if org_member.role.name == 'Owner' or org_member.role.name == 'Administrator':
                    return 'Admin'
                else:
                    return 'Member'
            elif org_member.status == 'P':
                return 'PendingMember'
            else:
                return 'NonMember'
        else:
            return 'NonMember'
    except Exception, e:
        return 'NonMember'
    
  
def org_uploadfile(request):

    allowedExtension = django_settings.ALLOWED_IMAGE_FILE_TYPES
    sizeLimit = django_settings.MAX_UPLOAD_FILE_SIZE
    uploader = qqFileUploader(allowedExtension, sizeLimit)

    result = uploader.handleUpload(request, django_settings.MEDIA_ROOT + "/upfiles/org_logos/")

    return_array = result["json"]
    from django.utils import simplejson as json

    if result['success'] == True:
        return_array = json.loads(result["json"])
        full_path = django_settings.MEDIA_ROOT+'/upfiles/org_logos/'+return_array['store_name']
        aa = get_thumbnail(full_path,'140x140', quality=99)
        return_array['thum_path'] = aa.url
        return_array = json.dumps(return_array)
    return HttpResponse(return_array)
  
def change_right_access(members_list, role_list, org):
    acc_flag = True
    for role in role_list:
        if role == 'Administrator':
            return True        
    orgmembers = OrganizationMember.objects.filter(organization = org, status__iexact = 'A', role__name = 'Administrator').exclude(id__in=members_list)
    if len(orgmembers) > 0:
        return True
    else:
        return False
    return True
  
def get_data_for_org_details(org, request):
    data = {}
    user = request.user
    orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R')         
    if orgmembers and len(orgmembers) > 0:
        orgmember = orgmembers[0]
    else:
        orgmember = None
                  
    data['orgmember'] = orgmember
    data['orgname'] = org.name              
    data['organization'] = org

    '''
    if org.logo != None and org.logo !='':
        print 'org.logo.path :: ' + str(org.logo.path)
        data['thum'] = get_thumbnail(org.logo.path,'140x140', quality=99)
    else:
        data['thum'] = ''    
    '''
    
    data['access'] = get_org_access(user, org)
    data['date_type'] = 'join'
    members = get_members(org, 1)
    data['members'] = members
    data['next_page_param'] = 'page=2'
            
    org_admins = OrganizationMember.objects.filter(organization=org, role__name='Administrator', status = 'A').order_by('user__username')
    data['org_admins'] = org_admins   
                            
    return data
  
def send_delete_org_email(user, org):  
    data = {}
    data['site_url'] = settings.SITE_URL
    orgmembers = OrganizationMember.objects.filter(organization = org).exclude(status__iexact='RM').exclude(status__iexact='R').exclude(user = user)
    if orgmembers:
        data['deletor'] = user.username
        data['organization_name'] = org.name
        for member in orgmembers:
            if member.user_id != '' and member.user_id != None:
                data['username'] = str(member.user.username)
                to_mail = [member.user.email]
            else:
                data['username'] = member.email
                to_mail = [member.email]
            send_org_email(data, to_mail, subject='Delete Org', template='delete_org.html')
                    
            
               
def get_invitation_key(email):
    salt = datetime.datetime.now()
    salt_key = email + ':' + str(salt)
    md5_key = hashlib.md5(salt_key).hexdigest()
    
    return md5_key
    
