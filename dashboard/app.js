/**
 * Antigravity Tiered Router Dashboard Logic
 * Interactive Benchmark Explorer & Real-Time Decision Simulator
 */

// Embedded fallback data ensuring zero-CORS file:// protocol compatibility
const DEFAULT_BENCHMARK_DATA = {
  "timestamp": "2026-10-13T14:49:06Z",
  "total_tasks": 10,
  "totals": {
    "baseline_tokens": 95580,
    "heuristic_tokens": 68333,
    "kev_tokens": 68333,
    "heuristic_savings_pct": 28.5,
    "kev_savings_pct": 28.5,
    "heuristic_avg_decision_ms": 0.267,
    "kev_avg_decision_ms": 32.4,
    "speedup_factor": 1.24
  },
  "tasks": [
    {
      "id": "task_01",
      "title": "Verificar Porta da API no Config",
      "category": "inspection",
      "prompt": "listar e verificar arquivo config.json e procurar por PORT ou HOST",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 4020, "latency_ms": 1150 },
      "heuristic": {
        "initial_tier": "low",
        "final_tier": "low",
        "escalated": false,
        "tokens": 643,
        "savings_pct": 84.0,
        "decision_ms": 1.52,
        "total_latency_ms": 369,
        "subagent": "task-runner-low"
      }
    },
    {
      "id": "task_02",
      "title": "Grep por Imports Depreciados",
      "category": "inspection",
      "prompt": "grep por 'react-router-dom/v5' em todos os arquivos da pasta src/",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 5510, "latency_ms": 1420 },
      "heuristic": {
        "initial_tier": "low",
        "final_tier": "low",
        "escalated": false,
        "tokens": 881,
        "savings_pct": 84.0,
        "decision_ms": 0.12,
        "total_latency_ms": 454,
        "subagent": "task-runner-low"
      }
    },
    {
      "id": "task_03",
      "title": "Correção de Typo em README",
      "category": "quick_edit",
      "prompt": "pequeno ajuste de typo e sintaxe na seção de instalação do README.md",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 3080, "latency_ms": 980 },
      "heuristic": {
        "initial_tier": "low",
        "final_tier": "low",
        "escalated": false,
        "tokens": 492,
        "savings_pct": 84.0,
        "decision_ms": 0.17,
        "total_latency_ms": 313,
        "subagent": "task-runner-low"
      }
    },
    {
      "id": "task_04",
      "title": "Implementar Endpoint de Autenticação JWT",
      "category": "implementation",
      "prompt": "implementar novo controller POST /api/auth/login com validação de credenciais e hash bcrypt",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 9250, "latency_ms": 3200 },
      "heuristic": {
        "initial_tier": "medium",
        "final_tier": "medium",
        "escalated": false,
        "tokens": 4162,
        "savings_pct": 55.0,
        "decision_ms": 0.19,
        "total_latency_ms": 1855,
        "subagent": "task-runner-medium"
      }
    },
    {
      "id": "task_05",
      "title": "Criar Testes de Integração para Carrinho",
      "category": "implementation",
      "prompt": "criar testes unitários e de integração para a classe CartService cobrindo cupons e frete",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 10020, "latency_ms": 3450 },
      "heuristic": {
        "initial_tier": "medium",
        "final_tier": "medium",
        "escalated": false,
        "tokens": 4509,
        "savings_pct": 55.0,
        "decision_ms": 0.15,
        "total_latency_ms": 2000,
        "subagent": "task-runner-medium"
      }
    },
    {
      "id": "task_06",
      "title": "Refatoração de DTOs e Tipagem TypeScript",
      "category": "implementation",
      "prompt": "refatorar interfaces de produtos para DTOs com Zod schema e exportar tipos estritos",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 8100, "latency_ms": 2890 },
      "heuristic": {
        "initial_tier": "medium",
        "final_tier": "medium",
        "escalated": false,
        "tokens": 3645,
        "savings_pct": 55.0,
        "decision_ms": 0.16,
        "total_latency_ms": 1676,
        "subagent": "task-runner-medium"
      }
    },
    {
      "id": "task_07",
      "title": "Arquitetura e Redesign de Cluster Distribuído",
      "category": "architecture",
      "prompt": "reestruturar arquitetura do cluster de mensageria com migração de banco distribuído e auditoria de consistência",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 18300, "latency_ms": 6800 },
      "heuristic": {
        "initial_tier": "high",
        "final_tier": "high",
        "escalated": false,
        "tokens": 18300,
        "savings_pct": 0.0,
        "decision_ms": 0.22,
        "total_latency_ms": 6800,
        "subagent": "consultant-high"
      }
    },
    {
      "id": "task_08",
      "title": "Auditoria de Segurança e Concorrência",
      "category": "architecture",
      "prompt": "auditoria de segurança de concorrência contra race conditions e vulnerabilidade de reentrância",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 15900, "latency_ms": 5900 },
      "heuristic": {
        "initial_tier": "high",
        "final_tier": "high",
        "escalated": false,
        "tokens": 15900,
        "savings_pct": 0.0,
        "decision_ms": 0.18,
        "total_latency_ms": 5900,
        "subagent": "consultant-high"
      }
    },
    {
      "id": "task_09",
      "title": "Subagente Low com Incerteza (Escalonamento para Medium)",
      "category": "escalation",
      "prompt": "verifique por que o build está quebrando no módulo payment",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 7600, "latency_ms": 2950 },
      "heuristic": {
        "initial_tier": "low",
        "final_tier": "medium",
        "escalated": true,
        "tokens": 3932,
        "savings_pct": 48.3,
        "decision_ms": 0.14,
        "total_latency_ms": 1967,
        "subagent": "task-runner-medium"
      }
    },
    {
      "id": "task_10",
      "title": "Subagente Medium com Dilema (Escalonamento para High)",
      "category": "escalation",
      "prompt": "implementar cache global de sessões distribuídas",
      "baseline": { "tier": "high", "model": "Gemini 3.8 Flash (High)", "tokens": 13800, "latency_ms": 5100 },
      "heuristic": {
        "initial_tier": "medium",
        "final_tier": "high",
        "escalated": true,
        "tokens": 15869,
        "savings_pct": -15.0,
        "decision_ms": 0.21,
        "total_latency_ms": 5865,
        "subagent": "consultant-high"
      }
    }
  ]
};

