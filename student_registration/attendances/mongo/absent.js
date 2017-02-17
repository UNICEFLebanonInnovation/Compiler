db.getCollection('attendances_by_day').aggregate([
    {
        '$match': {
            'value.validation_date': {'$not': {'$type': 'null'}},
            'value.date': {'$gt': new Date('2016-10-01')},
            'value.date': {'$lte': new Date('2017-02-10')},
        }
    },
    {
        '$project': {
            'date': '$value.date',
            'school_id': '$value.school',
            'student_id': '$value.student',
            'attended': {'$cond': [{'$eq': ['$value.attended', true]}, 1, 0]},
            'absent': {'$cond': [{'$eq': ['$value.attended', false]}, 1, 0]},
        }
    },
    {
        '$group': {
            '_id': {'school_id': '$school_id', 'student_id': '$student_id'},
            'total_attended': {'$sum': "$attended"},
            'total_absences': {'$sum': "$absent"},
        }
    },
    {
        '$match': {
            'total_absences': {'$gt': 10},
        }
    }
])
