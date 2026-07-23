# Outreach Draft Template

Every draft Sales Director produces follows this structure. Drafts are
always personalised from the real record in
`06-CRM/company-intelligence.json`, never sent from a generic script.

---

**Company:** {{COMPANY_NAME}}
**Contact / channel:** {{RECRUITER_OR_CONTACT}}
**Relationship temperature:** {{RELATIONSHIP_TEMPERATURE}}
**Last touch:** {{LAST_TOUCH_DATE}} via {{LAST_TOUCH_CHANNEL}}
**Why now:** {{REASON_THIS_IS_DUE}}

## Draft Message

{{OPENING_LINE_REFERENCING_LAST_INTERACTION}}

{{BODY_USING_TAILORED_POSITIONING}}

{{SPECIFIC_ASK_OR_NEXT_STEP}}

{{SIGN_OFF}}

---

## Drafting Rules

- The opening line must reference something real from
  `outreachHistory` or `previousApplications` — never a cold generic
  opener.
- The body must use the record's `tailoredPositioning` rather than a
  restated general pitch.
- Every draft ends with one specific, low-friction next step (a
  question, a suggested time, a specific document to share) — never a
  vague "let me know if you're interested."
- Draft, do not send. The founder reviews and sends every message.
- After sending, log the touch back to `outreachHistory` in
  `06-CRM/company-intelligence.json`.
