from __future__ import unicode_literals, absolute_import, division

from model_utils.models import TimeStampedModel
from model_utils import Choices

from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from helpdesk.models import Ticket
from .mailer import send_messaage
from django.utils.encoding import force_text

from student_registration.users.models import User
from student_registration.schools.models import School


class Exporter(TimeStampedModel):

    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['created']
        verbose_name = "Exported file"
        verbose_name_plural = "Exported files"

    def __unicode__(self):
        return self.name


class Notification(TimeStampedModel):

    name = models.CharField(max_length=100, blank=False, null=True)
    type = models.CharField(
        choices=Choices(
            ('general', 'General'),
            ('helpdesk', 'Helpdesk'),
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


def create_helpdesk_notification(sender, instance, created, **kwargs):
    title = ''
    comments = ''
    submitter = None
    school = None
    submitter_email = instance.submitter_email
    try:
        status = force_text(dict(Ticket.STATUS_CHOICES)[instance.status]) if instance.status else ''
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
        status = force_text(dict(Ticket.STATUS_CHOICES)[instance.status]) if instance.status else ''
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
