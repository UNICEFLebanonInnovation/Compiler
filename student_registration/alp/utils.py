

def refer_to_level(
                student_age,
                registered_in_level,
                total_grades
            ):

    from student_registration.schools.models import ALPReferMatrix

    if not student_age or not registered_in_level:
        return None

    if student_age < 9:
        student_age = 9
    if student_age > 17:
        student_age = 17
    try:
        matrix = ALPReferMatrix.objects.get(age=student_age, level=registered_in_level)
        if total_grades >= matrix.success_grade:
            return matrix.success_refer_to
        else:
            return matrix.fail_refer_to
    except ALPReferMatrix.DoesNotExist:
        default = ALPReferMatrix.objects.get(id=50)
        return default.fail_refer_to

