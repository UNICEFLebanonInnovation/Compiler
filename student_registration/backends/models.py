from __future__ import unicode_literals, absolute_import, division

from model_utils.models import TimeStampedModel

from django.utils.translation import ugettext as _
from django.contrib.gis.db import models
from django.db.models.signals import post_save
from helpdesk.models import Ticket
from .mailer import send_messaage
from django.utils.encoding import force_text

from student_registration.users.models import User


class Exporter(TimeStampedModel):

    name = models.CharField(max_length=100)
    file_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ['created']
        verbose_name = "Exported file"
        verbose_name_plural = "Exported files"

    def __unicode__(self):
        return self.name


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


post_save.connect(send_ticket_email, sender=Ticket)
