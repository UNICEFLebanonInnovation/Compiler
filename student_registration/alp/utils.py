

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
    except ALPReferMatrix.DoesNotExist:
        matrix = ALPReferMatrix.objects.get(id=50)

    if total_grades >= matrix.success_grade:
        return matrix.success_refer_to
    else:
        return matrix.fail_refer_to


def assign_to_level(level, exam_total):
    from student_registration.schools.models import ALPAssignmentMatrix
    from student_registration.schools.models import EducationLevel

    try:
        Education_Level = EducationLevel.objects.filter(name=level)
        for education_level in Education_Level:
            if education_level.new_calculation:
                alp_matrix = ALPAssignmentMatrix.objects.filter(level=level, matrix_type='N')
                for matrix in alp_matrix:
                    if ((exam_total > matrix.range_start*education_level.coefficient_score*education_level.note
                         * education_level.sum_subjects/100)and (exam_total <= matrix.range_end
                                                                 * education_level.coefficient_score
                                                                 * education_level.note
                                                                 * education_level.sum_subjects/100)):
                        return matrix.refer_to
                        break

            else:
                result = ALPAssignmentMatrix.objects.get(level=level, range_start__gt=exam_total,
                                                         range_end__lte=exam_total)
                return result.refer_to
    except ALPAssignmentMatrix.DoesNotExist:
        return None
