import os
from unittest import TestSuite
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.utils import unittest
from django.test import TestCase
from django.test.client import Client
from django.conf import settings

class Command(BaseCommand):
    help = """
    Tests the api by feeding it canned requests, and comparing the
    response from the server to a stored response.
    """
    option_list = BaseCommand.option_list + (make_option("--write-expect",
                                                         action='store_true',
                                                         dest='write_expect',
                                                         default=False,
                                                         help="Instead of testing the responses, write the responses out to the expect files."),)
    def handle(self, **options):
        unittest.TextTestRunner().run(XMLTestSuite(options['write_expect']))

TESTDIR = os.path.join(settings.PROJECT_ROOT, 'functional-tests', 'api')
CASEDIR = os.path.join(TESTDIR, 'case')
EXPECTDIR = os.path.join(TESTDIR, 'expect')

class XMLTestCase(TestCase):
    case = None
    expect = None
    client = Client()
    def __init__(self, filename, write_expect=False, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.writing = write_expect
        self.filename = filename
        self.case = os.path.join(CASEDIR, filename)
        self.expect = os.path.join(EXPECTDIR, filename)
    def runTest(self, result=None):
        with open(self.case) as casefile:
            response = self.client.post("/api/read/engineering_verification",
                                        data=casefile.read(),
                                        content_type="text/xml")
        self.assertEqual(200, response.status_code)
        if self.writing:
            with open(self.expect, 'w+') as expectfile:
                expectfile.write(response.content)
        try:
            with open(self.expect) as expectfile:
                self.assertEqual(expectfile.read(), response.content)
        except IOError as e:
            raise CommandError("Could not open or read file '%s'." % self.expect)

class XMLTestSuite(TestSuite):
    _files = filter(lambda f: f.endswith('.xml'), os.listdir(CASEDIR))
    writing = False
    def __init__(self, write_expect=False, *args, **kwargs):
        unittest.TestSuite.__init__(self, *args, **kwargs)
        self.writing = write_expect
    def __iter__(self):
        return (XMLTestCase(f, write_expect=self.writing) for f in self._files)
