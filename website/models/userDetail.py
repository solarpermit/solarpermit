import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserDetail(models.Model):
    NOTIFICATION_CHOICES = (
        ('I', 'Immediately'),
        ('D', 'Daily'),
        ('W', 'Weekly'),
        ('M', 'Monthly'),
        ('N', 'Never'),
    )
    
    TITLES = (
        ('Administrative/Clerical', 'Administrative/Clerical'),
        ('CAD designer', 'CAD designer'),
        ('Consultant', 'Consultant'),
        ('Engineer', 'Engineer'),    
        ('Installer', 'Installer'),
        ('Manager/Supervisor', 'Manager/Supervisor'),           
        ('Permit runner', 'Permit runner'),    
        ('Other', 'Other'),                          
    )
    user = models.ForeignKey(User, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, blank=True, null=True)
    old_password = models.CharField(max_length=32, blank=True, null=True)
    reset_password_key = models.CharField(max_length=128, blank=True, null=True)
    notification_preference = models.CharField(choices=NOTIFICATION_CHOICES, max_length=2, blank=True, null=True)
    display_preference = models.CharField(max_length=16, blank=True, null=True)    # real_name; username
    title = models.CharField(max_length=124, blank=True, null=True)
    migrated_id = models.IntegerField(blank=True, null=True, db_index=True) 
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    def user_email(self):
        return self.user.email
    class Meta:
            app_label = 'website'

    def get_display_name(self):
        display_name = ''
        if self.display_preference == 'realname':
            return self.user.first_name + ' ' + self.user.last_name
        elif self.display_preference == 'username':
            return self.user.username
        else:
            return self.user.username
    
    def get_user_org(self):
        from website.models import OrganizationMember, Organization
        user = self.user
        oms = OrganizationMember.objects.filter(user = user, status= 'A', organization__status = 'A')
        if len(oms) > 0 :
            return oms[0].organization
        else:
            return None
    
    @staticmethod
    def get_migrated_user_by_id(mid):
        #if mid is zero, is "Early Contributor"
        if mid == 0 or mid == '0':
            users = User.objects.filter(username='early_contributors')
            if len(users) == 0:
                user = User(first_name='Early', last_name='Contributors')
                user.username = 'early_contributors'
                user.email = 'support@cleanpowerfinance.com'
                user.save()
                user_detail = UserDetail(user=user, migrated_id=0)
                user_detail.save()

                return user
            else:
                return users[0]
        else:
            user_details = UserDetail.objects.filter(migrated_id=mid)
            if len(user_details) > 0:
                user_detail = user_details[0]
                return user_detail.user
        return None
    
class UserFavorite(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    #entity name that the user pick as favorite, like "Jurisdiction"
    entity_name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    entity_id = models.IntegerField(blank=True, null=True, db_index=True) #id of the record (entity)
    display_order = models.PositiveSmallIntegerField(blank=True, null=True) #rank or order to show within same entity_name
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'

# remember last 10 user's search results that was selected
class UserSearch(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    #entity name that the user pick as favorite, like "Jurisdiction"
    entity_name = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    entity_id = models.IntegerField(blank=True, null=True, db_index=True) #id of the record (entity)
    label = models.CharField(max_length=64, blank=True, null=True) #label to show user for this search choice
    search_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)
    create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'
    
    #this save method will check if this entity_name and id already exist for this user, just update
    #no need to check elsewhere in code
    #it will also delete old searches to ensure no more than 10 per user
    def save(self, *args, **kwargs):
        same_searches = UserSearch.objects.filter(user=self.user, entity_name=self.entity_name, entity_id=self.entity_id)
        if len(same_searches) > 0:
            #just an update of existing
            self.id = same_searches[0].id
        else:
            #delete if more than 9 items for this user, since there is a new one
            user_searches = UserSearch.objects.filter(user=self.user).order_by('-search_datetime')
            if len(user_searches) > 9:
                for user_search in user_searches[9:]:
                    user_search.delete()
        super(UserSearch, self).save(*args, **kwargs)
    
    @staticmethod
    def get_user_recent(user):
        try:
            user_searches = UserSearch.objects.filter(user=user).order_by('-search_datetime')
        except:
            user_searches = []
        return user_searches   
                  
class UserPageView(models.Model):
    user = models.ForeignKey(User, blank=True, null=True, db_index=True)
    url = models.CharField(max_length=1024, blank=True, null=True, db_index=False)
    #view_datetime = models.DateTimeField(blank=True, null=True)    
    last_page_view_date = models.DateField(blank=True, null=True) #now used to store every single page view, not the last!
    #create_datetime = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    #modify_datetime = models.DateTimeField(auto_now=True, blank=True, null=True)    
    class Meta:
        app_label = 'website'                    
    