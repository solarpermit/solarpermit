from django.core.management.base import BaseCommand, CommandError
from website.utils.templateUtil import TemplateUtil

class Command(BaseCommand):
    args = 'No argument needed'
    help = 'Update the static site map pages.'

    def handle(self, *args, **options):
        template_util = TemplateUtil()
        template_util.update_site_map()