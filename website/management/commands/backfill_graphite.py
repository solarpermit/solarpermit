#!/usr/bin/env python

import socket
import time
from datetime import datetime
from django.utils.timezone import utc
from django.core.management.base import BaseCommand, CommandError
from website.models import Question
from pprint import pprint

def since_epoch(timestamp):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
    return int((timestamp - epoch).total_seconds())

CARBON_SERVER = ('localhost', 2003)
CUTOFF_TIME = since_epoch(datetime(2013, 06, 13, 0, 0, 0, 0, utc))
NOW = since_epoch(datetime.now(utc))

class Command(BaseCommand):
    def handle(self, *args, **options):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(CARBON_SERVER)
        questions = Question.objects.all()
        #questions = Question.objects.filter(id=3)
        for q in questions:
            timeline = []
            answers = q.answerreference_set.all()
            if not answers:
                print "not backfilling question %d, it has no suggestions/answers" % q.id
            else:
                print "backfilling question %d with %d suggestions/answers" % (q.id, answers.count())
                for ans in answers:
                    create = since_epoch(ans.create_datetime)
                    modify = since_epoch(ans.modify_datetime)
                    timeline.append((create, {'suggested': 1}))
                    if ans.approval_status == 'C':
                        timeline.append((modify, {'suggested': -1}))
                    elif ans.approval_status == 'A':
                        timeline.append((modify, {'answered': 1}))
                    elif ans.approval_status in ('R', 'F'):
                        timeline.append((modify, {'suggested': -1}))
                timeline.sort(None, lambda t: t[0])
                metrics = {'suggested': 0, 'answered': 0}
                start = int(timeline[0][0] - (timeline[0][0] % 10)) - 100 # start a few steps before the first one
                end = start + 10
                while start < NOW:
                    last_count = metrics['suggested']
                    while timeline and (timeline[0][0] < end):
                        m = timeline.pop(0)[1]
                        if 'suggested' in m:
                            metrics['suggested'] += m['suggested']
                        if 'answered' in m:
                            metrics['answered'] += m['answered']
                    if metrics['suggested'] > last_count:
                        print "  found %d answers between %d and %d" % (metrics['suggested'] - last_count, start, end)
                    send(sock,
                         "solarpermit.dev.gauges.question.suggested.%d" % q.id,
                         metrics['suggested'],
                         end)
                    send(sock,
                         "solarpermit.dev.gauges.question.answered.%d" % q.id,
                         metrics['answered'],
                         end)
                    start = end
                    end += 10
            # yes, sleep. if we go too fast, carbon doesn't create all of the databases
            time.sleep(1)
        sock.close()

def send(socket, name, value, timestamp):
    socket.sendall("%s %s %d\n" % (name, value, timestamp))