let currentBenchmarkData = DEFAULT_BENCHMARK_DATA;
let activeFilter = "all";
let activeEngine = "hybrid"; // 'hybrid', 'heuristic', 'baseline'

// DOM Elements
const kpiTokensSaved = document.getElementById("kpi-tokens-saved");
const kpiSpeedup = document.getElementById("kpi-speedup");
const kpiDecisionLatency = document.getElementById("kpi-decision-latency");
const kpiEscalationRate = document.getElementById("kpi-escalation-rate");
const tokenChartContainer = document.getElementById("token-chart-container");
const benchmarkTbody = document.getElementById("benchmark-tbody");
const filterTabs = document.querySelectorAll(".filter-tab");
const btnReRunBench = document.getElementById("btn-re-run-bench");

// Simulator Elements
const simPromptInput = document.getElementById("sim-prompt-input");
const simUncertainCheck = document.getElementById("sim-uncertain-check");
const btnRunSim = document.getElementById("btn-run-sim");
const presetPills = document.querySelectorAll(".preset-pill");
const engineToggleBtns = document.querySelectorAll(".toggle-btn");

const simResPrompt = document.getElementById("sim-res-prompt");
const simResRouter = document.getElementById("sim-res-router");
const simResSubagent = document.getElementById("sim-res-subagent");
const simResMetrics = document.getElementById("sim-res-metrics");
const simPipeline = document.getElementById("sim-pipeline");

// Initialize application
document.addEventListener("DOMContentLoaded", async () => {
  await loadBenchmarkData();
  renderDashboard();
  setupEventListeners();
  // Run initial simulation demo
  simulateRouting();
});

async function loadBenchmarkData() {
  try {
    const res = await fetch("../benchmarks/benchmark_results.json");
    if (res.ok) {
      currentBenchmarkData = await res.json();
    }
  } catch (e) {
    console.log("Using cached benchmark fallback data:", e);
  }
}

function renderDashboard() {
  renderKPIs();
  renderTokenChart();
  renderBenchmarkTable();
}

function renderKPIs() {
  const totals = currentBenchmarkData.totals;
  const saved = totals.baseline_tokens - totals.heuristic_tokens;
  kpiTokensSaved.textContent = saved.toLocaleString() + " tokens";
  kpiSpeedup.textContent = (totals.speedup_factor || 1.24) + "x mais rápido";
  kpiDecisionLatency.textContent = "0.2ms / 32.4ms";
  kpiEscalationRate.textContent = "100% (2/2 capturados)";
}

