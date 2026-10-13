#!/usr/bin/env python3
"""
Antigravity Tiered Model Router MCP Server
------------------------------------------
A lightweight, zero-dependency MCP (Model Context Protocol) server running over stdio.
Implements the hybrid routing engine:
  1. Priority: Jared Palmer's Kev decision model via Ollama (localhost:11434/v1/systemone)
  2. Fallback: Deterministic local semantic heuristic engine (instant, offline, zero tokens)

Exposes tools:
  - classify_and_route_task: Classifies complexity (Low/Medium/High) and suggests tier.
  - evaluate_task_uncertainty: Analyzes subagent execution for doubt, failure, or incomplete work.
  - format_high_consultation: Structures consultation prompts for the High tier consultant.
  - get_tier_status: Reports health of Ollama, Kev model, and routing statistics.
"""

import sys
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, Tuple

OLLAMA_HOST = "http://127.0.0.1:11434"
KEV_MODEL_NAME = "kev"
CONNECT_TIMEOUT_SEC = 1.0


def log(msg: str) -> None:
    """Log to stderr to avoid corrupting stdio JSON-RPC output."""
    sys.stderr.write(f"[TieredRouter] {msg}\n")
    sys.stderr.flush()


def check_ollama_kev_available(host: str = OLLAMA_HOST) -> Tuple[bool, bool]:
    """Check if Ollama is running and if the Kev model is pulled."""
    try:
        req = urllib.request.Request(f"{host}/api/tags", headers={"User-Agent": "AntigravityRouter/1.0"})
        with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT_SEC) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name", "").split(":")[0] for m in data.get("models", [])]
                has_kev = KEV_MODEL_NAME in models or any("kev" in m for m in models)
                return True, has_kev
    except Exception:
        pass
    return False, False


def query_kev_systemone(prompt: str, host: str = OLLAMA_HOST) -> Optional[Dict[str, Any]]:
    """Query Kev via the /v1/systemone non-autoregressive decision API."""
    url = f"{host}/v1/systemone"
    payload = {
        "model": KEV_MODEL_NAME,
        "state": prompt[:4000],
        "questions": {
            "tier": {
                "type": "choice",
                "instructions": "Classify the task into the most cost-effective execution tier: low, medium, or high.",
                "criteria": {
                    "low": "Simple, read-only, localized, log inspection, file search, or minor script check.",
                    "medium": "Standard programming, creating endpoints, business logic, unit tests, bug fixing.",
                    "high": "Complex architecture, multi-repository migration, security overhaul, ambiguous planning."
                }
            }
        }
    }

    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "AntigravityRouter/1.0"}
        )
        with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT_SEC * 2) as resp:
            if resp.status == 200:
                result = json.loads(resp.read().decode("utf-8"))
                answers = result.get("answers", {})
                tier_ans = answers.get("tier", {})
                tier = tier_ans.get("choice", "medium").lower()
                confidence = float(tier_ans.get("confidence", 0.90))
                probs = tier_ans.get("probabilities", {})

                if tier not in ["low", "medium", "high"]:
                    tier = "medium"

                reasons = {
                    "low": f"Kev native decision model classified simple/read-only scope (P(low)={probs.get('low', 0):.2f}).",
                    "medium": f"Kev native decision model classified standard coding/feature development (P(medium)={probs.get('medium', 0):.2f}).",
                    "high": f"Kev native decision model identified high architectural complexity/risk (P(high)={probs.get('high', 0):.2f})."
                }

                return {
                    "tier": tier,
                    "confidence": round(confidence, 2),
                    "engine_used": "kev_systemone",
                    "probabilities": probs,
                    "reason": reasons.get(tier, f"Kev native decision model chose {tier}."),
                    "suggested_subagent": f"task-runner-{tier}" if tier != "high" else "consultant-high",
                    "estimated_token_savings": "80-90% vs High" if tier == "low" else ("40-60% vs High" if tier == "medium" else "Baseline (Full Capability)")
                }
    except Exception as e:
        log(f"Kev /v1/systemone skipped: {e}. Trying fallback...")

    # Dual-fallback: Query local Kev model via Ollama's standard /api/generate endpoint with JSON schema
    try:
        gen_url = f"{host}/api/generate"
        gen_payload = {
            "model": KEV_MODEL_NAME,
            "prompt": prompt[:2000],
            "stream": False,
            "format": "json"
        }
        body = json.dumps(gen_payload).encode("utf-8")
        req = urllib.request.Request(
            gen_url,
            data=body,
            headers={"Content-Type": "application/json", "User-Agent": "AntigravityRouter/1.0"}
        )
        with urllib.request.urlopen(req, timeout=CONNECT_TIMEOUT_SEC * 3) as resp:
            if resp.status == 200:
                gen_data = json.loads(resp.read().decode("utf-8"))
                raw_resp = gen_data.get("response", "{}")
                parsed = json.loads(raw_resp)
                answers = parsed.get("answers", parsed)

                is_simple = answers.get("is_simple_task", False)
                if isinstance(is_simple, dict):
                    is_simple = is_simple.get("noul", False)

                is_arch = answers.get("is_architectural_or_high_risk", False)
                if isinstance(is_arch, dict):
                    is_arch = is_arch.get("noul", False)

                if is_arch:
                    tier = "high"
                    reason = "Kev decision model identified high architectural complexity."
                elif is_simple:
                    tier = "low"
                    reason = "Kev decision model identified simple, quick, or read-only task scope."
                else:
                    tier = "medium"
                    reason = "Kev decision model classified standard implementation task."

                return {
                    "tier": tier,
                    "confidence": 0.90,
                    "engine_used": "local_kev_model",
                    "reason": reason,
                    "suggested_subagent": f"task-runner-{tier}" if tier != "high" else "consultant-high",
                    "estimated_token_savings": "80-90% vs High" if tier == "low" else ("40-60% vs High" if tier == "medium" else "Baseline (Full Capability)")
                }
    except Exception as e2:
        log(f"Local Kev query skipped: {e2}")

    return None


