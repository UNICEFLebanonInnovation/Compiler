from __future__ import unicode_literals, absolute_import, division

from django.db import models
from django.conf import settings
from model_utils import Choices
from model_utils.models import TimeStampedModel
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils.translation import ugettext as _


class LocationType(models.Model):
    name = models.CharField(max_length=64, unique=True)
    name_en = models.CharField(max_length=145, blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Location Type'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Location(MPTTModel):

    name = models.CharField(max_length=254)
    name_en = models.CharField(max_length=254, blank=True, null=True)
    type = models.ForeignKey(LocationType, verbose_name='Location Type')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    p_code = models.CharField(max_length=32, blank=True, null=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

    def __str__(self):
        return self.name

    def __unicode__(self):
        # if self.type:
        #     return u'{} - {}'.format(
        #         self.name,
        #         self.type.name
        #     )
        return self.name

    class Meta:
        unique_together = ('name', 'type', 'p_code')
        ordering = ['name']


class Center(TimeStampedModel):
    TYPE = Choices(
        ('Municipality', _('Municipality')),
        ('Collective Settlement', _('Collective Settlement')),
        ('Informal Settlement', _('Informal Settlement')),
        ('Welfare Center', _('Welfare Center')),
        ('Community Hub', _('Community Hub')),
    )
    PROVIDED_PACKAGES = Choices(
        ('Education', 'Education'),
        ('Youth', 'Youth'),
        ('Health & Nutrition', 'Health & Nutrition'),
        ('Child Protection', 'Child Protection'),
        ('Social Protection', 'Social Protection'),
    )
    EDUCATION_PROGRAM = Choices(
        ('BLN', 'BLN'),
        ('ABLN', 'ABLN'),
        ('RS', 'RS'),
        ('CBECE', 'CBECE')
    )
    YOUTH_PROGRAM = Choices(
        ('YBLN', 'YBLN'),
        ('YFS', 'YFS')
    )
    YES_NO = Choices(
        ('', '----------'),
        ('Yes', _("Yes")),
        ('No', _("No"))
    )

    name = models.CharField(max_length=100)
    governorate = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Governorate')
    )
    caza = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Caza')
    )
    cadaster = models.ForeignKey(
        Location,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cadaster')
    )
    longitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Center GPS (longitude)')
    )
    latitude = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Center GPS (latitude)')
    )
    manager_name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Center Manager name')
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Phone number')
    )
    email = models.EmailField(blank=True, max_length=254, verbose_name='Email')

    type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=TYPE,
        verbose_name=_('Type')
    )
    provided_packages = ArrayField(
        models.CharField(
            choices=PROVIDED_PACKAGES,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Provided Services')
    )
    education_programs = ArrayField(
        models.CharField(
            choices=EDUCATION_PROGRAM,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Education Program')
    )
    youth_programs = ArrayField(
        models.CharField(
            choices=YOUTH_PROGRAM,
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Youth Program')
    )
    admin_staff_number = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 300)),
        verbose_name=_('Number of Admin staff in the centers')
    )
    cwd_accessible = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Is the center accessible for CWD ?')
    )
    p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('P-Code')
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False, null=True,
        related_name='+',
    )
    modified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Modified by'),
    )
    @property
    def total_children(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).count()

    @property
    def total_male(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Male').count()

    @property
    def total_female(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id, child__gender='Female').count()

    @property
    def total_disability(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).exclude(child__disability__name_en='No').count()

    @property
    def total_disability_male(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id,child__gender='Male').exclude(child__disability__name_en='No').count()

    @property
    def total_disability_female(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id,child__gender='Female').exclude(child__disability__name_en='No').count()


    @property
    def total_lebanese(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id,child__nationality__code='LEB').count()

    @property
    def total_non_lebanese(self):
        from student_registration.mscc.models import Registration
        return Registration.objects.filter(center=self.id).exclude(child__nationality__code='LEB').count()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


    class Meta:
        ordering = ['name']
        verbose_name = "Center"
        verbose_name_plural = "Centers"
