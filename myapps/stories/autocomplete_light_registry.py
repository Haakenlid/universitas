import autocomplete_light
from .models import Story
from django.utils.translation import ugettext_lazy as _

# This will generate a PersonAutocomplete class
autocomplete_light.register(Story,
    # Just like in ModelAdmin.search_fields
    search_fields=['title', 'lede'],
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': _('Story headline or lede.'),
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-autocomplete-minimum-characters': 3,
    },
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 10,
        # Enable modern-style widget !
        'class': 'modern-style',
    },
)