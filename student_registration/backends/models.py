from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.utils.translation import gettext as _
from django.db import models
from django.db.models import JSONField
from model_utils.models import TimeStampedModel
from model_utils import Choices
from student_registration.schools.models import School


class Exporter(TimeStampedModel):

    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Exported by')
    )

    class Meta:
        ordering = ['created']
        verbose_name = "Exported file"
        verbose_name_plural = "Exported files"

    def __unicode__(self):
        return self.name


class Notification(TimeStampedModel):

    name = models.CharField(max_length=500, blank=False, null=True)
    type = models.CharField(
        choices=Choices(
            ('general', 'General'),
            ('helpdesk', 'Helpdesk'),
        ),
        max_length=50,
        blank=True, null=True
    )
    school_type = models.CharField(
        choices=Choices(
            ('2ndshift', '2nd-shift'),
            ('ALP', 'ALP'),
        ),
        max_length=50,
        blank=True, null=True
    )
    status = models.BooleanField(blank=True, default=False)
    description = models.TextField(max_length=500, blank=True, null=True)
    comments = models.TextField(max_length=500, blank=True, null=True)
    school = models.ForeignKey(
        School,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
    )
    schools = models.ManyToManyField(School, blank=True)
    ticket = models.CharField(
        max_length=100,
        blank=True, null=True,
    )

    class Meta:
        ordering = ['created']
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __unicode__(self):
        return self.name


class ExportHistory(TimeStampedModel):

    EXPORT_TYPE = Choices(
        ('', '----------'),
        ('Makani List', _('Makani List')),
        ('Makani Raw Attendance', _('Makani Raw Attendance')),
        ('Makani Total Attendance', _('Makani Total Attendance')),
        ('Center List', _('Center List')),
        ('Bridging Absence Raw Data', _('Bridging Absence Raw Data')),
        ('Bridging Attendance Total', _('Bridging Attendance Total')),
        ('Bridging Absence Consecutive', _('Bridging Absence Consecutive')),
        ('Teacher List', _('Teacher List')),
        ('Bridging List', _('Bridging List')),
        ('School List - Bridging', _('School List - Bridging')),
        ('School List', _('School List')),
    )
    STATUS = Choices(
        ('pending', 'Pending'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    )
    export_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=EXPORT_TYPE,
        verbose_name=_('Export Type')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Modified by'),
    )
    partner_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Partner name')
    )
    fields = JSONField(blank=True, null=True)
    file_format = models.CharField(max_length=10, default='csv')
    file_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS,
        default=STATUS.pending,
    )

    class Meta:
        ordering = ['-created']
        verbose_name = "Export History"
        verbose_name_plural = "Export History"


class UserActivity(models.Model):
    username = models.CharField(max_length=255, db_index=True)
    path = models.TextField()
    method = models.CharField(max_length=10, db_index=True)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['username', '-timestamp'], name='user_activity_user_ts_idx'),
            models.Index(fields=['method', '-timestamp'], name='user_activity_method_ts_idx'),
        ]

    def __str__(self):
        return "{} - {} {}".format(self.username, self.method, self.path)


class AdolescentUpload(TimeStampedModel):
    file = models.FileField(upload_to='uploads/adolescent_imports')
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True,
        null=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=_('Uploaded by')
    )
    failed_file = models.FileField(
        upload_to='uploads/adolescent_imports',
        blank=True,
        null=True,
    )
    processed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']
        verbose_name = 'Adolescent upload'
        verbose_name_plural = 'Adolescent uploads'

    def __str__(self):
        return self.file.name
