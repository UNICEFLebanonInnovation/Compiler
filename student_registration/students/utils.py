

def generate_id(
        first_name,
        father_name,
        last_name,
        mother_full_name,
        gender
    ):
    """
    Unique Number Proposal:
    full name total char number
    mother full name total char number
    Concatenate hash number for: first name, father name and last name
    Concatenate hash number for: mother first name and mother last name
    Sum of char code for: first name, father name and last name
    Gender type first letter
    Birthday

    :return:
    """
    import hashlib

    try:
        full_name = u'{}{}{}'.format(first_name, father_name, last_name)
        full_name_char_count = len(full_name)
        mother_name_char_count = len(mother_full_name)

        full_name_hash = int(hashlib.sha1(full_name.encode('UTF-8')).hexdigest(), 16) % 10000
        if len(str(full_name_hash)) < 4:
            full_name_hash = int(hashlib.sha1(full_name.encode('UTF-8')).hexdigest(), 16) % 10001
        if len(str(full_name_hash)) < 4:
            full_name_hash = int(hashlib.sha1(full_name.encode('UTF-8')).hexdigest(), 16) % 10002
        if len(str(full_name_hash)) < 4:
            full_name_hash = int(hashlib.sha1(full_name.encode('UTF-8')).hexdigest(), 16) % 10005

        mother_name_hash = int(hashlib.sha1(mother_full_name.encode('UTF-8')).hexdigest(), 16) % 10000
        if len(str(mother_name_hash)) < 4:
            mother_name_hash = int(hashlib.sha1(mother_full_name.encode('UTF-8')).hexdigest(), 16) % 10001
        if len(str(mother_name_hash)) < 4:
            mother_name_hash = int(hashlib.sha1(mother_full_name.encode('UTF-8')).hexdigest(), 16) % 10002
        if len(str(mother_name_hash)) < 4:
            mother_name_hash = int(hashlib.sha1(mother_full_name.encode('UTF-8')).hexdigest(), 16) % 10005

        if mother_name_char_count < 10 and not len(str(mother_name_hash)) > 4:
            mother_name_char_count = "0"+str(mother_name_char_count)

        if mother_name_char_count < 10 and len(str(mother_name_hash)) == 4:
            mother_name_char_count = "0"+str(mother_name_char_count)

        if full_name_char_count < 10 and not len(str(full_name_hash)) > 4:
            full_name_char_count = "0"+str(full_name_char_count)

        if full_name_char_count < 10 and len(str(full_name_hash)) == 4:
            full_name_char_count = "0"+str(full_name_char_count)

        gender_first_char = gender[:1]

        return '{}{}{}{}{}'.format(
            str(full_name_char_count),
            str(mother_name_char_count),
            str(full_name_hash),
            str(mother_name_hash),
            gender_first_char,
        )
    except Exception as exp:
        return ''
