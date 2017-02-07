db.attendances_by_day.aggregate([
    {
       '$lookup':
         {
           from: 'students',
           localField: 'value.student',
           foreignField: 'id',
           as: 'gender'
         }
    },
    {
        '$project': {
            'school': '$value.school',
            'date': '$value.date',
            'validation_date': '$value.validation_date',
            'student': '$value.student',
            'gender': {'$arrayElemAt': [ "$gender", 0 ] },
            'Attended': {"$cond": ["$value.attended", 1, 0]},
            'Absent': {"$cond": [{"$not": "$value.attended"}, 1, 0]},
            'Attended Male': {"$cond": [{'$and': [{"$eq": ["$value.gender", "Male"]}, "$value.attended"]}, 1, 0]},
            'Attended Female': {"$cond": [{'$and': [{"$eq": ["$value.gender", "Female"]}, "$value.attended"]}, 1, 0]},
            'Absent Male': {"$cond": [{'$and': [{"$eq": ["$value.gender", "Male"]}, {"$not": "$value.attended"}]}, 1, 0]},
            'Absent Female': {"$cond": [{'$and': [{"$eq": ["$value.gender", "Female"]}, {"$not": "$value.attended"}]}, 1, 0]},
        }
    },
    {
        '$group': {
            '_id': {'school': '$school', 'date': '$date'},
            'school_id': {'$first': '$school'},
            'attendance_date': {'$first': '$date'},
            'total_enrolled': {'$sum': 1},
            'total_attended': {'$sum': "$Attended"},
            'total_absences': {'$sum': "$Absent"},
            'total_attended_male': {'$sum': "$Attended Male"},
            'total_attended_female': {'$sum': "$Attended Female"},
            'total_absent_male': {'$sum': "$Absent Male"},
            'total_absent_female': {'$sum': "$Absent Female"},
            'validation_date': {'$first': "$validation_date"},
        }
    },
    {'$addFields': {'_id': {'$concat': ["$_id.school", "-", "$_id.date"]}}},
    {'$out': 'attendances_by_day_school'}
])
