import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.conf import settings as django_settings 
from website.models import Address
from django.contrib.localflavor.us.models import PhoneNumberField
from urlparse import urlparse
from sorl.thumbnail import get_thumbnail

class OrganizationCategory(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class Organization(models.Model):
    ORGANIZATION_STATUS_CHOICES = (
        ('A', 'Active'),
        ('D', 'Disabled'),
    )
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(OrganizationCategory, blank=True, null=True)
    parent_org = models.ForeignKey('self', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = PhoneNumberField(blank=True, null=True)
    fax = PhoneNumberField(blank=True, null=True)    
    logo = models.ImageField(upload_to='org_logos', blank=True, null=True)
    logo_scaled = models.ImageField(upload_to='org_logos_scaled', blank=True, null=True) #logo that has been scale to size for display
    status = models.CharField(choices=ORGANIZATION_STATUS_CHOICES, max_length=8, blank=True, null=True, db_index=True, default='A')
    status_datetime = models.DateTimeField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'
        
    def get_display_website(self):
        url_components = urlparse(self.website)
        if url_components.scheme == '':
            return str(url_components.path)
        else:
            return str(url_components.netloc)
    
    def get_clickable_website(self):
        url_components = urlparse(self.website)
        if url_components.scheme == '':
            return 'http://' + str(self.website)
        else:
            return self.website        
    
    def status_label(self):
        #clean up old data
        if self.status == None or self.status == '':
            self.status = 'A'
            self.save()
        for choice in self.ORGANIZATION_STATUS_CHOICES:
            if self.status == choice[0]:
                return choice[1]
        return ''
    
    #set the current owner and make the previous owner just a member, if any
    def set_owner(self, user):
        try:
            ownerRole = RoleType.objects.get(name="Owner")
            memberRole = RoleType.objects.get(name="Member")
        except:
            #should not happen, fixture defined role already
            ownerRole = None
            memberRole = None
        try:
            lastOwner = OrganizationMember.objects.get(organization=self, role=ownerRole, status='A')
        except:
            lastOwner = None
        #has last owner
        if lastOwner != None:
            #see if owner has changed
            if user != lastOwner.user:
                #make last owner just a member
                lastOwner.role = memberRole
                lastOwner.display_order = 1
                lastOwner.save()
            #owner has not change
            else:
                return #do nothing
        #see if user already a member
        try:
            newOwner = OrganizationMember.objects.get(organization=self, user=user, role=memberRole)
        except:
            newOwner = OrganizationMember(organization=self, user=user)
        #add or change to new owner
        newOwner.role = ownerRole
        newOwner.status = 'A' #active
        newOwner.display_order = 0
        newOwner.save()
        self.remove_other_organizations(user)
        return newOwner

    def set_member(self, user, status=None):
        try:
            memberRole = RoleType.objects.get(name="Member")
        except:
            #should not happen, fixture defined role already
            memberRole = None
        try:
            member = OrganizationMember.objects.get(organization=self, user=user)
            #existing, don't change current role
        except:
            member = OrganizationMember(organization=self, user=user)
            member.role = memberRole
            member.display_order = 1
        if status != None:
            member.status = status
        member.save()
        self.remove_other_organizations(user)
        return member
    
    def get_owners(self):
        try:
            ownerRole = RoleType.objects.get(name="Owner")
        except:
            ownerRole = None
            
        try:
            owners = OrganizationMember.objects.filter(organization=self, role=ownerRole, status='A')
        except:
            owners = None
            
        return owners
    
    #remove a user's membership from other organization
    def remove_other_organizations(self, user):
        members = OrganizationMember.objects.filter(user=user).exclude(organization=self)
        for member in members:
            if member.status == 'A':
                member.status = 'RM' #removed
                member.save()
    
    def get_logo_thumbnail(self,size):
        if self.logo == None or self.logo == '':
            return ''
        full_path = django_settings.MEDIA_ROOT+ str(self.logo)
        full_image = get_thumbnail(full_path,size, quality=99)
        return full_image.url          
    
class OrganizationAddress(models.Model):
    organization = models.ForeignKey(Organization, blank=True, null=True)
    address = models.ForeignKey(Address, blank=True, null=True)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'

class RoleType(models.Model):
    name = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def __unicode__(self):
        return self.name
    class Meta:
        app_label = 'website'

class OrganizationMember(models.Model):
    MEMBER_STATUS_CHOICES = (
        ('P', 'Pending'), #request to join is pending approval
        ('A', 'Active'), #active member, request was accepted, or owner, ...
        ('R', 'Rejected'),
        ('RM', 'Removed'), #was a member but removed
        ('AI', 'Inited by Admin'),
        ('MI', 'Inited by Member'),
    )
    organization = models.ForeignKey(Organization, blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, related_name= '_member_user') #if this is a system user
    invitor = models.ForeignKey(User, null=True, blank=True, related_name= '_member_invitor') #this is a invitor
    email = models.EmailField(blank=True, null=True)
    role = models.ForeignKey(RoleType, blank=True, null=True)
    status = models.CharField(choices=MEMBER_STATUS_CHOICES, max_length=8, blank=True, null=True, db_index=True, default="P")
    display_order = models.PositiveSmallIntegerField(blank=True, null=True)
    join_date = models.DateTimeField(blank=True, null=True)
    requested_date = models.DateTimeField(blank=True, null=True)
    invitation_key = models.CharField(max_length=128, blank=True, null=True)    
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    def status_label(self):
        if self.status != None and self.status != '':
            for choice in self.MEMBER_STATUS_CHOICES:
                if self.status == choice[0]:
                    return choice[1]
        return ''
    
    def user_name_Label(self):
        try:
            user_detail = self.user.get_profile()
        except:
            return self.user.username
        if user_detail.display_preference == 'realname':
            return self.user.first_name + ' ' + self.user.last_name
        else:
            return self.user.username
    
    def get_show_requested_date(self, timezone = ''):
        from website.utils.datetimeUtil import DatetimeHelper
        dh = DatetimeHelper(self.requested_date, timezone)
        return dh.showTimeFormat()
    
    def get_show_join_date(self, timezone = ''):
        from website.utils.datetimeUtil import DatetimeHelper
        dh = DatetimeHelper(self.join_date, timezone)
        return dh.showTimeFormat()
    
    def get_user_orgs(self, user):
        data = {}
        orgmembers = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='AI').exclude(status__iexact='MI')
        data['orgmembers'] = orgmembers            
        orgmembers_invite = OrganizationMember.objects.filter(user = user, organization__status = 'A').exclude(status__iexact='RM').exclude(status__iexact='R').exclude(status__iexact='A').exclude(status__iexact='P')
        data['orgmembers_invite'] = orgmembers_invite 
        
        return data    
    
    
    def get_user_org(self, user):

        org_members = OrganizationMember.objects.filter(user = user, status = 'A', organization__status = 'A')
        if len(org_members) >=1:
            org = org_members[0].organization
        else:
            org = None
            
        return org    
    
