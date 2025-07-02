from student_registration.dashboard.views import RunExporterViewSet


def test_group_required():
    """RunExporter should only be accessible to MEHE."""
    assert RunExporterViewSet.group_required == [u"MEHE"]
