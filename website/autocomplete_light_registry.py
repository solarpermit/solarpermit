from django.conf import settings
import autocomplete_light
from website.models.jurisdiction import Jurisdiction

class JurisdictionAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'Type some text to search for jurisdictions'}
    widget_attrs = {'data-widget-bootstrap': 'side-by-side'}
    choice_html_format = u'<option data-value="%s">%s</option>'
    def choices_for_request(self):
        self.choices = self.choices.exclude(jurisdiction_type__exact = 'U') \
                                   .exclude(pk__in = settings.SAMPLE_JURISDICTIONS)
        return super(JurisdictionAutocomplete, self).choices_for_request()
    def choice_label(self, choice):
        return choice.get_jurisdiction_display()

autocomplete_light.register(Jurisdiction, JurisdictionAutocomplete)
