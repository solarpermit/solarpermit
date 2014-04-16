from django.conf import settings
from django.utils.html import escape
import autocomplete_light
from website.models.jurisdiction import Jurisdiction

class JurisdictionAutocomplete(autocomplete_light.AutocompleteModelBase):
    search_fields = ['name']
    attrs = {'placeholder': 'Type some text to search for jurisdictions'}
    widget_attrs = {'data-widget-bootstrap': 'side-by-side'}
    choice_html_format = u'<option data-value="%s">%s</option>'
    choice_html_format_multiple = u'<option data-value="%s-m" data-value-multiple="%s">%s</option>'
    choices = Jurisdiction.objects.exclude(jurisdiction_type__exact = 'U') \
                                  .exclude(pk__in = settings.SAMPLE_JURISDICTIONS)
    def choices_for_request(self):
        choices = super(JurisdictionAutocomplete, self).choices_for_request()
        self.choices = []
        for choice in choices:
            self.choices.append(choice)
            parent_of = choice.parent_jurisdiction \
                              .exclude(jurisdiction_type__exact = 'U') \
                              .exclude(pk__in = settings.SAMPLE_JURISDICTIONS) \
                              .values_list('pk', flat=True)
            if parent_of:
                self.choices.append((choice, parent_of))
        return self.choices
    def choice_value(self, choice):
        if isinstance(choice, Jurisdiction):
            return choice.pk
        return choice[0].pk
    def choice_values(self, choice):
        return ",".join([str(c) for c in choice[1]])
    def choice_label(self, choice):
        if isinstance(choice, Jurisdiction):
            return choice.get_jurisdiction_display()
        return 'All jurisdictions within '+ choice[0].get_jurisdiction_display()
    def choice_html(self, choice):
        # I hope the label never needs to be escaped
        if isinstance(choice, (list, tuple)):
            return self.choice_html_format_multiple % (escape(self.choice_value(choice)),
                                                       escape(self.choice_values(choice)),
                                                       self.choice_label(choice))
        return self.choice_html_format % (escape(self.choice_value(choice)),
                                          self.choice_label(choice))
autocomplete_light.register(Jurisdiction, JurisdictionAutocomplete)
