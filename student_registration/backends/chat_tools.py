# chat_tools.py
GET_METRIC_TOOL = {
  "type": "function",
  "function": {
    "name": "get_metric",
    "description": "Retrieve a metric with optional filters/breakdowns and time range.",
    "parameters": {
      "type": "object",
      "properties": {
        "metric_key": {
          "type": "string",
          "enum": [
            "mscc_registrations_total",
            "mscc_education_status_breakdown",
            "mscc_program_breakdown",
            "mscc_dropout_total",
            "mscc_dropout_rate",
            "mscc_outreach_total",
            "mscc_outreach_yes_rate",
            "mscc_digital_lp_users",
            "mscc_digital_akelius_users",
            "mscc_digital_lp_rate",
            "mscc_digital_akelius_rate",
            "mscc_attendance_total_attended",
            "mscc_attendance_total_absence",
            "mscc_attendance_registrations",
            "mscc_attendance_absence_rate",
            "mscc_age_gender_yearly",
            "mscc_registrations_gender_by_nationality"  # optional MV we added
          ]
        },
        "time_range": {
          "type": "object",
          "properties": {
            "start": {"type": "string", "format": "date"},
            "end":   {"type": "string", "format": "date"}
          },
          "required": ["start","end"]
        },
        "breakdown_by": {"type":"string"},
        "breakdowns": {
          "type": "array",
          "items": {
            "type":"string",
            "enum":[
              "month","year",
              "governorate","caza","cadaster",
              "child_gender","child_gender_norm",
              "child_nationality_name",
              "partner_id","center_type","cycle","round_id",
              "education_status","education_program",
              "age_band","age_years"
            ]
          }
        },
        "filters": {
          "type": "array",
          "items": {
            "type":"object",
            "properties": {
              "field": {"type":"string"},
              "op": {"type":"string","enum":["eq","in","neq","nin","gte","gt","lte","lt","contains"]},
              "value": {}
            },
            "required":["field","op","value"]
          }
        }
      },
      "required": ["metric_key","time_range"]
    }
  }
}
