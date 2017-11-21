

def initiate_grading(enrollment, term):
    from .models import EnrollmentGrading
    grade = EnrollmentGrading.objects.create(enrollment=enrollment, exam_term=term)
    grade.save()
