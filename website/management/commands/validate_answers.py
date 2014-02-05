from django.core.management.base import BaseCommand, CommandError
from website.utils.fieldValidationCycleUtil import FieldValidationCycleUtil

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Check and validate all pending answers if they are due.'

    def handle(self, *args, **options):
        fvcu = FieldValidationCycleUtil()
        fvcu.cron_validate_answers()