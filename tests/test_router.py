#!/usr/bin/env python3
"""
Unit and integration tests for Antigravity Tiered Router MCP Server.
Verifies:
  1. Heuristic classification for Low, Medium, and High tiers.
  2. Uncertainty evaluation and automatic cascading triggers.
  3. High-tier consultation formatting.
  4. Full MCP JSON-RPC 2.0 protocol over stdio subprocess.
"""

import unittest
import sys
import os
import json
import subprocess

# Ensure server module is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
server_dir = os.path.join(current_dir, "..", "server")
sys.path.insert(0, server_dir)

from tiered_router_mcp import (
    heuristic_classifier,
    evaluate_uncertainty,
    format_consultation,
    handle_tool_call,
    TOOLS
)


class TestTieredRouterLogic(unittest.TestCase):

    def test_classify_low_tier(self):
        prompts = [
            "listar arquivos do diretório src",
            "grep por 'PORT' no arquivo config.ts",
            "verifique a sintaxe deste pequeno arquivo",
            "veja se tem algum typo no comentário do README"
        ]
        for p in prompts:
            result = heuristic_classifier(p)
            self.assertEqual(result["tier"], "low", f"Failed for prompt: {p}")
            self.assertEqual(result["suggested_subagent"], "task-runner-low")
            self.assertIn("85", result["estimated_token_savings"])

    def test_classify_medium_tier(self):
        prompts = [
            "implementar autenticação JWT no controller de usuários",
            "adicionar testes unitários para a classe PaymentService",
            "corrigir bug de cálculo de desconto no checkout",
            "criar nova rota POST /api/products com validação de payload"
        ]
        for p in prompts:
            result = heuristic_classifier(p)
            self.assertEqual(result["tier"], "medium", f"Failed for prompt: {p}")
            self.assertEqual(result["suggested_subagent"], "task-runner-medium")

    def test_classify_high_tier(self):
        prompts = [
            "reestruturar arquitetura do sistema distribuído e auditar segurança contra race conditions",
            "system design e redesign completo de persistência com benchmark de arquitetura",
            "auditoria de segurança de concorrência com migração de banco e breaking changes"
        ]
        for p in prompts:
            result = heuristic_classifier(p)
            self.assertEqual(result["tier"], "high", f"Failed for prompt: {p}")
            self.assertEqual(result["suggested_subagent"], "consultant-high")

    def test_uncertainty_clean_output(self):
        clean_output = (
            "Análise concluída com sucesso. O arquivo foi localizado em src/utils.ts "
            "e a função calculateTotal foi verificada. Não foram encontrados erros."
        )
        res = evaluate_uncertainty(clean_output, current_tier="low")
        self.assertFalse(res["should_escalate"])
        self.assertIsNone(res["escalate_to"])
        self.assertGreater(res["confidence_score"], 0.8)

    def test_uncertainty_low_to_medium_escalation(self):
        doubt_output = (
            "Analisei o arquivo mas não tenho certeza sobre a dependência externa. "
            "Além disso, ocorreu um erro: SyntaxError: Unexpected token."
        )
        res = evaluate_uncertainty(doubt_output, current_tier="low")
        self.assertTrue(res["should_escalate"])
        self.assertEqual(res["escalate_to"], "medium")
        self.assertIn("task-runner-medium", res["action"])

    def test_uncertainty_medium_to_high_escalation(self):
        failing_output = (
            "Tentei aplicar a correção no controller, mas o teste falhou com Traceback: "
            "Failed with code 1. Não consegui resolver o conflito de tipos."
        )
        res = evaluate_uncertainty(failing_output, current_tier="medium")
        self.assertTrue(res["should_escalate"])
        self.assertEqual(res["escalate_to"], "high")
        self.assertIn("consultant-high", res["action"])

    def test_format_high_consultation(self):
        task = "Migrar autenticação para sessões stateless"
        findings = "Descobrimos que 4 microsserviços dependem do token em memória"
        dilemma = "Devemos usar Redis compartilhado ou assinar tokens JWT com rotação de chaves?"

        res = format_consultation(task, findings, dilemma)
        self.assertIn("CONSULTATION REQUEST: HIGH TIER ORACLE", res["formatted_prompt"])
        self.assertIn("Redis compartilhado", res["formatted_prompt"])
        self.assertEqual(res["target_agent"], "consultant-high")


class TestMCPProtocolStdio(unittest.TestCase):

    def setUp(self):
        server_path = os.path.join(server_dir, "tiered_router_mcp.py")
        self.proc = subprocess.Popen(
            [sys.executable, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

    def tearDown(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            self.proc.wait()
        if self.proc.stdin:
            self.proc.stdin.close()
        if self.proc.stdout:
            self.proc.stdout.close()
        if self.proc.stderr:
            self.proc.stderr.close()

    def send_and_receive(self, request_obj):
        line = json.dumps(request_obj) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        resp_line = self.proc.stdout.readline()
        return json.loads(resp_line)

    def test_mcp_handshake_and_tool_call(self):
        # 1. Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        }
        init_res = self.send_and_receive(init_req)
        self.assertEqual(init_res["id"], 1)
        self.assertEqual(init_res["result"]["serverInfo"]["name"], "antigravity-tiered-router")

        # 2. List tools
        tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        tools_res = self.send_and_receive(tools_req)
        self.assertEqual(tools_res["id"], 2)
        tool_names = [t["name"] for t in tools_res["result"]["tools"]]
        self.assertIn("classify_and_route_task", tool_names)
        self.assertIn("evaluate_task_uncertainty", tool_names)
        self.assertIn("format_high_consultation", tool_names)
        self.assertIn("get_tier_status", tool_names)

        # 3. Call tool classify_and_route_task
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "classify_and_route_task",
                "arguments": {"prompt": "listar os arquivos da pasta docs"}
            }
        }
        call_res = self.send_and_receive(call_req)
        self.assertEqual(call_res["id"], 3)
        content_text = call_res["result"]["content"][0]["text"]
        data = json.loads(content_text)
        self.assertEqual(data["tier"], "low")
        self.assertEqual(data["suggested_subagent"], "task-runner-low")


if __name__ == "__main__":
    unittest.main()
