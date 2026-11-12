from importlib import import_module
from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.messages.storage.fallback import FallbackStorage
from django.template.loader import get_template
from django.test import RequestFactory

from student_registration.schools.models import PartnerOrganization
from student_registration.youth.models import EnrolledPrograms, Registration
from student_registration.youth.program_form import EnrolledProgramsForm
from student_registration.youth.views import MainListView, ProfileView


@pytest.fixture
def partners(db):
    return [PartnerOrganization.objects.create(name=name, is_youth=True)
            for name in ['Registration partner', 'User partner', 'Other partner']]


def request_for(partner, group='YOUTH_PARTNER', data=None):
    user = get_user_model().objects.create(username='viewer', partner=partner)
    user.groups.add(Group.objects.get_or_create(name=group)[0])
    factory = RequestFactory()
    request = factory.post('/', data) if data is not None else factory.get('/')
    request.user = user
    request.session = {}
    request._messages = FallbackStorage(request)
    return request


@pytest.mark.parametrize('use_user_partner', [True, False])
@pytest.mark.parametrize('editing', [True, False])
def test_partner_is_hidden_and_derived_on_save(partners, use_user_partner, editing):
    registration = Registration.objects.create(partner=partners[0])
    enrollment = EnrolledPrograms.objects.create(registration=registration) if editing else None
    request = request_for(partners[1] if use_user_partner else None, data={
        'partner': partners[2].pk,
    })
    form = EnrolledProgramsForm(
        registry=registration.pk, instance=enrollment.pk if enrollment else None,
        request=request,
    )
    expected = partners[1] if use_user_partner else partners[0]
    assert form.fields['partner'].widget.is_hidden
    assert form.initial['partner'] == expected.pk
    saved = form.save(request=request, registry=registration.pk,
                      instance=enrollment.pk if enrollment else None)
    saved.refresh_from_db()
    assert saved.partner == expected  # Forged POST partner is ignored.


@pytest.mark.parametrize('use_user_partner', [True, False])
def test_bulk_partner_is_derived_for_each_registration(partners, use_user_partner):
    registrations = [Registration.objects.create(partner=partner) for partner in partners[:2]]
    request = request_for(partners[2] if use_user_partner else None, data={})
    form = EnrolledProgramsForm(request=request)
    form.cleaned_data = {'selected_registration_ids': ','.join(str(r.pk) for r in registrations)}
    saved = form.save_bulk(request=request)
    assert [p.partner_id for p in saved] == (
        [partners[2].pk] * 2 if use_user_partner else [r.partner_id for r in registrations]
    )


def test_list_includes_owned_and_enrolled_registrations_without_duplicates(partners):
    owned, shared, unrelated, deleted = [Registration.objects.create(
        partner=partner, deleted=deleted
    ) for partner, deleted in [
        (partners[0], False), (partners[1], False),
        (partners[1], False), (partners[0], True),
    ]]
    for _ in range(2):
        EnrolledPrograms.objects.create(registration=shared, partner=partners[0])
    view = MainListView()
    view.request = request_for(partners[0])
    assert list(view.get_queryset()) == [shared, owned]


def test_profile_only_exposes_current_partner_enrollments(partners):
    registration = Registration.objects.create(partner=partners[0])
    own = EnrolledPrograms.objects.create(registration=registration, partner=partners[1])
    EnrolledPrograms.objects.create(registration=registration, partner=partners[0])
    view = ProfileView()
    view.request = request_for(partners[1])
    view.kwargs = {'pk': registration.pk}
    assert list(view.get_context_data()['enrolled_programs']) == [own]
    get_template('youth/child_info_tab.html')


def test_backfill_uses_registration_partner(partners):
    from django.apps import apps
    from django.db import connection
    registration = Registration.objects.create(partner=partners[0])
    enrollment = EnrolledPrograms.objects.create(registration=registration)
    orphan = EnrolledPrograms.objects.create()
    migration = import_module('student_registration.youth.migrations.0039_enrolledprograms_partner')
    migration.populate_partners(apps, SimpleNamespace(connection=connection))
    enrollment.refresh_from_db()
    orphan.refresh_from_db()
    assert enrollment.partner_id == partners[0].pk
    assert orphan.partner_id is None


@pytest.mark.parametrize('group, expected_count', [('YOUTH_UNICEF', 1), ('YOUTH_PARTNER', 0)])
def test_profile_without_partner_preserves_unicef_access_only(partners, group, expected_count):
    registration = Registration.objects.create(partner=partners[0])
    EnrolledPrograms.objects.create(registration=registration, partner=partners[0])
    view = ProfileView()
    view.request = request_for(None, group=group)
    view.kwargs = {'pk': registration.pk}
    assert view.get_context_data()['enrolled_programs'].count() == expected_count


@pytest.mark.parametrize('group, expected_count', [('YOUTH_UNICEF', 1), ('YOUTH_PARTNER', 0)])
def test_list_without_partner_preserves_unicef_access_only(partners, group, expected_count):
    Registration.objects.create(partner=partners[0])
    view = MainListView()
    view.request = request_for(None, group=group)
    assert view.get_queryset().count() == expected_count
