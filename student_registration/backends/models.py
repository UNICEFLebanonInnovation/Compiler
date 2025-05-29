from __future__ import unicode_literals, absolute_import, division

from django.conf import settings
from django.utils.translation import ugettext as _
from django.db import models
# from django.contrib.gis.db import models
from django.db.models.signals import post_save
from django.utils.encoding import force_str

from model_utils.models import TimeStampedModel
from model_utils import Choices
from helpdesk.models import Ticket

from .mailer import send_messaage
from student_registration.users.models import User
from student_registration.schools.models import School


class Exporter(TimeStampedModel):

    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)
    exported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
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
        related_name='+'
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
        verbose_name=_('Modified by'),
    )
    partner_name = models.CharField(
        max_length=64,
        db_index=True,
        blank=True, null=True,
        verbose_name=_('Partner name')
    )

    class Meta:
        ordering = ['id']
        verbose_name = "Export History"
        verbose_name_plural = "Export History"


class UserActivity(models.Model):
    username = models.CharField(max_length=255)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    data = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{} - {} {}".format(self.user, self.method, self.path)


def create_helpdesk_notification(sender, instance, created, **kwargs):
    title = ''
    comments = ''
    submitter = None
    school = None
    submitter_email = instance.submitter_email
    try:
        status = force_str(dict(Ticket.STATUS_CHOICES)[instance.status]) if instance.status else ''
        if instance.followup_set:
            comments = instance.followup_set.all().last().comment if instance.followup_set.all().last() else ''
            # comments = '\r\n'.join([f.comment for f in instance.followup_set.all()])

        if instance.submitter_email:
            submitter = User.objects.filter(email=submitter_email).first()
        if submitter:
            school = submitter.school

        title = '{} - {} - {}'.format(
            instance.queue,
            instance.title,
            status,
        )
    except Exception as ex:
        pass

    try:
        notification = Notification.objects.get(
            type='helpdesk',
            school=school,
            ticket=instance.id
        )
        notification.status = False
        notification.name = title
        notification.description = instance.description
        notification.comments = comments
        notification.save()

    except Notification.DoesNotExist as ex:
        Notification.objects.create(
            name=title,
            description=instance.description,
            comments=comments,
            type='helpdesk',
            school=school,
            ticket=instance.id
        )


def send_ticket_email(sender, instance, created, **kwargs):
    comments = ''
    submitter = None
    school = None
    submitter_email = instance.submitter_email
    submitter_name = None
    queue = instance.queue
    try:
        status = force_str(dict(Ticket.STATUS_CHOICES)[instance.status]) if instance.status else ''
        if instance.followup_set:
            comments = '\r\n'.join([f.comment for f in instance.followup_set.all()])

        if instance.submitter_email:
            submitter = User.objects.filter(email=submitter_email).first()
        if submitter:
            school = submitter.school
            submitter_email = school.email
            submitter_name = '{} - {}'.format(school.it_name, school.it_phone_number)

        text = 'Ticket type: {}\r\nTitle: {}\r\nDescription: {}\r\nSchool: {}\r\n{}\r\nStatus: {}\r\n \r\n \r\nComments: {}'.format(
            instance.queue,
            instance.title,
            instance.description,
            school,
            submitter_name,
            status,
            comments
        )

        messages_sent_to = [submitter_email, 'galachkar@mehe.gov.lb', 'ghrizk@mehe.gov.lb']
        if instance.submitter_email:
            subject = '{} - {}: {} [{}]'.format('MDB2', 'Helpdesk', instance.title, status)
            # subject = instance.title
            send_messaage(subject, text, queue.email_address, messages_sent_to)
    except Exception as ex:
        pass


# post_save.connect(send_ticket_email, sender=Ticket)
post_save.connect(create_helpdesk_notification, sender=Ticket)
