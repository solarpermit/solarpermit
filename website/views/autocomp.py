## define what types of things can be autocompleted
from website.models import Jurisdiction
from autocomplete.views import AutocompleteView, AutocompleteSettings
from django.conf import settings
from django.db.models import Q

autocomplete_instance = AutocompleteView('website')
class JurisdictionSettings(AutocompleteSettings):
    queryset = Jurisdiction.objects.filter(~Q(jurisdiction_type__exact = 'U') & \
                                           ~Q(pk__in = settings.SAMPLE_JURISDICTIONS))
    search_fields = ['name']
    key = 'pk'
    label = Jurisdiction.get_jurisdiction_display
    reverse_label = True
autocomplete_instance.register("jurisdictions", JurisdictionSettings)
