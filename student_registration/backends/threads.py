import time
import datetime
import logging
from django.utils import timezone
import threading

from student_registration.students.utils import generate_bulk_unique_id, get_bulk_programmes

logger = logging.getLogger(__name__)


class ChildUIDThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        thread.daemon = True
        thread.start()

    def run(self):
        from student_registration.child.models import Child

        records = Child.objects.exclude(unicef_id__isnull=False)[0:10000]

        payload = {
            "individuals": [
                {
                    "id": record.pk,
                    "first_name": record.first_name,
                    "father_name": record.father_name,
                    "last_name": record.last_name,
                    "mother_name": record.mother_fullname,
                    "date_of_birth": record.birthdate,
                    "nationality": record.nationality_name_en,
                    "gender": record.gender
                }
                for record in records
            ]
        }

        result = generate_bulk_unique_id(payload)

        # Update Django records in bulk
        for record in records:
            if record.pk in result:
                record.unicef_id = result[record.pk]
                record.save()

        # for django >= 2.2
        # Student.objects.bulk_update(records, ['unicef_id'])

        logger.info("End Thread")


class AllChildUIDThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        thread.daemon = True
        thread.start()

    def run(self):

        from student_registration.child.models import Child

        records = Child.objects.all()

        slicing = 10000

        for key in range(1, 7):
            batch = records[slicing * key:(key + 1) * slicing]  # Correct slicing

            payload = {
                "individuals": [
                    {
                        "id": record.pk,
                        "first_name": record.first_name,
                        "father_name": record.father_name,
                        "last_name": record.last_name,
                        "mother_name": record.mother_fullname,
                        "date_of_birth": record.birthdate,
                        "nationality": record.nationality_name_en,
                        "gender": record.gender
                    }
                    for record in batch
                ]
            }

            result = generate_bulk_unique_id(payload)

            # Update Django records in bulk
            for record in batch:
                if record.pk in result:
                    record.unicef_id = result[record.pk]
                    record.save()

        # for django >= 2.2
        # Student.objects.bulk_update(records, ['unicef_id'])

        logger.info("End Thread")


class CashProgrammeThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        thread.daemon = True
        thread.start()

    def run(self):
        from student_registration.child.models import Child

        records = Child.objects.exclude(unicef_id__isnull=True, cash_programmes__isnull=False)

        slicing = 10

        for key in range(1, 100):
            batch = records[slicing * key:(key + 1) * slicing]  # Correct slicing

            payload = {
                "individuals": [staff.unicef_id for staff in batch]
            }

            result = get_bulk_programmes(payload)

            # Update Django records in bulk
            for record in batch:
                if record.pk in result:
                    logger.info(result[record.unicef_id])
                    record.cash_programmes = result[record.unicef_id]
                    record.save()
                else:
                    record.cash_programmes = {}
                    record.save()

        logger.info("End Thread")


def generate_child_programmes():
    th = CashProgrammeThreading(interval=4)


def generate_child_unique_id():
    th = ChildUIDThreading(interval=5)


def generate_all_child_unique_id():
    th = AllChildUIDThreading(interval=6)


class StudentUIDThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        logger.info("Start Thread")
        thread.daemon = True
        thread.start()

    def run(self):
        from student_registration.students.models import Student
        from student_registration.clm.models import Bridging

        records = Student.objects.filter(id__in=Bridging.objects.values('student_id'), unicef_id__isnull=True)[:1000]

        payload = {
            "individuals": [
                {
                    "id": record.pk,
                    "first_name": record.first_name,
                    "father_name": record.father_name,
                    "last_name": record.last_name,
                    "mother_name": record.mother_fullname,
                    "date_of_birth": record.birthdate,
                    "nationality": record.nationality_name_en,
                    "gender": record.sex
                }
                for record in records
            ]
        }

        result = generate_bulk_unique_id(payload)
        # print(result)

        # Update Django records in bulk
        for record in records:
            if record.pk in result:
                record.unicef_id = result[record.pk]
                record.save()

        # for django >= 2.2
        # Student.objects.bulk_update(records, ['unicef_id'])

        logger.info("End Thread")

        return True


def generate_student_unique_id():
    th = StudentUIDThreading(interval=5)
    return th


def generate_all_teacher_unique_id():
    th = AllTeacherUIDThreading(interval=6)


class AllTeacherUIDThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        thread.daemon = True
        thread.start()

    def run(self):

        from student_registration.students.models import Teacher

        records = Teacher.objects.filter(unicef_id__isnull=True)

        slicing = 100

        for key in range(1, 7):
            batch = records[slicing * key:(key + 1) * slicing]  # Correct slicing

            print(batch)

            payload = {
                "individuals": [
                    {
                        "id": record.pk,
                        "first_name": record.first_name,
                        "father_name": record.father_name,
                        "last_name": record.last_name,
                        "mother_name": 'hala',
                        "date_of_birth": '2000-01-01',
                        "nationality": 'lebanese',
                        "gender": record.sex
                    }
                    for record in batch
                ]
            }

            result = generate_bulk_unique_id(payload)

            # Update Django records in bulk
            for record in records:
                if record.pk in result:
                    print(result[record.pk])
                    record.unicef_id = result[record.pk]
                    record.save()

        # for django >= 2.2
        # Teacher.objects.bulk_update(records, ['unicef_id'])

        print("End Thread")


class TeacherUIDThreading(object):
    def __init__(self, interval=1):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())

        logger.info("Start Thread")
        thread.daemon = True
        thread.start()

    def run(self):
        from student_registration.students.models import Teacher

        records = Teacher.objects.exclude(unicef_id__isnull=False)[0:10000]

        payload = {
            "individuals": [
                {
                    "id": record.pk,
                    "first_name": record.first_name,
                    "father_name": record.father_name,
                    "last_name": record.last_name,
                    "mother_name": 'hala',
                    "date_of_birth": '2000-01-01',
                    "nationality": 'lebanese',
                    "gender": record.sex
                }
                for record in records
            ]
        }

        result = generate_bulk_unique_id(payload)
        # print(result)

        # Update Django records in bulk
        for record in records:
            if record.pk in result:
                record.unicef_id = result[record.pk]
                record.save()

        # for django >= 2.2
        # Student.objects.bulk_update(records, ['unicef_id'])

        logger.info("End Thread")

        return True


def generate_teacher_unique_id():
    th = TeacherUIDThreading(interval=5)
    return th