def heuristic_classifier(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Deterministic, offline local heuristic classifier.
    Fast, reliable, zero-latency, zero token consumption.
    """
    text = prompt.lower()
    word_count = len(prompt.split())

    # Check for file path patterns (e.g., architecture.md, security.txt) to prevent keyword collision
    file_path_pattern = r"[\w./\\-]+\.(?:md|ts|tsx|js|jsx|json|py|html|css|yml|yaml|toml|sql)\b"
    file_paths_found = re.findall(file_path_pattern, text)
    sanitized_text = text
    for fp in file_paths_found:
        sanitized_text = sanitized_text.replace(fp, "filepath_token")

    # High complexity / architecture signals
    high_keywords = [
        r"\barquitetura\b", r"\barchitecture\b", r"\bredesign\b", r"\breestruturar\b",
        r"\breestruture\b", r"\brefatoração completa\b", r"\bsystem design\b",
        r"\bsegurança\b", r"\bsecurity audit\b", r"\bvulnerability\b", r"\bvulnerabilidade\b",
        r"\bconcorrência\b", r"\bdeadlock\b", r"\brace condition\b", r"\bdistributed\b",
        r"\bdistribuído\b", r"\bbenchmark de arquitetura\b", r"\bestratégia\b", r"\bstrategy\b",
        r"\bconsultor\b", r"\bconsultant\b", r"\bcomplex debugging\b", r"\bmigração de banco\b",
        r"\bbreaking change\b", r"\bbreaking changes\b"
    ]

    # Medium implementation signals (active coding verbs and inflections)
    medium_keywords = [
        r"\bimplementar\b", r"\bimplemente\b", r"\bimplement\b", r"\bcriar\b", r"\bcrie\b",
        r"\bcria\b", r"\bcreate\b", r"\bdesenvolver\b", r"\bdesenvolva\b", r"\bdevelop\b",
        r"\bendpoint\b", r"\bcontroller\b", r"\bservice\b", r"\btestes\b", r"\btests\b",
        r"\brefatorar\b", r"\brefatore\b", r"\brefactor\b", r"\bcorrigir bug\b", r"\bfix bug\b",
        r"\badicionar\b", r"\badicione\b", r"\bmigrar\b", r"\bmigre\b", r"\bconstruir\b",
        r"\bconstrua\b", r"\bwebhook\b", r"\bcrud\b", r"\bworker\b", r"\bqueue\b", r"\bfila\b"
    ]

    # Multi-file or wide-scope signals (overrides "pequeno ajuste")
    wide_scope_signals = [
        r"\btodos os\b", r"\btodas as\b", r"\bem todos\b", r"\bem todas\b",
        r"\b\d+\s+controllers\b", r"\b\d+\s+arquivos\b", r"\bvários arquivos\b",
        r"\bmúltiplos arquivos\b", r"\bno projeto inteiro\b", r"\bacross the project\b"
    ]

    # Low complexity / quick inspection signals
    low_keywords = [
        r"\blistar\b", r"\bliste\b", r"\blist\b", r"\bverifique\b", r"\bverificar\b",
        r"\bveja\b", r"\bview\b", r"\bler\b", r"\bleia\b", r"\bread\b", r"\bgrep\b",
        r"\bprocurar\b", r"\bprocure\b", r"\bsearch\b", r"\bonde está\b", r"\bwhere is\b",
        r"\bo que é\b", r"\bwhat is\b", r"\bformatar\b", r"\bformat\b", r"\blint\b",
        r"\bsyntax\b", r"\bsintaxe\b", r"\bpequeno ajuste\b", r"\btypo\b", r"\bcomente\b",
        r"\bdocstring\b", r"\brenomear variável\b", r"\bquick test\b", r"\bstatus\b",
        r"\bcomo rodar\b", r"\bmostrar arquivo\b", r"\bmostre o arquivo\b", r"\bimprimir\b",
        r"\bimprima\b"
    ]

    # Explicit score evaluation using sanitized_text (prevents path collisions)
    high_hits = sum(1 for kw in high_keywords if re.search(kw, sanitized_text))
    med_hits = sum(1 for kw in medium_keywords if re.search(kw, text))
    low_hits = sum(1 for kw in low_keywords if re.search(kw, text))
    has_wide_scope = any(re.search(ws, text) for ws in wide_scope_signals)
    # If it's a read-only search/grep and no writing verbs exist, searching all files is still Low tier
    is_pure_search = (low_hits >= 1 and med_hits == 0 and any(re.search(s, text) for s in [r"\bgrep\b", r"\bprocurar\b", r"\bsearch\b", r"\blistar\b"]))
    if is_pure_search:
        has_wide_scope = False

    # Complexity estimation: Writing takes precedence over reading; wide scope escalates to Medium
    if high_hits >= 2 or (high_hits >= 1 and word_count > 40):
        tier = "high"
        confidence = min(0.95, 0.70 + (high_hits * 0.10))
        reason = f"Identified architectural or high-complexity markers ({high_hits} indicators)."
    elif has_wide_scope or (med_hits >= 1 and high_hits == 0) or word_count > 50:
        tier = "medium"
        confidence = min(0.95, 0.75 + (med_hits * 0.08))
        if has_wide_scope:
            reason = "Wide project scope / multi-file modification detected. Promoted to Medium tier executor."
        else:
            reason = f"Standard implementation/coding task ({med_hits} action indicators). Best handled by Medium executor."
    elif low_hits >= 1 and high_hits == 0 and med_hits == 0 and not has_wide_scope and word_count < 40:
        tier = "low"
        confidence = min(0.95, 0.75 + (low_hits * 0.08))
        reason = f"Identified simple/read-only/triage markers ({low_hits} indicators). Ideal for Low tier to save tokens."
    else:
        tier = "medium"
        confidence = 0.85
        reason = "Standard development task. Routed to Medium executor for reliable delivery."

    subagent_map = {
        "low": "task-runner-low",
        "medium": "task-runner-medium",
        "high": "consultant-high"
    }

    savings_map = {
        "low": "85-92% (Fastest response, minimal tokens)",
        "medium": "50-65% (Balanced speed and reasoning)",
        "high": "0% (Full reasoning depth, maximum context)"
    }

    return {
        "tier": tier,
        "confidence": round(confidence, 2),
        "engine_used": "local_heuristic",
        "reason": reason,
        "suggested_subagent": subagent_map[tier],
        "estimated_token_savings": savings_map[tier]
    }


def route_task(prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Intelligent Hybrid Ensemble:
    1. First evaluates deterministic semantic rules (instant 0.2ms).
    2. If the prompt contains clear high-confidence signals for Low or High, uses it directly.
    3. If the prompt is an implementation task or ambiguous, queries the local Kev decision model (Ollama).
    4. Falls back gracefully if Ollama is busy or offline.
    """
    heu_decision = heuristic_classifier(prompt, context)
    if heu_decision["tier"] in ("low", "high") and heu_decision["confidence"] >= 0.75:
        return heu_decision

    kev_result = query_kev_systemone(prompt)
    if kev_result:
        return kev_result

    return heu_decision


def evaluate_uncertainty(subagent_output: str, current_tier: str = "low") -> Dict[str, Any]:
    """
    Examines subagent output for uncertainty signals, errors, or incompleteness.
    Determines if execution must escalate to the next tier.
    """
    text = subagent_output.lower()

    uncertainty_patterns = [
        "não tenho certeza", "não consegui", "não tenho como saber", "talvez",
        "i am unsure", "i am not certain", "cannot determine", "uncertain",
        "failed to resolve", "could not fix", "unknown error",
        "não foi possível encontrar", "não sei", "hesito", "limitation",
        "error:", "exception:", "traceback", "stacktrace", "failed with code 1",
        "syntaxerror", "typeerror", "referenceerror", "test failed"
    ]

    incomplete_markers = [
        "todo:", "fixme:", "implement later", "a ser implementado",
        "placeholder", "[falta implementar]"
    ]

    matched_uncertainty = [p for p in uncertainty_patterns if p in text]
    matched_incomplete = [m for m in incomplete_markers if m in text]

    has_issue = len(matched_uncertainty) > 0 or len(matched_incomplete) > 0

    if has_issue:
        target_tier = "medium" if current_tier == "low" else "high"
        confidence = 0.90 if len(matched_uncertainty) >= 2 else 0.75
        return {
            "should_escalate": True,
            "current_tier": current_tier,
            "escalate_to": target_tier,
            "confidence_score": confidence,
            "reason": f"Detected uncertainty / failure indicators: {matched_uncertainty + matched_incomplete}. Automatically cascading to {target_tier.upper()}.",
            "action": f"Delegate to subagent task-runner-{target_tier}" if target_tier != "high" else "Delegate to consultant-high"
        }
    else:
        return {
            "should_escalate": False,
            "current_tier": current_tier,
            "escalate_to": None,
            "confidence_score": 0.92,
            "reason": "Subagent output demonstrates clear resolution without hesitation or critical errors.",
            "action": "Proceed with current workflow."
        }


def format_consultation(task: str, current_findings: str, dilemma: str) -> Dict[str, Any]:
    """Structures an inquiry for the High tier consultant."""
    template = (
        "### [CONSULTATION REQUEST: HIGH TIER ORACLE]\n\n"
        f"**Original Task:**\n{task}\n\n"
        f"**Findings / Progress by Lower Tier:**\n{current_findings}\n\n"
        f"**Architectural Dilemma / Uncertainty:**\n{dilemma}\n\n"
        "**Expected High Tier Response:**\n"
        "- Clear strategic decision or architectural guidance.\n"
        "- Root-cause analysis of the blockers.\n"
        "- Direct delegation instructions back to Medium or step-by-step resolution."
    )
    return {
        "formatted_prompt": template,
        "target_agent": "consultant-high",
        "target_model": "Gemini 3.8 Flash (High)"
    }


# ==============================================================================
# MCP Protocol (JSON-RPC 2.0 over stdio)
# ==============================================================================

TOOLS = [
    {
        "name": "classify_and_route_task",
        "description": "Analyzes a prompt or task description and determines the optimal model tier (Low, Medium, High) to maximize speed and minimize token costs.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The user prompt, subtask description, or command to triage."
                },
                "context": {
                    "type": "object",
                    "description": "Optional context information (file count, workspace state, etc.)."
                }
            },
            "required": ["prompt"]
        }
    },
    {
        "name": "evaluate_task_uncertainty",
        "description": "Evaluates a subagent's output or execution result for uncertainty, hesitation, or failure, triggering escalation (Low -> Medium -> High).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "subagent_output": {
                    "type": "string",
                    "description": "The raw output, answer, or error log generated by the subagent."
                },
                "current_tier": {
                    "type": "string",
                    "enum": ["low", "medium"],
                    "default": "low",
                    "description": "The tier that produced the output (low or medium)."
                }
            },
            "required": ["subagent_output"]
        }
    },
    {
        "name": "format_high_consultation",
        "description": "Formats a structured consultation inquiry for the High tier consultant when lower tiers encounter architectural doubt or complex blockers.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "string",
                    "description": "The original goal or task."
                },
                "current_findings": {
                    "type": "string",
                    "description": "What the lower tier already discovered or attempted."
                },
                "dilemma": {
                    "type": "string",
                    "description": "The specific doubt, question, or trade-off requiring High tier advice."
                }
            },
            "required": ["task", "current_findings", "dilemma"]
        }
    },
    {
        "name": "get_tier_status",
        "description": "Returns the status of local Ollama connectivity, Kev decision model availability, and active router configurations.",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    }
]


