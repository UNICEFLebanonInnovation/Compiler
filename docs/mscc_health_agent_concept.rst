MSCC Health Support AI Agent
============================

Overview
--------
The Makani Strategic Child Care (MSCC) programme now features an AI-enabled
health support agent that helps frontline staff identify children who require
additional health, psychosocial, or nutrition follow-up. The concept builds on
three pillars: consolidating MSCC registration data, summarising the meaning of
recorded services, and orchestrating an OpenAI analysis that delivers
actionable, question-driven insights.

Problem statement
-----------------
MSCC teams manage large caseloads of children registered in the core package of
services. Staff need a rapid way to understand which children show concerning
attendance gaps, unresolved required services, or red flags captured in PSS and
health records. Manual review of each child profile is time-consuming and can
hide patterns around wellbeing or nutrition risks. The health support agent
addresses this by scoring children, translating structured responses into
interpretable signals, and inviting the AI model to explain the most urgent
follow-up actions.

Data foundation
---------------
* **Eligibility filter** – Only active registrations in the Core Package are
  considered, and each child must have at least one PSS assessment plus a
  health or nutrition service or referral. This keeps the analysis focused on
  children with enough contextual information for AI review.【F:student_registration/mscc/views.py†L558-L670】
* **Attendance and services** – Attendance history, pending required services,
  and completion counts are aggregated per child to show recent absenteeism
  trends and outstanding support obligations.【F:student_registration/mscc/views.py†L600-L670】
* **PSS, health, and referral meaning** – The most recent records are parsed to
  extract labelled responses, wellbeing flags, alerts, and a composite life
  quality score that highlight issues such as malnutrition screenings, missed
  vaccinations, or psychosocial stressors.【F:student_registration/mscc/views.py†L422-L536】

Analytical capabilities
-----------------------
* **Risk scoring** – Attendance gaps, age, pending services, and wellbeing
  alerts combine into a risk score that prioritises children in the AI request
  and the user interface.【F:student_registration/mscc/views.py†L499-L536】
* **Sentiment and life quality** – Attendance, PSS, health, and referral
  signals are synthesised into a qualitative life quality assessment, including
  the strongest positive and negative indicators surfaced to staff.【F:student_registration/mscc/views.py†L422-L536】
* **Focus-aware insights** – Staff can ask domain-specific questions (for
  example, “Which children show concerning nutrition trends?”). Keywords in the
  question infer focus topics that instruct the OpenAI model to restrict its
  analysis to relevant programme dimensions and enrich nutrition prompts with
  domain guidance.【F:student_registration/mscc/ai_agent.py†L41-L146】【F:student_registration/mscc/views.py†L560-L700】

AI workflow
-----------
1. The dashboard calls the ``HealthSupportAgentView`` endpoint with optional
   registration IDs, limit, and staff question. The view normalises inputs,
   filters registrations, and assembles a structured payload per child that
   includes attendance summaries, service metrics, wellbeing flags, focus
   topics, and life quality sentiment.【F:student_registration/mscc/views.py†L539-L700】
2. ``HealthSupportAgent`` packages the payload into an OpenAI Chat Completions
   prompt, injecting any inferred focus topics to tighten the model’s scope and
   ensure nutrition-only questions stay on-topic.【F:student_registration/mscc/ai_agent.py†L59-L116】
3. The agent calls the configured OpenAI model (default ``gpt-4o-mini``) and
   returns markdown formatted sections – Priority Cases, Watch List, and Key
   Programme Insights – which the UI renders for staff review.【F:student_registration/mscc/ai_agent.py†L33-L158】

User experience
---------------
* **Dashboard entry point** – A dedicated “Health Support Insights” link in the
  Makani navigation takes authenticated staff directly to the AI dashboard.
  【F:student_registration/templates/base.html†L138-L149】
* **Insight request form** – The ``health_agent.html`` template provides fields
  for registration IDs, focus question, and maximum children to review, as well
  as guidance about how the analysis works and the configured AI model.
  【F:student_registration/templates/mscc/health_agent.html†L24-L118】
* **Interactive results** – The accompanying JavaScript renders AI markdown,
  tabular child summaries, life quality sentiment badges, wellbeing insight
  lists, and metadata about each analysis request so staff can act immediately
  on the prioritised recommendations.【F:student_registration/static/js/mscc/health_agent.js†L211-L338】

Operational considerations
--------------------------
* **Configuration** – Environment variables (``OPENAI_API_KEY``,
  ``OPENAI_HEALTH_AGENT_MODEL``, ``OPENAI_API_BASE``, ``OPENAI_TIMEOUT``) are
  surfaced in ``config/settings/base.py`` so deployments can control API
  access, model selection, and request timeouts.【F:config/settings/base.py†L158-L163】
* **Error handling** – The view traps configuration and upstream API errors,
  returning clear messages in the JSON response while logging unexpected
  failures for support teams.【F:student_registration/mscc/views.py†L683-L699】
* **Extensibility** – The agent payload structure exposes derived metrics (risk
  score, wellbeing flags, sentiment signals, inferred focus topics), enabling
  future rule-based triage or integration with case management workflows.

Roadmap suggestions
-------------------
* **Model evaluation** – Pilot the experience with programme teams to validate
  prioritisation accuracy, refine weighting, and calibrate life quality
  thresholds before expanding coverage beyond Core Package registrations.
* **Feedback loop** – Capture staff actions and outcomes after reviewing AI
  recommendations to continuously improve scoring and prompt engineering.
* **Multilingual support** – Localise the dashboard prompts, AI outputs, and
  wellbeing descriptors to support Arabic- and English-speaking staff.
* **Offline summaries** – Generate scheduled reports for centres with limited
  connectivity, reusing the structured context without requiring manual
  dashboard interaction.
