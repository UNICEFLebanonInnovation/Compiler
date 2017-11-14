from __future__ import unicode_literals, absolute_import, division

from django.db import models

from model_utils.models import TimeStampedModel

from django.utils.translation import ugettext as _


class Exporter(TimeStampedModel):

    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['created']
        verbose_name = "Exported file"
        verbose_name_plural = "Exported files"

    def __unicode__(self):
        return self.name
