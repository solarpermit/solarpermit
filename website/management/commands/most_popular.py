from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import json
import datetime
from website.models import UserPageView, Jurisdiction, JurisdictionRating

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Find the most popular jurisdictions'
    # url names that are for sure not specific jurisdiction
    skip_names = ['browse', 'search', 'autocomplete', 'answer_uploadfile', ]

    def handle(self, *args, **options):
        jurisdiction_unique_users = {}
        
        #find all the UserPageView for the last 7 days
        today = datetime.date.today()
        d = datetime.timedelta(days=-8)
        start_date = today + d
        print 'Updating most popular jurisdictions for days after: ' + str(start_date)
        user_page_views = UserPageView.objects.filter(last_page_view_date__gt=start_date)
        #print 'Number of user page views: ' + str(len(user_page_views))
        
        for user_page_view in user_page_views:
            #print 'Datetime: ' + str(user_page_view.last_page_view_date)
            if user_page_view.url.startswith('/jurisdiction/'):
                name_for_url = user_page_view.url.replace('/jurisdiction/', '')
                name_for_url = name_for_url.partition('/')[0]
                if name_for_url in self.skip_names:
                    continue
                if name_for_url.isdigit():
                    #search for jurisdiction by id
                    jurisdictions = Jurisdiction.objects.filter(id=name_for_url)
                else:
                    #search for jurisdiction by name for url
                    jurisdictions = Jurisdiction.objects.filter(name_for_url=name_for_url)
                if len(jurisdictions) > 0:
                    jurisdiction = jurisdictions[0] #just get 1st
                #print 'name_for_url: ' + name_for_url
                #print 'jurisdiction: ' + jurisdiction.show_jurisdiction()
                
                #remember jurisdiction unique users
                try:
                    jurisdiction_unique_users[jurisdiction.id]
                except:
                    jurisdiction_unique_users[jurisdiction.id] = []
                if user_page_view.user.id not in jurisdiction_unique_users[jurisdiction.id]:
                    jurisdiction_unique_users[jurisdiction.id].append(user_page_view.user.id)
                #print 'jurisdiction_unique_users' + str(jurisdiction_unique_users)
            
        #find the jurisdiction with most unique users
        jurisdiction_unique_users_counts = []
        for jid, user_list in jurisdiction_unique_users.iteritems():
            jurisdiction_unique_users_counts.append([jid, len(user_list)])
        jurisdiction_unique_users_counts.sort(key=lambda x: x[1], reverse=True) #sort by user count
        jurisdiction_unique_users_counts = jurisdiction_unique_users_counts[0:10] #only top 10
        
        #save data in JurisdictionRating
        jurisdiction_ratings = JurisdictionRating.objects.filter(rating_type='V')
        for jurisdiction_rating in jurisdiction_ratings:
            jurisdiction_rating.delete()
        rank = 1
        for jid, count in jurisdiction_unique_users_counts:
            jurisdiction_rating = JurisdictionRating(rating_type='V', rank=rank, value=count)
            jurisdiction = Jurisdiction.objects.get(id=jid)
            jurisdiction_rating.jurisdiction = jurisdiction
            jurisdiction_rating.create_datetime = today
            jurisdiction_rating.save()
            print str(rank) + ': ' +jurisdiction.show_jurisdiction() + ', unique views: ' + str(count)
            rank += 1
        
        '''#just for testing
        print 'Recently updated: '
        jurisdictions = JurisdictionRating.recently_updated()
        for jurisdiction in jurisdictions:
            print jurisdiction.show_jurisdiction()
        
        #just for testing
        print 'Most popular: '
        jurisdictions = JurisdictionRating.most_popular()
        for jurisdiction in jurisdictions:
            print jurisdiction.show_jurisdiction()'''
        
        