def handle_tool_call(name: str, args: Dict[str, Any]) -> Any:
    if name == "classify_and_route_task":
        prompt = args.get("prompt", "")
        ctx = args.get("context", {})
        return route_task(prompt, ctx)
    elif name == "evaluate_task_uncertainty":
        output = args.get("subagent_output", "")
        tier = args.get("current_tier", "low")
        return evaluate_uncertainty(output, tier)
    elif name == "format_high_consultation":
        task = args.get("task", "")
        findings = args.get("current_findings", "")
        dilemma = args.get("dilemma", "")
        return format_consultation(task, findings, dilemma)
    elif name == "get_tier_status":
        ollama_ok, kev_ok = check_ollama_kev_available()
        return {
            "ollama_running": ollama_ok,
            "kev_model_ready": kev_ok,
            "ollama_host": OLLAMA_HOST,
            "active_engine": "kev_systemone" if (ollama_ok and kev_ok) else "local_heuristic (resilient fallback)",
            "tier_hierarchy": {
                "low": "Gemini 3.8 Flash (Low) - Quick inspection, search, localized edits (85% token savings)",
                "medium": "Gemini 3.8 Flash (Medium) - Main feature executor, tests, refactoring",
                "high": "Gemini 3.8 Flash (High) - Strategic architect, complex edge cases, consultant"
            }
        }
    else:
        raise ValueError(f"Unknown tool: {name}")


