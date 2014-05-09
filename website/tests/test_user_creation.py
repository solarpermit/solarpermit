from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import inspect

class NewUserTestCase(TestCase):
    def setUp(self):
        self.users = [{ 'ajax': "create_account_submit",
                        'invitation_key': "",
                        'email': "create@testing.solarpermit.org",
                        'title': "Engineer",
                        'firstname': "abc",
                        'lastname': "def",
                        'username': "abcdef",
                        'display_as': "realname",
                        'password': "qwertyuiop",
                        'verify_password': "qwertyuiop" },
                      { 'ajax': "create_account_submit",
                        'invitation_key': "",
                        'email': "create@testing.solarpermit.org",
                        'title': "Engineer",
                        'firstname': "ghi",
                        'lastname': "jkl",
                        'username': "ghijkl",
                        'display_as': "realname",
                        'password': "asdfghjkl",
                        'verify_password': "asdfghjkl" }]
    def test_create_user(self):
        client = Client()
        res = client.post('/account/', self.users[0])
        self.assertEqual(res.status_code, 200)
        # the request can fail partially, successfully creating the
        # user object but displaying a python exception message; thus
        # we check that there is no dialog box
        self.assertEqual(-1, res.content.find("modal_dialog_message"))
        new_user = User.objects.all()[0]
        self.assertFalse(new_user.is_superuser)
        self.assertFalse(new_user.is_staff)
        auth_user = authenticate(username = self.users[0]['username'],
                                 password = self.users[0]['password'])
        self.assertIsNotNone(auth_user);
        self.assertEqual(new_user, auth_user)

    def test_duplicate_user(self):
        client = Client()
        res = client.post('/account/', self.users[0])
        self.assertEqual(res.status_code, 200)
        res = client.post('/account/', self.users[1])
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.content.find("email address already exists") != -1)
        auth_user = authenticate(username = self.users[1]['username'],
                                 password = self.users[1]['password'])
        self.assertIsNone(auth_user);
