# Antigravity Tiered Router & Fallback System (Projeto Antiback)

[![Antigravity Plugin](https://img.shields.io/badge/Antigravity_IDE-Plugin_Ready-blue?style=flat-square&logo=google)](./plugin.json)
[![Models](https://img.shields.io/badge/Model_Support-Gemini_3.8_Flash_(Low/Med/High)-6f42c1?style=flat-square)](./rules/tiered_escalation.md)
[![Decision Engine](https://img.shields.io/badge/Decision_Engine-Kev_System_One_(0.8B)_+_Heuristic-059669?style=flat-square)](https://huggingface.co/ggml-org/Kev-0.8B-GGUF)
[![Token Savings](https://img.shields.io/badge/Token_Savings-Up_to_84%25-10b981?style=flat-square)](./benchmarks/deep_audit_results.json)
[![License: MIT](https://img.shields.io/badge/License-MIT-f59e0b?style=flat-square)](./LICENSE)
[![Architecture](https://img.shields.io/badge/Architecture-Modular_%26_Agnostic-8b5cf6?style=flat-square)](#-modular-architecture--custom-model-triads)

[English](#overview) | [Português](#visão-geral-pt-br)

---

## Overview

**Antigravity Tiered Router** is an intelligent task classification and model delegation proxy for the **Google Antigravity IDE**. It mitigates inference token consumption and response latency by dynamically routing development tasks across tiered LLM execution profiles (**Gemini 3.8 Flash Low, Medium, and High**) using a local, single-forward-pass decision model (**Kev-0.8B**) with a deterministic offline heuristic fallback.

Unlike traditional static proxies, it incorporates an **active runtime uncertainty fallback protocol (Antiback)**: if a delegated subagent encounters ambiguity, syntax errors, or missing dependencies during execution, it self-evaluates uncertainty and seamlessly escalates to the senior tier with full contextual preservation.

### Key Capabilities
- **Zero-Token Neural Triage**: Uses Jared Palmer's native **Kev-0.8B** decision model via Ollama's `/v1/systemone` endpoint. It produces calibrated choice probabilities in a single forward pass without autoregressive token generation.
- **Deterministic Heuristic Engine**: Sub-millisecond (0.2 ms) offline regex boundary parser acting as an instant failover if the local Ollama daemon is offline.
- **Active Antiback Protocol**: Continuous self-assessment tool (`evaluate_task_uncertainty`) preventing subagent loops and hallucinatory retries.
- **Measurable Token Economy**: Yields **26.7% to 84% token savings** across typical day-to-day software engineering tasks.
- **Telemetry Dashboard**: Built-in real-time monitoring interface served locally on port 8085.

---

## Architecture Lifecycle

```mermaid
flowchart TD
    Prompt(["Developer / IDE Task Prompt"]):::promptBox --> Router{"MCP Router<br/><b>classify_and_route_task</b>"}:::routerBox

    subgraph Decision_Engine ["Local Decision Engine (Zero Cloud Tokens)"]
        direction TB
        Kev["<b>Kev-0.8B Native</b><br/>/v1/systemone (Local GPU)<br/><i>Single forward pass</i>"]
        Heur["<b>Heuristic Engine</b><br/>Deterministic Fallback<br/><i>0.2ms latency</i>"]
    end

    Router <--> Decision_Engine

    Router -->|"Simple / Read-Only<br/>(84% token savings)"| Low["<b>Tier 1: Low</b><br/>Gemini 3.8 Flash Low<br/><i>task-runner-low</i>"]:::lowBox
    Router -->|"Standard Implementation<br/>(55% token savings)"| Med["<b>Tier 2: Medium</b><br/>Gemini 3.8 Flash Medium<br/><i>task-runner-medium</i>"]:::medBox
    Router -->|"Architecture / Security<br/>(Baseline)"| High["<b>Tier 3: High</b><br/>Gemini 3.8 Flash High<br/><i>consultant-high</i>"]:::highBox

    Low --> CheckLow{"Execution Check"}:::checkStatus
    Med --> CheckMed{"Execution Check"}:::checkStatus

    CheckLow -->|"Success"| Done(["Verified Completion"]):::doneBox
    CheckMed -->|"Success"| Done
    High --> Done

    CheckLow -->|"Error / Hesitation Detected<br/><b>evaluate_task_uncertainty</b>"| Med
    CheckMed -->|"Architectural Roadblock<br/><b>evaluate_task_uncertainty</b>"| High

    classDef promptBox fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#ffffff;
    classDef routerBox fill:#1e293b,stroke:#06b6d4,stroke-width:2px,color:#ffffff;
    classDef lowBox fill:#064e3b,stroke:#10b981,stroke-width:2px,color:#ffffff;
    classDef medBox fill:#1e1b4b,stroke:#818cf8,stroke-width:2px,color:#ffffff;
    classDef highBox fill:#4c0519,stroke:#f43f5e,stroke-width:2px,color:#ffffff;
    classDef checkStatus fill:#1f2937,stroke:#f59e0b,stroke-width:2px,color:#ffffff;
    classDef doneBox fill:#022c22,stroke:#22c55e,stroke-width:2px,color:#ffffff;
```

---

## The 3 Operational Tiers

| Tier | Assigned Model | Subagent Persona | Target Task Scope | Token Economy |
| :--- | :--- | :--- | :--- | :---: |
| **Tier 1 (Low)** | Gemini 3.8 Flash (Low) | `task-runner-low` | Read-only tasks, file search, grep, syntax checks, log inspection, documentation typos. | **~84% savings** |
| **Tier 2 (Medium)** | Gemini 3.8 Flash (Medium) | `task-runner-medium` | Feature development, writing endpoints, unit tests, bug fixes, localized refactoring. | **~55% savings** |
| **Tier 3 (High)** | Gemini 3.8 Flash (High) | `consultant-high` | System architecture, distributed consensus, security audits, database migrations. | Baseline (Full reasoning) |

---

## 🧩 Modular Architecture & Custom Model Triads

The router's core innovation is **semantic tier decoupling**: the decision engine (Kev-0.8B and the heuristic fallback) does **not** evaluate vendor-specific model names; it evaluates the **intrinsic complexity of the task** (code changes, blast radius, read vs. write, ambiguity).

Tasks are classified into three abstract capability bands:
- **Tier 1 (Low)**: Read-only, inspection, localized grep, single-line patches, syntax checks.
- **Tier 2 (Medium)**: Feature creation, endpoint development, standard bug fixing, unit tests.
- **Tier 3 (High)**: Architectural design, distributed systems, deep security audits, deadlocks.

This abstraction makes the architecture **100% provider-agnostic**. While the default distribution maps these tiers to **Gemini 3.8 Flash (Low / Med / High)**, you can configure any model triad in minutes:

### Example Triad Configurations

| Provider / Strategy | Tier 1 (Low Runner) | Tier 2 (Medium Executor) | Tier 3 (High Consultant) | Ideal For |
| :--- | :--- | :--- | :--- | :--- |
| **Default (Google)** | Gemini 3.8 Flash (Low) | Gemini 3.8 Flash (Medium) | Gemini 3.8 Flash (High) / Pro | Zero setup, out-of-the-box Antigravity IDE |
| **Anthropic Claude** | `claude-3-5-haiku-latest` | `claude-3-5-sonnet-latest` | `claude-3-opus-latest` | High-precision coding and refactoring |
| **OpenAI** | `gpt-4o-mini` | `gpt-4o` | `o1` or `o3-mini` | Deep reasoning and mathematical verification |
| **100% Local (Ollama)** | `qwen2.5-coder:1.5b` | `qwen2.5-coder:7b` | `deepseek-r1:14b` or `llama3.3:70b` | Air-gapped, zero cloud cost, 100% privacy |
| **Hybrid Zero-Cost** | Local Ollama (0 tokens) | Gemini 3.8 Flash (Low cost) | Claude 3.5 Sonnet / Gemini Pro | Maximum token optimization |

---

### How to Swap Models (Step-by-Step)

Swapping models requires **zero code changes in the router engine**:

#### 1. Update Subagent Definitions (`agents/*.md`)
Open the subagent markdown files in `agents/` and modify the `model:` property in the YAML frontmatter:

- **[`agents/task-runner-low.md`](./agents/task-runner-low.md)**:
  ```yaml
  model: claude-3-5-haiku-latest  # or gpt-4o-mini, qwen2.5-coder:1.5b
  ```
- **[`agents/task-runner-medium.md`](./agents/task-runner-medium.md)**:
  ```yaml
  model: claude-3-5-sonnet-latest # or gpt-4o, qwen2.5-coder:7b
  ```
- **[`agents/consultant-high.md`](./agents/consultant-high.md)**:
  ```yaml
  model: claude-3-opus-latest    # or o1, deepseek-r1:14b
  ```

#### 2. Update Governance Rule (`rules/tiered_escalation.md`)
Update the table in [`rules/tiered_escalation.md`](./rules/tiered_escalation.md) to reflect your chosen models so the primary orchestrator understands the capabilities assigned to each tier.

#### 3. (Optional) Custom Model Metadata in MCP Server (`server/tiered_router_mcp.py`)
To expose explicit model identifiers in the JSON-RPC response, you can map `recommended_model` in `classify_and_route_task`:
```python
model_mapping = {
    "low": "claude-3-5-haiku-latest",
    "medium": "claude-3-5-sonnet-latest",
    "high": "claude-3-opus-latest",
}
```

#### 4. (Optional) Update Dashboard Labels (`dashboard/app.js`)
Update the card titles and cost multiplier metrics in `dashboard/app.js` if you want the telemetry dashboard to reflect custom pricing per million tokens.

---

## State of the Art Comparison

| Project | Scope & Target | Decision Mechanism | Runtime Uncertainty Detection | Native IDE Plugin |
| :--- | :--- | :--- | :---: | :---: |
| **RouteLLM** (LMSYS) | Generic Web Chatbot (API Proxy) | Elo Preference / BERT | No | No (Python client only) |
| **FrugalGPT** (Stanford) | Theoretical Model Cascade | Linear scoring / cascade | No (Post-failure only) | No |
| **tierdecay** | Quota / Token Analytics | Historical log heuristics | No | Passive metric tracking |
| **jaredpalmer/kev** | Standalone Decision Model | LoRA + Pointer Head (Qwen base) | No (Inference only) | No |
| **Antigravity Tiered Router** | **Google Antigravity IDE** | **Kev-0.8B (Q8_0) + Heuristic Fallback** | **Yes (Active Antiback Protocol)** | **Full Plugin (MCP + Rules + Subagents)** |

---

## Benchmark & Audit Results

Consolidated from the 25-scenario deep audit test suite (`tests/deep_audit_tiered_router.py`):

| Metric | Result | Target Benchmark |
| :--- | :---: | :---: |
| **Initial Triage Accuracy** | **100.0%** (25/25) | > 95% |
| **Uncertainty Capture Rate (Recall)** | **100.0%** (4/4) | 100% |
| **False Escalation Rate** | **0.0%** (0 false positives) | < 5% |
| **Overall Token Reduction** | **-26.7%** (62,253 tokens saved) | -20% to -40% |
| **Routing Decision Overhead** | **0.23 ms** (Heuristic) / **32 ms** (Kev) | < 100 ms |
| **Cloud Tokens Consumed by Router** | **0 tokens** | 0 tokens |

---

## Quickstart

### Prerequisites
- Python 3.9+
- [Ollama](https://ollama.com/) (version 0.40.4-rc1 or newer for native decision model support)

### 1. Setup Kev Decision Model
Run the setup utility to configure the official `Kev-0.8B-Q8_0.gguf` checkpoint into Ollama:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_kev.ps1
```

### 2. Run Unit Tests
```bash
python -m unittest tests/test_router.py
```

### 3. Run Deep Audit Benchmark
```bash
python tests/deep_audit_tiered_router.py
```

### 4. Launch Telemetry Dashboard
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_dashboard.ps1
```
Open `http://localhost:8085` in your browser.

---

## Antigravity IDE Integration

### Option A: Global Plugin (Recommended)
Copy the repository into your global Antigravity customizations directory:
- **Windows:** `%USERPROFILE%\.gemini\config\plugins\projeto-antiback`
- **Linux / macOS:** `~/.gemini/config/plugins/projeto-antiback`

The IDE automatically registers the MCP tools and subagent escalation rules across all workspaces.

### Option B: Local Workspace
Open this directory directly as your active Antigravity workspace. The [`GEMINI.md`](./GEMINI.md) and [`mcp_config.json`](./mcp_config.json) manifests are recognized automatically.

---

## Visão Geral (PT-BR)

O **Antigravity Tiered Router (Projeto Antiback)** é uma arquitetura de roteamento de tarefas e contingência ativa para o **Google Antigravity IDE**. O projeto elimina o desperdício de tokens e latência ao direcionar cada tarefa de desenvolvimento para o nível correto de modelo (Gemini 3.8 Flash Low, Medium ou High).

### Destaques Técnicos:
1. **Triagem em 1 Passada com 0 Tokens**: Utiliza o modelo neural Kev-0.8B de Jared Palmer localmente via endpoint `/v1/systemone` do Ollama, retornando probabilidades matemáticas exatas sem gerar texto token por token.
2. **Motor Heurístico Determinístico**: Fallback instantâneo offline (0,2 ms) caso o daemon local esteja indisponível.
3. **Protocolo Antiback Ativo**: Se um subagente encontra uma exceção ou incerteza durante a execução, ele aciona a ferramenta `evaluate_task_uncertainty` e é promovido automaticamente ao modelo sênior com todo o contexto preservado.
4. **Economia Real Comprovada**: Até **84% de redução de tokens** em inspeções e **26,7% de economia líquida** no portfólio completo de desenvolvimento.

### 🧩 Suporte a Qualquer Família de Modelos (Arquitetura Modular)
O Kev-0.8B classifica tarefas por **complexidade intrínseca** (leitura vs. implementação vs. arquitetura) e não pelo nome comercial da API. Isso significa que você pode trocar a família padrão por qualquer fornecedor:
- **Anthropic Claude**: Haiku (Low) ➔ Sonnet (Med) ➔ Opus (High)
- **OpenAI**: GPT-4o-mini (Low) ➔ GPT-4o (Med) ➔ o1 / o3-mini (High)
- **100% Local (Ollama)**: Qwen 1.5B (Low) ➔ Qwen 7B (Med) ➔ DeepSeek-R1 / Llama 70B (High)
- **Híbrido Custo Zero**: Ollama Local (0 tokens) ➔ Gemini Flash (Med) ➔ Claude Opus (High)

Basta alterar a propriedade `model:` no cabeçalho YAML dos arquivos em `agents/` (`task-runner-low.md`, `task-runner-medium.md`, `consultant-high.md`). O roteador e o fallback funcionam imediatamente sem necessidade de retreinar o Kev!

---

## Repository Structure

```text
projeto_antiback/
├── .github/workflows/ci.yml       # Automated GitHub Actions test workflow
├── agents/                        # Antigravity subagent persona definitions
│   ├── task-runner-low.md         # Tier 1 runner (Gemini 3.8 Flash Low)
│   ├── task-runner-medium.md      # Tier 2 runner (Gemini 3.8 Flash Medium)
│   └── consultant-high.md         # Tier 3 consultant (Gemini 3.8 Flash High)
├── benchmarks/                    # Empirical benchmark suite and telemetry data
│   ├── benchmark_results.json     # Standard 10-task benchmark data
│   ├── deep_audit_results.json    # 25-scenario deep audit metrics
│   └── run_benchmark.py           # Benchmark execution runner
├── dashboard/                     # Dark-mode glassmorphic telemetry dashboard
│   ├── index.html                 # Dashboard UI
│   ├── styles.css                 # Clean CSS token design system
│   └── app.js                     # Live chart and interactive simulator logic
├── rules/                         # Operational rules for Antigravity IDE
│   └── tiered_escalation.md       # Core escalation and handover contract
├── scripts/                       # Turnkey automation utilities
│   ├── run_tests.ps1              # Test runner script
│   ├── setup_kev.ps1              # Ollama and Kev-0.8B automated setup
│   └── start_dashboard.ps1        # Local telemetry server launcher
├── server/                        # MCP JSON-RPC Server
│   ├── __init__.py                # Server package marker
│   └── tiered_router_mcp.py       # Core router engine and MCP tools
├── skills/tiered-router/          # Antigravity workflow skill instructions
│   └── SKILL.md                   # Operational procedures for IDE agents
├── tests/                         # Unit tests and deep stress validation
│   ├── test_router.py             # 8 unit tests for MCP protocol and triage
│   └── deep_audit_tiered_router.py # 25 adversarial and stress scenarios
├── CONTRIBUTING.md                # Open source contribution guidelines
├── GEMINI.md                      # Antigravity workspace instructions
├── LICENSE                        # MIT Open Source License
├── mcp_config.json                # MCP server configuration manifest
├── Modelfile                      # Ollama Modelfile for Kev-0.8B
├── plugin.json                    # Antigravity plugin manifest
├── pyproject.toml                 # Standard PEP 517/621 packaging metadata
├── README.md                      # Technical documentation
└── requirements.txt               # Development dependencies
```

---

## License

This project is licensed under the [MIT License](./LICENSE).
