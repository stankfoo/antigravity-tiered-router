---
name: tiered-router
description: Global tiered model router and uncertainty fallback workflow. Guides the agent to triage tasks across Gemini 3.8 Flash (Low, Medium, High) / Gemini 4 Argon, and use classify_and_route_task and evaluate_task_uncertainty tools for token optimization.
---

# Tiered Router & Model Escalation Guide

This skill provides operational procedures for using the **Antigravity Tiered Router** to save tokens, accelerate response times, and handle uncertainty safely.

## Core Rules

1. **Triage First**:
   - Before executing tasks, call `classify_and_route_task` to determine the target tier:
     - `Low`: Inspections, file reads, greps, typos, syntax checks (saves ~84% tokens).
     - `Medium`: Routine implementation, writing tests, bug fixes, refactoring (saves ~55% tokens).
     - `High`: Architecture redesign, distributed consensus, security audits, deadlocks (full reasoning capacity with Gemini 3.8 Flash High / Gemini 4 Argon).
2. **Evaluate Non-Capacity (Uncertainty Fallback)**:
   - After a lower-tier subagent finishes its turn, run `evaluate_task_uncertainty`.
   - If hesitation, errors (`TypeError`, `SyntaxError`, `failed with code 1`), or unresolved doubts are detected:
     - Immediately cascade from `Low -> Medium` or `Medium -> High`.
     - Pass accumulated context and error logs to avoid restarting from scratch.
3. **High Consultation**:
   - When facing architectural trade-offs, call `format_high_consultation` to formulate a concise query for the High tier consultant.