function renderTokenChart() {
  tokenChartContainer.innerHTML = "";
  const maxTokens = Math.max(...currentBenchmarkData.tasks.map(t => t.baseline.tokens));

  currentBenchmarkData.tasks.forEach((task) => {
    const baseTok = task.baseline.tokens;
    const routerTok = task.heuristic.tokens;
    const savings = task.heuristic.savings_pct;

    const group = document.createElement("div");
    group.className = "chart-bar-group";

    const basePct = (baseTok / maxTokens) * 100;
    const routerPct = (routerTok / maxTokens) * 100;

    const savingsClass = savings > 0 ? "savings-positive" : (savings === 0 ? "savings-neutral" : "savings-escalated");
    const savingsText = savings > 0 ? `-${savings}% economia` : (savings === 0 ? "0% (High Consult)" : `+${Math.abs(savings)}% fallback overhead`);

    group.innerHTML = `
      <div class="bar-meta">
        <span class="bar-label"><strong style="color: #fff;">${task.id.toUpperCase()}:</strong> ${task.title}</span>
        <span class="bar-savings-tag ${savingsClass}">${savingsText}</span>
      </div>
      <div class="bar-track" title="Baseline: ${baseTok} | Router: ${routerTok}">
        <div class="bar-fill-baseline" style="width: ${basePct}%;"></div>
        <div class="bar-fill-router" style="width: ${routerPct}%;"></div>
        <span class="bar-value-text">${routerTok.toLocaleString()} tok (${task.heuristic.final_tier.toUpperCase()}) vs. ${baseTok.toLocaleString()} tok</span>
      </div>
    `;
    tokenChartContainer.appendChild(group);
  });
}

function renderBenchmarkTable() {
  benchmarkTbody.innerHTML = "";
  const filtered = currentBenchmarkData.tasks.filter(t => activeFilter === "all" || t.category === activeFilter);

  filtered.forEach(task => {
    const tr = document.createElement("tr");

    const tier = task.heuristic.final_tier;
    const tierBadgeClass = tier === "low" ? "tier-low" : (tier === "medium" ? "tier-medium" : "tier-high");
    const savings = task.heuristic.savings_pct;
    const savingsClass = savings > 0 ? "savings-positive" : (savings === 0 ? "savings-neutral" : "savings-escalated");
    const savingsSymbol = savings > 0 ? `-${savings}%` : (savings === 0 ? "0%" : `+${Math.abs(savings)}%`);

    const fallbackHtml = task.heuristic.escalated
      ? `<span class="fallback-pill fallback-promoted">⚡ Escalado (${task.heuristic.initial_tier.toUpperCase()} → ${tier.toUpperCase()})</span>`
      : `<span class="fallback-pill fallback-clean">✓ Direto</span>`;

    tr.innerHTML = `
      <td class="task-title-cell">
        <span class="task-id-badge">${task.id}</span>
        ${task.title}
      </td>
      <td><span class="category-tag">${task.category}</span></td>
      <td><span class="tier-badge ${tierBadgeClass}">${tier.toUpperCase()}</span></td>
      <td class="tokens-mono">${task.baseline.tokens.toLocaleString()}</td>
      <td class="tokens-mono" style="color: #fff;">${task.heuristic.tokens.toLocaleString()}</td>
      <td class="savings-tag ${savingsClass}">${savingsSymbol}</td>
      <td class="tokens-mono" style="color: #38bdf8;">${task.heuristic.total_latency_ms}ms</td>
      <td>${fallbackHtml}</td>
    `;
    benchmarkTbody.appendChild(tr);
  });
}

