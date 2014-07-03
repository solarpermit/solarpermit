#!/usr/bin/env python
import socket
import time
from datetime import datetime
from django.utils.timezone import utc
from django.core.management.base import BaseCommand, CommandError
import website
from website.utils import reporting
from website.utils.temporal_stats import normalize
from pprint import pprint

def since_epoch(timestamp):
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=utc)
    return int((timestamp - epoch).total_seconds())

CARBON_SERVER = ('localhost', 2003)
base = "solarpermit.counters.question"
backfilling_msg = "%s: backfilling report %s for question %d with %d answers at %d distinct times"

class Command(BaseCommand):
    def handle(self, *args, **options):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(CARBON_SERVER)
        questions = website.models.Question.objects.all()
        #questions = website.models.Question.objects.filter(pk=9)
        print "%s: backfilling %d questions" % (datetime.now(), len(questions))
        jurisdiction_timestamps = set([j.create_datetime or j.modify_datetime
                                       for j in website.models.Jurisdiction.objects.all()
                                       if j.create_datetime is not None or
                                          j.modify_datetime is not None])
        for q in questions:
            answers = q.answerreference_set.all()
            if not answers:
                print "%s: not backfilling question %d, it has no answers" % (datetime.now(), q.id)
            else:
                # you might think we could just use
                # reporting.update_reports, but that will report via
                # statsd which wouldn't let us actually backfill
                reports = reporting.get_reports(q)
                for report in reports:
                    if 'name' in report:
                        timestamps = set([ans.create_datetime for ans in answers]) | \
                                     set([ans.modify_datetime for ans in answers])
                        if report['name'] == 'coverage':
                            timestamps |= jurisdiction_timestamps
                        print backfilling_msg % (datetime.now(), report['name'], q.id, answers.count(), len(timestamps))
                        last = None
                        for stamp in sorted(timestamps):
                            seconds = since_epoch(stamp)
                            start = int(seconds - (seconds % 10))
                            end = start + 10
                            current = reporting.run_report(q, report, before=stamp)['table']
                            changes = differences(last, current) if last else current
                            for row in changes:
                                k = row['key'].lower()
                                v = row['value']
                                if v is not None:
                                    send(sock, [base, report['name'], q.id, k, "count"], v, end)
                                    send(sock, [base, report['name'], q.id, k, "rate"], v / 10.0, end)
                            last = current
            # yes, sleep. if we go too fast, carbon doesn't create all of the databases
            time.sleep(30)
        sock.close()

def differences(last, current):
    return [{ 'key': row['key'],
              'value': row['value'] - last[r]['value'] }
            for (r, row) in enumerate(current)]

def send(socket, name, value, timestamp):
    name = ".".join([normalize(str(n)).lower() for n in name])
    msg = "%s %s %d\n" % (name, value, timestamp)
    #print "%s: %s" % (datetime.now(), msg),
    socket.sendall(msg)
