# Antigravity Workspace Guidelines: Tiered Model Escalation

This workspace uses a multi-tiered model delegation and escalation workflow to optimize token consumption and response latency.

- **Primary Session**: Operates with Gemini 3.8 Flash (High) as architect, reviewer, and orchestrator.
- **Triage**: Use the `classify_and_route_task` tool to decide delegation between `task-runner-low`, `task-runner-medium`, and `consultant-high`.
- **Uncertainty Fallback**: If a lower tier subagent shows hesitation or encounters unresolved errors, use `evaluate_task_uncertainty` and cascade to the next tier immediately.
- For full details, see [rules/tiered_escalation.md](./rules/tiered_escalation.md).
