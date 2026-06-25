from importlib import import_module

from django.apps import apps

_MSCC_APP = 'mscc'
_MSCC_MODELS = import_module('student_registration.' + _MSCC_APP + '.models')

Registration = apps.get_model(_MSCC_APP, 'Registration', require_ready=False)
Referral = apps.get_model(_MSCC_APP, 'Referral', require_ready=False)
EducationAssessment = apps.get_model(_MSCC_APP, 'EducationAssessment', require_ready=False)
EducationHistory = apps.get_model(_MSCC_APP, 'EducationHistory', require_ready=False)
EducationService = apps.get_model(_MSCC_APP, 'EducationService', require_ready=False)
EducationRSService = apps.get_model(_MSCC_APP, 'EducationRSService', require_ready=False)
EducationProgrammeAssessment = apps.get_model(_MSCC_APP, 'EducationProgrammeAssessment', require_ready=False)
EducationProgrammeWLAssessment = apps.get_model(_MSCC_APP, 'EducationProgrammeWLAssessment', require_ready=False)
Packages = apps.get_model(_MSCC_APP, 'Packages', require_ready=False)
ProvidedServices = apps.get_model(_MSCC_APP, 'ProvidedServices', require_ready=False)
Round = apps.get_model(_MSCC_APP, 'Round', require_ready=False)
ServiceProgramOption = apps.get_model(_MSCC_APP, 'ServiceProgramOption', require_ready=False)
TarlAssessment = apps.get_model(_MSCC_APP, 'TarlAssessment', require_ready=False)

YES_NO = _MSCC_MODELS.YES_NO
PACKAGE_TYPES = _MSCC_MODELS.PACKAGE_TYPES

__all__ = [
    'EducationAssessment',
    'EducationHistory',
    'EducationProgrammeAssessment',
    'EducationProgrammeWLAssessment',
    'EducationRSService',
    'EducationService',
    'PACKAGE_TYPES',
    'Packages',
    'ProvidedServices',
    'Referral',
    'Registration',
    'Round',
    'ServiceProgramOption',
    'TarlAssessment',
    'YES_NO',
]
