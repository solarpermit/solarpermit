from django.core.management.base import BaseCommand, CommandError
from website.utils.cleanCommentViewsHelper import CleanCommentViews

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Remove user comments older than 3 months.'

    def handle(self, *args, **options):
        CleanCommentViews()
        