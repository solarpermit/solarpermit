from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import inspect

class NewUserTestCase(TestCase):
    def test_create_user(self):
        client = Client();
        res = client.post('/account/',
                          { 'ajax': "create_account_submit",
                            'invitation_key': "",
                            'email': "create@testing.solarpermit.org",
                            'title': "Engineer",
                            'firstname': "abc",
                            'lastname': "def",
                            'username': "abcdef",
                            'display_as': "realname",
                            'password': "qwertyuiop",
                            'verify_password': "qwertyuiop" })
        self.assertEqual(res.status_code, 200)
        # the request can fail partially, successfully creating the
        # user object but displaying a python exception message; thus
        # we check that there is no dialog box
        self.assertEqual(-1, res.content.find("modal_dialog_message"))
        new_user = User.objects.all()[0]
        self.assertFalse(new_user.is_superuser)
        self.assertFalse(new_user.is_staff)
        auth_user = authenticate(username = 'abcdef',
                                 password = 'qwertyuiop')
        self.assertIsNotNone(auth_user);
        self.assertEqual(new_user, auth_user)
