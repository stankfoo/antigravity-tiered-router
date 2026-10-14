# Tiered Model Escalation & Fallback Rule

This rule governs how tasks and subagent operations are delegated across model tiers in Antigravity to maximize speed, save tokens, and ensure rock-solid reliability.

## 1. The 3-Tier Hierarchy

| Tier | Model Designation | Recommended Subagent | Role & Best Used For |
| :--- | :--- | :--- | :--- |
| **Tier 1 (Low)** | Gemini 3.8 Flash (Low) | `task-runner-low` | File lookups, simple greps, syntax check, status, minor 1-line edits. Saves ~85% tokens. |
| **Tier 2 (Medium)** | Gemini 3.8 Flash (Medium) | `task-runner-medium` | Core development, multi-file edits, writing tests, debugging, feature implementation. |
| **Tier 3 (High)** | Gemini 3.8 Flash (High) / Gemini 4 Argon | `consultant-high` | System architecture, complex debugging, security audits, fallback when lower tiers fail. |

---

## 2. Delegation & Routing Protocol

Whenever processing a user request or decomposing a project into subtasks:

1. **Triage First**:
   - Use the `classify_and_route_task` tool to determine the recommended tier.
   - If the task is classified as **Low**, delegate it immediately to `task-runner-low`.
   - If the task is classified as **Medium**, delegate it to `task-runner-medium`.
   - If the task is classified as **High**, keep execution in the High primary session or consult `consultant-high`.

2. **Uncertainty Evaluation & Automatic Escalation**:
   - After a lower tier subagent completes its step, inspect the response using `evaluate_task_uncertainty`.
   - **Low → Medium Escalation**: If `task-runner-low` outputs `[ESCALATE_TO: MEDIUM]`, expresses doubt ("não tenho certeza", "não consegui encontrar"), or hits an error, immediately escalate the task to `task-runner-medium` with all accumulated context.
   - **Medium → High Consultation**: If `task-runner-medium` outputs `[CONSULT_HIGH]`, faces an architectural dilemma, or fails a fix after 2 test attempts, format an inquiry using `format_high_consultation` and consult `consultant-high`.

3. **Context Preservation**:
   - During escalation, never restart from scratch. Pass the partial findings, investigated files, error traces, and the exact reason for escalation to the higher tier.
