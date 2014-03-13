from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from website.models import Jurisdiction
from django.conf import settings

class AHJUrlsTestCase(TestCase):
    def test_ahj_urls(self):
        j = Jurisdiction.objects.create(city = "foo city",
                                        name_for_url = "foo",
                                        description = "foo",
                                        state = "CA",
                                        jurisdiction_type = "CI",
                                        name = "foo")
        client = Client()
        patterns = ["/jurisdiction/%s",
                    "/jurisdiction/%s/"]
        for ahj in Jurisdiction.objects.all():
            urls = [p % ahj.name_for_url for p in patterns]
            response = client.get(urls[0])
            self.assertEqual(301, response.status_code)
            self.assertEqual("http://testserver" + urls[1],
                             response['Location'])
            response = client.get(urls[1])
            self.assertEqual(200, response.status_code)

