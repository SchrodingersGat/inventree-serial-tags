"""Enforce unique serial numbers based on part tags"""

import logging

from django.core.exceptions import ValidationError

import part.models
import stock.models

from plugin import InvenTreePlugin
from plugin.mixins import SettingsMixin, ValidationMixin

from . import PLUGIN_VERSION


logger = logging.getLogger('inventree')


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

    # Plugin settings (from SettingsMixin)
    SETTINGS = {
        "TAG_PARAMETER": {
            "name": "Tag Parameter",
            "description": "Parameter used to tag parts for serial number uniqueness",
            "model": "part.partparametertemplate",
        }
    }
    
    @property
    def parameter_template(self):
        """Return the parameter template used to tag parts."""
        if template_id := self.get_setting('TAG_PARAMETER'):
            try:
                template = part.models.PartParameterTemplate.objects.get(pk=template_id)
                return template
            except Exception:
                logger.error(f"Failed to load parameter template {template_id}")
                return None

        return None

    def get_latest_serial_number(self, part, **kwargs):
        """Return the 'latest' serial number for a given Part instance."""

        latest_sn = None

        for tag in self.get_tags_for_part(part):

            # Fetch all stock items which are tagged with this parameter
            stock_items = self.get_stock_items_for_tag(tag)
            stock_items = stock_items.exclude(serial=None).exclude(serial='')

            if not stock_items.exists():
                continue

            stock_items = stock_items.order_by('-serial_int', '-serial', '-pk')

            sn = stock_items.first().serial_int
            
            if latest_sn is None or sn > latest_sn:
                latest_sn = sn
        
        if latest_sn is not None:
            return str(latest_sn)
        else:
            return None
    
    def validate_serial_number(self, serial: str, part_instance, stock_item):
        """Validate serial number uniqueness based on tagged parameter.
        
        Arguments:
            - serial: The serial number to validate
            - part_instance: The part instance to validate against
            - stock_item: The stock item instance to validate against
        """
    
        # Tags can be comma-separated
        for tag in self.get_tags_for_part(part_instance):

            tag = tag.strip()

            if not tag:
                continue

            stock_items = self.get_stock_items_for_tag(tag)

            # Find any stock items which match the provided serial number
            stock_items = stock_items.filter(
                serial=serial
            )

            if stock_item:
                stock_items = stock_items.exclude(pk=stock_item.pk)
                
            if stock_items.exists():
                raise ValidationError(
                    f"Serial number {serial} already exists for part tagged with '{tag}'"
                )

    def get_tags_for_part(self, part_instance):
        """Return a list of tags associated with a part instance."""

        template = self.parameter_template

        if not template:
            return []

        # Does this part (or any parts in the part tree) have the required parameter?
        parameter = part.models.PartParameter.objects.filter(
            part__tree_id=part_instance.tree_id,
            template=template
        ).first()

        if not parameter:
            return []
        
        return [t.strip() for t in parameter.data.split(',') if t.strip()]

    def get_stock_items_for_tag(self, tag: str):
        """Return a queryset of StockItem objects which are tagged with the specified tag."""
        
        template = self.parameter_template

        if not tag or not template:
            return stock.models.StockItem.objects.none()
        
        # Create a regex for finding this tag within a comma-separated string
        pattern = f"[^,\\w]*{tag}[,\\w$]*"

        # Find all parameter values which have the same tag
        part_ids = part.models.PartParameter.objects.filter(
            template=template,
            data__iregex=pattern
        ).values_list('part_id', flat=True)

        # Find all part "trees" which have the same tag
        trees = part.models.Part.objects.filter(
            id__in=part_ids
        ).values_list('tree_id', flat=True).distinct()

        # Find all stock items which match to parts which have the same tag
        stock_items = stock.models.StockItem.objects.filter(
            part__tree_id__in=trees
        )

        return stock_items