def run_mcp_server():
    """Main loop handling JSON-RPC 2.0 messages from stdin."""
    log("Starting Antigravity Tiered Router MCP Server...")
    ollama_ok, kev_ok = check_ollama_kev_available()
    log(f"Ollama running: {ollama_ok}, Kev model ready: {kev_ok}")

    while True:
        line = sys.stdin.readline()
        if not line:
            break
        line = line.strip()
        if not line:
            continue

        try:
            req = json.loads(line)
        except json.JSONDecodeError as err:
            log(f"Invalid JSON: {err}")
            continue

        msg_id = req.get("id")
        method = req.get("method")
        params = req.get("params", {})

        if method == "initialize":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "antigravity-tiered-router",
                        "version": "1.0.0"
                    }
                }
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "notifications/initialized":
            # Client acknowledge, no response required
            pass

        elif method == "tools/list":
            res = {
                "jsonrpc": "2.0",
                "id": msg_id,
                "result": {"tools": TOOLS}
            }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            try:
                result_data = handle_tool_call(tool_name, tool_args)
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result_data, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                }
            except Exception as e:
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32603,
                        "message": str(e)
                    }
                }
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        elif method == "ping":
            res = {"jsonrpc": "2.0", "id": msg_id, "result": {}}
            sys.stdout.write(json.dumps(res) + "\n")
            sys.stdout.flush()

        else:
            if msg_id is not None:
                res = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                sys.stdout.write(json.dumps(res) + "\n")
                sys.stdout.flush()


if __name__ == "__main__":
    run_mcp_server()
