from django.core.management.base import BaseCommand, CommandError
from website.utils.notificationSentHelper import NotificationHelper

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Send all pending immediate notifications.'

    def handle(self, *args, **options):
        NotificationHelper('I')