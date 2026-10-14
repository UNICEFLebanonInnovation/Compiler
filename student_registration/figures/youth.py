"""Youth as a programme of the NeuroDB figures' night task (snapshots.py), beside Makani and Bridging.

The counting itself is ``youth.indicator_figures.build`` (unique young people per indicator, the
``registered`` and ``enrolments`` blocks, the ``power_bi`` part over ``vw_youth_data_all``). Here it runs
as one READ ONLY transaction with the counting limits (engine.read_only_transaction), ORM queries
included, and its periods are the youth reporting years plus ``"all"`` (every year).

Youth is never listed in the education index nor served at /api/figures/<programme>/ (an older NeuroDB
would store it as education figures): its snapshots are read through /api/youth/indicator-figures/.
"""

from __future__ import annotations

from student_registration.youth import indicator_figures

from . import engine


class Youth:
    name = 'youth'
    label = 'Youth'
    format_version = indicator_figures.FORMAT_VERSION

    def years(self):
        from student_registration.youth.models import Year

        return list(Year.objects.order_by('-name').values_list('name', flat=True)) + [indicator_figures.ALL]

    def current_year(self):
        return indicator_figures.current_year_name()

    def has_year(self, year):
        from student_registration.youth.models import Year

        year = str(year).strip()
        return year == indicator_figures.ALL or Year.objects.filter(name=year).exists()

    def build(self, year):
        """The payload of ``year`` (a year's name, or "all"), counted under the read-only limits."""
        from student_registration.youth.models import Year

        year = str(year).strip()
        with engine.read_only_transaction() as alias:
            chosen = None
            if year != indicator_figures.ALL:
                chosen = Year.objects.using(alias).get(name=year)
            return indicator_figures.build(chosen, alias=alias)
