# Phase 4b — GOAT configuration

GOAT means Generative Offensive Agent Tester. Copy the workspace `goat.py` to a named attack module and tailor `APPLICATION_CONFIG` and `APPLICATION_GUARDRAILS`. Preserve its implementation and conversation logging.

Fill these fields from the current assessment and `spikee.log`. This is an agent checklist, not a questionnaire to send to the user. Ask only missing facts that change the configuration, at most three at a time. Record unknown controls as unknown; do not claim they are absent.

| Area | Information to use |
|---|---|
| Output | Short identifier for `attacks/<identifier>-goat.py`; lowercase letters, digits or hyphens. |
| Application | Name, purpose, intended users, supported tasks/topics, known model and deployment context. |
| Objective | Agreed unwanted outcomes and sensitive capabilities/data. |
| Each input control | Type, what it blocks/redacts, response on activation, observed weaknesses or edge cases. |
| Each output control | Same fields, including how a blocked/redacted response reaches the user. |
| Other controls | Session limits, abuse detection, human review, or other known controls. |
| Technique preferences | User-selected techniques and exclusions; no requirement to choose each individually. |
| Additional evidence | Supplied system-message fragments, refusal phrases and architecture relevant to the test. |

Examples of input controls include prompt rules, keyword/regex filters, injection detectors, PII redaction, topic/intent/toxicity classifiers, rate limits and allowlists. Output controls can include content classifiers, PII scans, groundedness/hallucination checks and output filters. Use only those established for this application.

Technique examples include gradual escalation (knowledge ladder), authority/citation, emotional appeals, scope creep, hypothetical/fictional or historical/academic framing, personas, encoding, language switching and injection in controlled data/file contents. These are options to tailor GOAT, not permission to try them manually.

`APPLICATION_CONFIG` is a concise description of the application, users, tasks, sensitive capabilities, model/deployment when known, and agreed objective. `APPLICATION_GUARDRAILS` contains one object per known control:

```python
APPLICATION_GUARDRAILS = [
    {
        "type": "output PII filter",
        "location": "output",
        "description": "Observed behaviour of this control",
        "recommendations": "Strategies relevant to the agreed test",
    },
]
```

When no controls are known, use `None` for this setting and describe that uncertainty in `APPLICATION_CONFIG`; do not assert there are no controls. When confirmed absent, say so. The module then uses its standard mode rather than control-specific guidance.

Log confirmed facts, choices and the created file path without secrets or a questionnaire transcript. Return to [Phase 4](04-testing.md) for baseline, workload, authorization, tmux and results.
