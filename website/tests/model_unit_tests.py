import random
import unittest
from django.contrib.auth.models import User
from website.models.userDetail import UserSearch


class ModelUnitTests(unittest.TestCase):
    def setUp(self):
        user = User.objects.create_user("testuser", "testuser@testing.solarpermit.org", "testuser")
        user.save()

    def test_user_search(self):
        user = User.objects.all()[0] #just get 1st user
        entity_id_range = range(1, 11) #1 to 10
        
        for index in entity_id_range:
            user_search = UserSearch(user=user, entity_name='Jurisdiction', entity_id=index)
            user_search.label = 'Initial Label ' + str(index)
            user_search.save()
        #repeat, but old ones should be deleted by itself
        for index in entity_id_range:
            user_search = UserSearch(user=user, entity_name='Jurisdiction', entity_id=index)
            user_search.label = 'Changed Label ' + str(index)
            user_search.save()
        
        user_searches = UserSearch.objects.filter(user=user, entity_name='Jurisdiction', entity_id__in=entity_id_range)
        self.assertEqual(10, len(user_searches), 'Got '+str(len(user_searches))+' user_searches instead of 10.')
        
        user_searches = UserSearch.objects.filter(user=user, entity_name='Jurisdiction', entity_id__in=entity_id_range, label='Changed Label 10')
        self.assertEqual(1, len(user_searches), 'Got '+str(len(user_searches))+' user_searches with "Changed Label 10" instead of 1.')
        
    def runTest(self):
        self.test_user_search()
