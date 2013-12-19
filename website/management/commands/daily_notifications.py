from django.core.management.base import BaseCommand, CommandError
from website.utils.notificationSentHelper import NotificationHelper

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Send all pending daily notifications.'

    def handle(self, *args, **options):
        NotificationHelper('D')