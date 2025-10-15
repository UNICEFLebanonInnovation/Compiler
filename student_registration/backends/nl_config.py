# Natural-language config (safe to tweak without touching core code)

PHRASE_MAP = {
    "gender": ["child_gender_norm", "child_gender"],
    "sex": ["child_gender_norm", "child_gender"],
    "nationality": ["child_nationality_name"],
    "governorate": ["governorate"],
    "caza": ["caza"],
    "cadaster": ["cadaster"],
    "partner": ["partner_id"],
    "center type": ["center_type"],
    "cycle": ["cycle"],
    "round": ["round_id"],
    "status": ["education_status"],
    "program": ["education_program"],
    "age": ["age_band", "age_years"],
    # time shorthands
    "trend": ["month"],
    "monthly": ["month"],
    "yearly": ["year"],
}

METRIC_INTENT = [
    {"phrases": ["dropout rate", "rate of dropout"], "metric": "mscc_dropout_rate"},
    {"phrases": ["outreach rate", "rate of outreach"], "metric": "mscc_outreach_yes_rate"},
    {"phrases": ["lp rate", "learning passport rate"], "metric": "mscc_digital_lp_rate"},
    {"phrases": ["akelius rate"], "metric": "mscc_digital_akelius_rate"},
    {"phrases": ["education status"], "metric": "mscc_education_status_breakdown"},
    {"phrases": ["program"], "metric": "mscc_program_breakdown"},
    {"phrases": ["age pyramid", "age gender"], "metric": "mscc_age_gender_yearly"},
    # default last
    {"phrases": ["registration", "registrations", "enrol", "enroll"], "metric": "mscc_registrations_total"},
]
