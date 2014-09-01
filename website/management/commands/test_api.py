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
                                                         help="Instead of testing the responses, write the responses out to the expect files."),
                                             make_option("--case",
                                                         action='store',
                                                         dest='case',
                                                         default=None,
                                                         help="Name of a case file to use."),)
    def handle(self, **options):
        unittest.TextTestRunner().run(XMLTestSuite(write_expect = options['write_expect'],
                                                   case = options['case']))

TESTDIR = os.path.join(settings.PROJECT_ROOT, 'functional-tests', 'api')
CASEDIR = os.path.join(TESTDIR, 'case')
EXPECTDIR = os.path.join(TESTDIR, 'expect')

class XMLTestCase(TestCase):
    case = None
    expect = None
    client = Client()
    maxDiff = 10000
    def __init__(self, filename, write_expect=False, *args, **kwargs):
        TestCase.__init__(self, *args, **kwargs)
        self.writing = write_expect
        self.filename = filename
        self.case = os.path.join(CASEDIR, filename)
        self.expect = os.path.join(EXPECTDIR, filename)
        self._testMethodDoc = self.case
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
                self.assertMultiLineEqual(expectfile.read(), response.content)
        except IOError as e:
            self.assertMultiLineEqual("", response.content)

class XMLTestSuite(TestSuite):
    _files = None
    writing = False
    def __init__(self, write_expect=False, case=None, *args, **kwargs):
        unittest.TestSuite.__init__(self, *args, **kwargs)
        self.writing = write_expect
        if case is None:
            self._files = filter(lambda f: f.endswith('.xml'), os.listdir(CASEDIR))
        else:
            self._files = filter(lambda f: f == case, os.listdir(CASEDIR))
    def __iter__(self):
        return (XMLTestCase(f, write_expect=self.writing) for f in self._files)
