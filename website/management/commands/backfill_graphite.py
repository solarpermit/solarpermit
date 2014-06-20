#!/usr/bin/env python
import copy
import socket
import time
from datetime import datetime
from django.utils.timezone import utc
from django.core.management.base import BaseCommand, CommandError
from website.models import Question
from website.utils import reporting
from pprint import pprint

def since_epoch(timestamp):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
    return int((timestamp - epoch).total_seconds())

CARBON_SERVER = ('localhost', 2003)

class Command(BaseCommand):
    def handle(self, *args, **options):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(CARBON_SERVER)
        questions = Question.objects.all()
        #questions = Question.objects.filter(pk=1)
        for q in questions:
            answers = q.answerreference_set.all()
            if not answers:
                print "not backfilling question %d, it has no suggestions/answers" % q.id
            else:
                timestamps = set([ans.create_datetime for ans in answers]) | \
                             set([ans.modify_datetime for ans in answers])
                print "backfilling question %d with %d answers at %d distinct times" % (q.id, answers.count(), len(timestamps))
                last = None
                for stamp in sorted(timestamps):
                    seconds = since_epoch(stamp)
                    start = int(seconds - (seconds % 10))
                    end = start + 10
                    base = "solarpermit.dev.counters.question"
                    reports = reporting.run_reports(q, before=stamp)
                    changes = differences(last, reports) if last else reports
                    for report in changes:
                        if 'name' in report:
                            for row in report['table']:
                                k = row['key'].lower()
                                v = row['value']
                                if v:
                                    send(sock, ".".join([base, report['name'].lower(), str(q.id), k, "count"]), v, end)
                                    send(sock, ".".join([base, report['name'].lower(), str(q.id), k, "rate"]), v / 10, end)
                    last = reports
            # yes, sleep. if we go too fast, carbon doesn't create all of the databases
            time.sleep(30)
        sock.close()

def differences(last, current):
    output = copy.deepcopy(current)
    for (i, report) in enumerate(current):
        if 'name' in report:
            for (r, row) in enumerate(report['table']):
                output[i]['table'][r]['value'] = row['value'] - last[i]['table'][r]['value']
    return output

def send(socket, name, value, timestamp):
    socket.sendall("%s %s %d\n" % (name, value, timestamp))
