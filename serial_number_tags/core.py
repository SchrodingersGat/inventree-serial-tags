"""Enforce unique serial numbers based on part tags"""

from plugin import InvenTreePlugin

from plugin.mixins import SettingsMixin, ValidationMixin

from . import PLUGIN_VERSION


class SerialNumberTags(SettingsMixin, ValidationMixin, InvenTreePlugin):

    """SerialNumberTags - custom InvenTree plugin."""

    # Plugin metadata
    TITLE = "Serial Number Tags"
    NAME = "SerialNumberTags"
    SLUG = "serial-number-tags"
    DESCRIPTION = "Enforce unique serial numbers based on part tags"
    VERSION = PLUGIN_VERSION

    # Additional project information
    AUTHOR = "Oliver Walters"
    WEBSITE = "https://github.com/SchrodingersGat/inventree-serial-tags"
    LICENSE = "MIT"

    # Optionally specify supported InvenTree versions
    # MIN_VERSION = '0.18.0'
    # MAX_VERSION = '2.0.0'

    
    
    
    # Plugin settings (from SettingsMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/settings/
    SETTINGS = {
        # Define your plugin settings here...
        'CUSTOM_VALUE': {
            'name': 'Custom Value',
            'description': 'A custom value',
            'validator': int,
            'default': 42,
        }
    }
    
    
    

    # Custom data validation (from ValidationMixin)
    # Ref: https://docs.inventree.org/en/stable/extend/plugins/validation/
    def validate_model_deletion(self, instance, **kwargs):
        """Run custom validation when a model instance is being deleted."""
        ...

    def validate_model_instance(self, instance, deltas=None, **kwargs):
        """Run custom validation on a database model instance."""
        ...
    
    def validate_part_name(self, name, part, **kwargs):
        """Perform validation on a proposed Part name."""
        ...

    def validate_part_ipn(self, ipn, part, **kwargs):
        """Perform validation on a proposed Part IPN."""
        ...

    def validate_part_parameter(self, parameter, data, **kwargs):
        """Perform validation on a proposed Part parameter."""
        ...

    def validate_batch_code(self, batch_code, stock_item, **kwargs):
        """Perform validation on a proposed StockItem batch code."""
        ...

    def generate_batch_code(self, **kwargs):
        """Generate a new StockItem batch code."""
        ...

    def validate_serial_number(self, serial, part, stock_item, **kwargs):
        """Perform validation on a proposed StockItem serial number."""
        ...

    def convert_serial_to_int(self, serial, **kwargs) -> int:
        """Convert a serial number to an integer value."""
        return None
        
    def get_latest_serial_number(self, part, **kwargs):
        """Return the latest serial number for a given part."""
        return None

    def increment_serial_number(self, serial, part=None, **kwargs):
        """Increment a serial number."""
        return None