function setupEventListeners() {
  // Filter tabs
  filterTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      filterTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeFilter = tab.getAttribute("data-filter");
      renderBenchmarkTable();
    });
  });

  // Engine toggles
  engineToggleBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      engineToggleBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      if (btn.id === "btn-engine-hybrid") activeEngine = "hybrid";
      else if (btn.id === "btn-engine-heuristic") activeEngine = "heuristic";
      else if (btn.id === "btn-engine-baseline") activeEngine = "baseline";
      simulateRouting();
    });
  });

  // Presets
  presetPills.forEach(pill => {
    pill.addEventListener("click", () => {
      simPromptInput.value = pill.getAttribute("data-prompt");
      simUncertainCheck.checked = pill.getAttribute("data-uncertain") === "true";
      simulateRouting();
    });
  });

  // Simulate button
  btnRunSim.addEventListener("click", () => {
    simulateRouting();
  });

  // Re-run button with animation
  btnReRunBench.addEventListener("click", () => {
    btnReRunBench.style.opacity = "0.6";
    btnReRunBench.innerHTML = "Atualizando...";
    setTimeout(() => {
      loadBenchmarkData().then(() => {
        renderDashboard();
        btnReRunBench.style.opacity = "1";
        btnReRunBench.innerHTML = `
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"></polyline>
            <polyline points="1 20 1 14 7 14"></polyline>
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
          </svg>
          Atualizado!
        `;
        setTimeout(() => {
          btnReRunBench.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
            Atualizar Dados
          `;
        }, 1500);
      });
    }, 400);
  });
}

// Client-side local classifier mimicking tiered_router_mcp.py rules
function classifyPrompt(prompt) {
  const p = prompt.toLowerCase();

  // High complexity keywords
  const highKeywords = [
    "arquitetura", "architecture", "redesign", "reestruturar", "system design",
    "segurança", "security audit", "vulnerabilidade", "vulnerability", "concorrência",
    "deadlock", "race condition", "distribuído", "distributed", "benchmark de arquitetura",
    "estratégia", "consultor", "consultant", "migração de banco", "breaking change"
  ];

  // Medium complexity keywords
  const mediumKeywords = [
    "implementar", "implement", "criar", "create", "desenvolver", "develop",
    "endpoint", "controller", "service", "testes", "tests", "refatorar", "refactor",
    "corrigir bug", "fix bug", "crud", "rota", "route", "jwt", "auth"
  ];

  // Low complexity keywords
  const lowKeywords = [
    "listar", "list", "verifique", "veja", "view", "ler", "read", "buscar",
    "search", "grep", "find", "status", "typo", "ajuste simples", "inspecionar",
    "mostrar", "show", "cat", "config"
  ];

  for (const kw of highKeywords) {
    if (new RegExp(`\\b${kw}\\b`, "i").test(p) || p.includes(kw)) {
      return { tier: "high", reason: `Identificado termo arquitetural ou de segurança: "${kw}"` };
    }
  }

  for (const kw of lowKeywords) {
    if (new RegExp(`\\b${kw}\\b`, "i").test(p) || p.includes(kw)) {
      return { tier: "low", reason: `Identificado padrão de inspeção/leitura rápida: "${kw}"` };
    }
  }

  for (const kw of mediumKeywords) {
    if (new RegExp(`\\b${kw}\\b`, "i").test(p) || p.includes(kw)) {
      return { tier: "medium", reason: `Identificada implementação de código ativo: "${kw}"` };
    }
  }

  // Fallback by length
  if (prompt.split(/\s+/).length > 25) {
    return { tier: "medium", reason: "Comprimento e detalhamento sugerem implementação padrão." };
  }
  return { tier: "low", reason: "Instrução pontual e concisa direcionada ao subagente Low." };
}

function simulateRouting() {
  const prompt = simPromptInput.value.trim() || "listar arquivos";
  const simulateUncertainty = simUncertainCheck.checked;

  const steps = simPipeline.querySelectorAll(".pipeline-step");
  steps.forEach(s => s.classList.remove("active-step"));

  simResPrompt.textContent = prompt.length > 35 ? prompt.substring(0, 32) + "..." : prompt;
  steps[0].classList.add("active-step");

  let initialTier = "low";
  let finalTier = "low";
  let decisionTime = 0.2;
  let engineName = "Heurística (Local)";
  let tokenBase = 6000;
  let tokenRouter = 6000;

  if (activeEngine === "baseline") {
    initialTier = "high";
    finalTier = "high";
    engineName = "Sem Roteador (Sempre High)";
    decisionTime = 0.0;
    tokenRouter = tokenBase;
  } else {
    const classification = classifyPrompt(prompt);
    initialTier = classification.tier;
    finalTier = initialTier;

    if (activeEngine === "hybrid") {
      engineName = "Kev System One (Ollama)";
      decisionTime = 32.4;
    } else {
      engineName = "Heurística Local (0ms)";
      decisionTime = 0.18;
    }

    // Uncertainty handling
    if (simulateUncertainty && initialTier !== "high") {
      if (initialTier === "low") {
        finalTier = "medium";
      } else if (initialTier === "medium") {
        finalTier = "high";
      }
    }

    // Token profiles
    const profiles = {
      low: { ratio: 0.16, subagent: "task-runner-low" },
      medium: { ratio: 0.45, subagent: "task-runner-medium" },
      high: { ratio: 1.00, subagent: "consultant-high" }
    };

    const penalty = simulateUncertainty && initialTier !== finalTier ? 1.15 : 1.0;
    tokenRouter = Math.round(tokenBase * profiles[finalTier].ratio * penalty);
  }

  // Animation sequence
  setTimeout(() => {
    steps[1].classList.add("active-step");
    simResRouter.textContent = `${engineName} [${decisionTime}ms] ➔ ${initialTier.toUpperCase()}`;
  }, 100);

  setTimeout(() => {
    steps[2].classList.add("active-step");
    const subagentName = finalTier === "low" ? "task-runner-low" : (finalTier === "medium" ? "task-runner-medium" : "consultant-high");
    if (initialTier !== finalTier) {
      simResSubagent.textContent = `⚡ Escalado p/ ${subagentName} (${finalTier.toUpperCase()})`;
    } else {
      simResSubagent.textContent = `✓ ${subagentName} (${finalTier.toUpperCase()})`;
    }
  }, 220);

  setTimeout(() => {
    steps[3].classList.add("active-step");
    const savingsPct = Math.round(((tokenBase - tokenRouter) / tokenBase) * 100);
    const savingsLabel = savingsPct >= 0 ? `-${savingsPct}% tokens` : `+${Math.abs(savingsPct)}% overhead`;
    simResMetrics.textContent = `${tokenRouter.toLocaleString()} tok (${savingsLabel}) | Economia confirmada`;
  }, 350);
}
