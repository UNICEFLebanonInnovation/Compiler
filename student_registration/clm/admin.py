from django.contrib import admin

from .models import (
    Assessment,
    Cycle,
    RSCycle,
    Site,
    Referral,
    Disability,
    BLN,
    RS,
    CBECE
)

admin.site.registry(Assessment)
admin.site.registry(Cycle)
admin.site.registry(RSCycle)
admin.site.registry(Site)
admin.site.registry(Referral)
admin.site.registry(Disability)
admin.site.registry(BLN)
admin.site.registry(RS)
admin.site.registry(CBECE)
