class MSCC(CLM):
    YES_NO = Choices(
        ('', '----------'),
        ('yes', _("Yes")),
        ('no', _("No")),
    )
    miss_school_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('miss_school_date')
    )
    LEARNING_RESULT = Choices(
        ('', _('Learning result')),
        ('Transition to FE', _('Transition to FE')),
        ('Repeat the school year', _('Repeat the school year')),
        ('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL)', _('Refer to a UNICEF Youth Programme (skills tranining, CBT, GIL)')),
        ('Transition to TVET', _('Transition to TVET')),
        ('Internship or volunteering opportunity', _('Internship or volunteering opportunity')),
    )
    REGISTRATION_LEVEL = (
        ('', '----------'),
        ('level_one', _('Level one')),
        ('level_two', _('Level two')),
        ('level_three', _('Level three'))
    )
    MAIN_CAREGIVER = (
        ('', '----------'),
        ('mother', _('Mother')),
        ('father', _('Father')),
        ('other', _('Other')),
    )
    CENTER_TYPE = (
        ('', '----------'),
        ('Municipality', _('Municipality')),
        ('Collective Settlement', _('Collective Settlement')),
        ('Informal Settlement', _('Informal Settlement')),
        ('Welfare Center', _('Welfare Center')),
        ('Collective Settlement', _('Collective Settlement')),
    )
    cycle = models.ForeignKey(
        Cycle,
        blank=True, null=True,
        related_name='+',
        verbose_name=_('Cycle')
    )
    center_p_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Center P-code')
    )

    center_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=CENTER_TYPE,
        verbose_name=_('Center Type')
    )
    referral = ArrayField(
        models.CharField(
            choices=CLM.REFERRAL,
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Referral')
    )

    learning_result = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=LEARNING_RESULT,
        verbose_name=_('Learning result')
    )
    learning_result_other = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    first_attendance_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('First attendance date')
    )
    round_start_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Round start date')
    )
    registration_level = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=REGISTRATION_LEVEL,
        verbose_name=_('Registration level')
    )
    main_caregiver = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=MAIN_CAREGIVER,
        verbose_name=_('Main Caregiver')
    )

    main_caregiver_nationality = models.ForeignKey(
        Nationality,
        blank=False, null=True,
        related_name='+',
        verbose_name=_('Main Caregiver Nationality')
    )
    main_caregiver_nationality_other = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('specify')
    )

    other_caregiver_relationship = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name=_('Other Caregiver Relationship')
    )

    student_number_children = models.IntegerField(
        blank=True,
        null=True,
        choices=((x, x) for x in range(0, 20)),
        verbose_name=_('How many children does this child have?')
    )
    phone_owner = models.CharField(
        max_length=100,
        blank=False,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Phone Owner')
    )
    second_phone_owner = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('main_caregiver', _('Phone Main Caregiver')),
            ('family member', _('Family Member')),
            ('neighbors', _('Neighbors')),
            ('shawish', _('Shawish')),
        ),
        verbose_name=_('Second Phone Owner')
    )
    second_phone_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number')
    )
    second_phone_number_confirm = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name=_('Second Phone number confirm')
    )

    source_of_identification = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Dirassa', _('Dirassa')),
            ('Awarness Session', _('Awarness Session')),
            ('Child''s parents', _('Child''s parents')),
            ('From Hosted Community', _('From Hosted Community')),
            ('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ',
             _('Sector Partners referral (CP, Education, Health, Wash, Youth, Palestenian program...) ')),
            ('From Profiling Database', _('From Profiling Database')),
            ('From Other NGO', _('From Other NGO')),
            ('From Displaced Community', _('From Displaced Community')),
            ('Referred by the municipality/Other formal sources', _('Referred by the municipality/Other formal sources')),
            ('Other Sources', _('Other Sources')),
        ),
        verbose_name=_('Source of identification of the child')
    )
    cash_support_programmes = ArrayField(
        models.CharField(
            choices=Choices(
                ('', '----------'),
                ('Haddi', _('Haddi')),
                ('Education Cash assistance', _('Education Cash assistance')),
                ('UNHCR cash assistance', _('UNHCR cash assistance')),
                ('WFP cash assistance', _('WFP cash assistance')),
            ),
            max_length=100,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Cash support programmes that child is already benefitting from')
    )
    packages_received = ArrayField(
        models.CharField(
            choices=Choices(
                ('', '----------'),
                ('Early Childhood Development', _('Early Childhood Development')),
                ('Education', _('Education')),
                ('Child Protection/Psychosocial support', _('Child Protection/Psychosocial support')),
                ('Youth Empowerment and engagement', _('Youth Empowerment and engagement')),
                ('Health and Nutrition', _('Health and Nutrition')),
                ('Parental and Caregiver Support', _('Parental and Caregiver Support')),
                ('Social Cash Assistance', _('Social Cash Assistance')),
            ),
            max_length=200,
            blank=True,
            null=True,
        ),
        blank=True,
        null=True,
        verbose_name=_('Packages received/to be provided to child under MSCC')
    )
    education_status = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('out of school', _('No Registered in any school before')),
            ('Was registered in formal school but didnt continue', _('Was registered in formal school but didnt continue')),
            ('Was registered in non formal program and was referred to MSCC', _('Was registered in non formal program and was referred to MSCC')),
            ('Was registered in non formal program but did not continue', _('Was registered in non formal program but did not continue')),
            ('Was enrolled in TVET Programs', _('Was enrolled in TVET Programse'))
        ),
        verbose_name=_('Education status')
    )
    dropout_program = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Was registered in CBECE level 1-2', _('Was registered in CBECE level 1-2')),
            ('other	please specify	Was registered in BLN program', _('other please specify	Was registered in BLN program')),
            ('Was registered in ALP program and didnt continue', _('Was registered in ALP program and didnt continue')),
            ('Was enrolled in Dirasa', _('Was enrolled in Dirasa')),
        ),
        verbose_name=_('Dropout Program')
    )
    education_program = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('BLN Level 1', _('BLN Level 1')),
            ('BLN Level 2', _('BLN Level 2')),
            ('YBLN', _('YBLN')),
            ('YFNL', _('YFNL')),
            ('CBECE Level 3', _('CBECE Level 3')),
            ('Retention Support', _('Retention Support')),
        ),
        verbose_name=_('Education Program')
    )
    volunteering_experience = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Does the adolescent have any volunteering experience?')
    )
    previous_community_initiative = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Was the adolescent part of any previous community based initiative?')
    )
    enrollement_reason = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_('What is the reason for the adolescent enrollement in the programme?')
    )
    pre_tests_administered = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Were pre-tests administered to assess adolescents level?')
    )
    test_diagnostic_done = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent undertake any Post Diagnostic tests?')
    )
    receive_passing_grade = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent receive a passing grade for the tests?')
    )
    life_skills_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the life skills package?')
    )
    participate_volunteering = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate in any volunteering opportunity during the course of the program?')
    )
    volunteering_specify = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Outreach', _('Outreach')),
            ('Data entry', _('Data entry')),
            ('Admin work', _('Admin work')),
            ('Awareness raising sessions', _('Awareness raising sessions')),
            ('Empowerment and leadership', _('Empowerment and leadership')),
            ('Other', _('Other')),
        ),
        verbose_name=_('Please specify the volunteering opportunity')
    )
    social_course = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent benefit from any social innovation/entrepreneurship course?')
    )
    yfs_course_completed = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent complete the YFS course?')
    )
    training_material = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Printed workbook', _('Printed workbook')),
            ('Tablets', _('Tablets')),
            ('Access to digital content (learning Passport) ', _('Access to digital content (learning Passport) ')),
            ('Other', _('Other')),
        ),
        verbose_name=_('What training material was provided?')
    )
    participate_community_initiatives = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        choices=YES_NO,
        verbose_name=_('Did the adolescent participate/come up in community based initiatives?')
    )
    community_initiatives_specify = models.TextField(
        blank=True, null=True,
        verbose_name=_('Please specify')
    )
    adolescent_attendance = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        choices=Choices(
            ('', '----------'),
            ('Full attendance', _('Full attendance')),
            ('Absence for less than 5 days', _('Absence for less than 5 days')),
            ('Absence for more than 5 days', _('Absence for more than 5 days')),
            ('Dropout', _('Dropout')),
        ),
        verbose_name=_('Adolescent attendance')
    )
    adolescent_dropout_reason = models.TextField(
        blank=True, null=True,
        verbose_name=_('Reason for dropout')
    )
    adolescent_dropout_date = models.DateField(
        blank=True,
        null=True,
        verbose_name=_('Dropout Date')
    )

    def assessment_form(self, stage, assessment_slug, callback=''):
        try:
            assessment = Assessment.objects.get(slug=assessment_slug)
            return '{form}?d[status]={status}&d[enrollment_id]={enrollment_id}&d[enrollment_model]=MSCC&returnURL={callback}'.format(
                form=assessment.assessment_form,
                status=stage,
                enrollment_id=self.id,
                callback=callback
            )
        except Assessment.DoesNotExist as ex:
            return ''

    def pre_assessment_form(self):
        return self.assessment_form(stage='pre_test', assessment_slug='pre_test')

    def post_assessment_form(self):
        return self.assessment_form(stage='post_test', assessment_slug='post_test')

    class Meta:
        ordering = ['-id']
        verbose_name = "MSCC"
        verbose_name_plural = "MSCC"
