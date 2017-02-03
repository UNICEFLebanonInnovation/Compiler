var map_function = function () {

    var lookup = {};
    for (var index in this.students) {
        student = this.students[index];
        lookup[student.student_id] = student;
    }

    for (var date in this.attendance) {
        day = this.attendance[date];
        for (var student in day['students']) {

            var key = this.school + '-' + date + '-' + student;
            record = day['students'][student];

            var gender = ((lookup.hasOwnProperty(student)) ? lookup[student].gender : null);

            var doc = {
                date: new Date(date.split("-").reverse().join("-")),
                school: this.school,
                class: this.class_id,
                section: this.section_id,
                location: this.location_id,
                student: student,
                gender: gender,
                attended: record.status,
                reason: record.reason,
                validation_date: ((day.hasOwnProperty('validation_date')) ? new Date(day.validation_date.split("-").reverse().join("-")) : null)

            };
            emit(key, doc);
        }
    }
};


db.runCommand({
    'mapReduce': 'attendances',
    'map': map_function,
    'reduce': function (key, values) {
        return values[0];
    },
    'out': {replace: 'attendances_by_day'}
})
