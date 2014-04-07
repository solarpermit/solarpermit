## define what types of things can be autocompleted
from website.models import Jurisdiction
from autocomplete.views import AutocompleteView, AutocompleteSettings

autocomplete_instance = AutocompleteView('website')
class JurisdictionSettings(AutocompleteSettings):
    queryset = Jurisdiction.objects.all()
    search_fields = ['name']
    key = 'pk'
    label = Jurisdiction.get_jurisdiction_display
    reverse_label = True

class CountiesSettings(JurisdictionSettings):
    queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CO', 'SC', 'CC'))
autocomplete_instance.register("counties", CountiesSettings)

class CitiesSettings(JurisdictionSettings):
    queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CC', 'CI', 'IC'))
autocomplete_instance.register("cities", CitiesSettings)

class CountiesByStateSettings(CountiesSettings):
    search_fields = ['=state']
    limit = None
autocomplete_instance.register("counties-by-state", CountiesByStateSettings)

class CitiesByCountySettings(CitiesSettings):
    search_fields = ['==parent_id']
    limit = None
autocomplete_instance.register("cities-by-county", CitiesByCountySettings)
