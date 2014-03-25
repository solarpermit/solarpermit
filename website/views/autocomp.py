## define what types of things can be autocompleted
from website.models import Jurisdiction
from autocomplete.views import AutocompleteView, AutocompleteSettings

autocomplete_instance = AutocompleteView('website')
class CountiesSettings(AutocompleteSettings):
    queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CO', 'SC', 'CC'))
    search_fields = ['name']
    key = 'pk'
    label = Jurisdiction.get_jurisdiction_display
autocomplete_instance.register("counties", CountiesSettings)
class CitiesSettings(AutocompleteSettings):
    queryset = Jurisdiction.objects.filter(jurisdiction_type__in = ('CC', 'CI', 'IC'))
    search_fields = ['name']
    key = 'pk'
    label = Jurisdiction.get_jurisdiction_display
autocomplete_instance.register("cities", CitiesSettings)
