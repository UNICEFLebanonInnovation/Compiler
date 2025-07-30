import json
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from django.db import models

from student_registration.backends.models import UserActivity
from student_registration.user_activity import get_current_user


def _model_to_dict(instance):
    return {field.name: getattr(instance, field.name) for field in instance._meta.fields}


@receiver(pre_save)
def store_previous_state(sender, instance, **kwargs):
    if not issubclass(sender, models.Model) or sender is UserActivity:
        return
    if instance.pk:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            instance._activity_prev_state = None
        else:
            instance._activity_prev_state = _model_to_dict(old)
    else:
        instance._activity_prev_state = None


@receiver(post_save)
def log_model_changes(sender, instance, created, **kwargs):
    if sender is UserActivity:
        return
    user = get_current_user()
    if not user or not user.is_authenticated:
        return
    before = getattr(instance, "_activity_prev_state", None)
    if created or not before:
        return
    after = _model_to_dict(instance)
    changed = {
        field: {"before": before.get(field), "after": after.get(field)}
        for field in after
        if before.get(field) != after.get(field)
    }
    if changed:
        UserActivity.objects.create(
            username=user.username,
            path=f"{sender._meta.app_label}.{sender._meta.model_name}:{instance.pk}",
            method="UPDATE",
            data=json.dumps(after),
            changed_data=json.dumps(changed),
        )
