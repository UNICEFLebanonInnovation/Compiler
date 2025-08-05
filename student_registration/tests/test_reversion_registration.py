import reversion
from student_registration.child.models import Child
from student_registration.mscc.models import Registration as MsccRegistration
from student_registration.youth.models import Registration as YouthRegistration
from student_registration.clm.models import CLM


def test_models_registered_with_reversion():
    assert reversion.is_registered(Child)
    assert reversion.is_registered(MsccRegistration)
    assert reversion.is_registered(YouthRegistration)
    assert reversion.is_registered(CLM)
