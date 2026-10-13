# Guia de Contribuição / Contributing Guide

Bem-vindo ao **Projeto Antiback / Antigravity Tiered Router**! 🎉
Agradecemos pelo interesse em contribuir para o sistema de roteamento em camadas, economia de tokens e telemetria para o Antigravity IDE.

---

## 🛠️ Como Contribuir

### 1. Clonar e Configurar o Repositório
```bash
git clone https://github.com/stankfoo/antigravity-tiered-router.git
cd projeto_antiback
```

### 2. Executar os Testes
Antes de abrir qualquer Pull Request, certifique-se de que todos os testes unitários e de integração MCP estão passando:
```bash
python tests/test_router.py
```
Todos os 8 testes devem passar com `OK`.

### 3. Rodar o Benchmark
Valide se as métricas de token e latência permanecem consistentes:
```bash
python benchmarks/run_benchmark.py
```

### 4. Adicionar Novas Palavras-Chave ou Regras de Triagem
Se desejar aprimorar o classificador heurístico, edite a função `heuristic_classifier` em `server/tiered_router_mcp.py` e adicione os respectivos casos de teste em `tests/test_router.py`.

---

## 📋 Convenções de Commit

Recomendamos seguir o padrão [Conventional Commits](https://www.conventionalcommits.org/):
- `feat: adiciona nova regra para detecção de migração de banco`
- `fix: corrige threshold de incerteza para subagente medium`
- `docs: atualiza guia de instalação do Ollama Kev`
- `perf: otimiza regex de fronteira para tempo < 0.1ms`

---

## 🛡️ Segurança e Relato de Bugs
Se encontrar alguma vulnerabilidade de segurança ou falha de execução, abra uma issue descrevendo o passo a passo para reprodução.
