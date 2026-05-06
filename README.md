<div align="center">

# 🧠 DevAgent

### A Lightweight Local Open-Source Miniature of Claude Code CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg?logo=ollama)](https://ollama.ai)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/VedantJadhav701/Developer-Code-Intelligence-Agent?style=social)](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent)

**A production-grade local coding agent that finds bugs, writes patches, reviews its own code, and validates with tests — all offline, all local, zero API costs.**

[Quick Start](#-quick-start) •
[Architecture](#-architecture) •
[Benchmarks](#-benchmarks) •
[Roadmap](#-roadmap) •
[Contributing](#-contributing)

---

</div>

## 🤔 Why DevAgent?

Most AI coding tools are **chatbots** — they suggest code, you copy-paste, you pray.

DevAgent is a **real agent** with a retrieval-first, tool-grounded architecture:

| | Chatbot | DevAgent |
|---|---|---|
| Searches your codebase | ❌ | ✅ ripgrep + semantic search |
| Retrieves relevant code | ❌ | ✅ FAISS embeddings |
| Plans before coding | ❌ | ✅ Planner layer |
| Generates patches | ❌ | ✅ Unified diffs |
| Reviews its own output | ❌ | ✅ Self-critique loop |
| Runs your tests | ❌ | ✅ pytest integration |
| Retries on failure | ❌ | ✅ Up to N iterations |
| Works in sandbox | ❌ | ✅ Isolated workspace |
| Works offline | ❌ | ✅ 100% local via Ollama |
| Costs money | 💸 | ✅ Free forever |

> **Philosophy:** Execution > Reasoning. Tools > Hallucination. Retrieval > Huge Context. Reliability > Intelligence.

---

## ✨ Features

🔁 **ReAct Loop** — Thought → Action → Observation → Fix → Review → Test cycle

🧠 **Planner** — LLM generates an action plan before coding

🔍 **Semantic Search** — FAISS + sentence-transformers code retrieval

🔎 **Code Search** — ripgrep-powered with cross-platform fallback

📝 **Self-Review** — LLM critiques its own fixes, revises until approved

🩹 **Patch Engine** — Line-level unified diffs instead of full file rewrites

🧪 **Test-Driven** — Runs pytest after every fix, retries on failure

🏖️ **Sandbox Mode** — Agent works in an isolated copy, applies changes only on success

📊 **Benchmarks** — 5 built-in benchmark suites with automated evaluation

📈 **Metrics** — Latency, token estimates, retries, and performance tracking

📋 **Full Audit Trail** — Every step logged to `logs/run.json`

🔒 **100% Offline** — Runs on Ollama with small models (2-4 GB)

⚡ **Low Resource** — Works on RTX 3050 (4 GB VRAM) / 16 GB RAM

---

## 🚀 Quick Start

### Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [Ollama](https://ollama.ai) installed and running

### Install (30 seconds)

```bash
# 1. Clone
git clone https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent.git
cd Developer-Code-Intelligence-Agent

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pull the model
ollama pull qwen2.5-coder:3b

# 4. Run!
python main.py --task "Fix the divide-by-zero bug in calculator.py" --root ./demo_project
```

No API keys. No sign-ups. No cloud.

### Optional: Enable Semantic Search

```bash
pip install faiss-cpu sentence-transformers
```

Without these, DevAgent falls back to keyword search — still fully functional.

---

## 🎬 Demo

```
 ____              _                    _
|  _ \  _____   __/ \   __ _  ___ _ __ | |_
| | | |/ _ \ \ / / _ \ / _` |/ _ \ '_ \| __|
| |_| |  __/\ V / ___ \ (_| |  __/ | | | |_
|____/ \___| \_/_/   \_\__, |\___|_| |_|\__|
                       |___/

+==========================================================+
|        DEVELOPER CODE INTELLIGENCE AGENT                 |
|        Model: qwen2.5-coder:3b                          |
|        Sandbox: OFF                                      |
+==========================================================+

  [PLAN] LIKELY_FILES: calculator.py
  1. search_code: divide
  2. read_file: calculator.py
  3. run_tests

  ----------------------------------------
  ITERATION 1/5
  ----------------------------------------
  [TOOL] Executing: search_code(divide)
  >> Found: calculator.py:10:def divide(a, b)
  [REVIEW] #1: APPROVED
  >> Tests: 5 passed ✓

  [OK]  AGENT COMPLETED SUCCESSFULLY

  Status:     success
  Steps used: 1/5
  Patches:    1
  Time:       8.2s
```

---

## 🏗️ Architecture

```
                    ┌─────────────────────────────┐
                    │       CLI (main.py)          │
                    │  --task --root --model       │
                    │  --sandbox --benchmark       │
                    │  --auto-commit --auto-push   │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │     Planner Layer            │
                    │  Identifies files + strategy │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │  Retrieval Layer (Memory)    │
                    │  FAISS + Sentence-Transformers│
                    │  Chunk → Embed → Top-K       │
                    └──────────┬──────────────────┘
                               │
                    ┌──────────▼──────────────────┐
                    │     ReAct Agent Loop         │
                    │                              │
                    │  1. THOUGHT   (LLM)          │
                    │  2. ACTION    (Tool)          │
                    │  3. OBSERVATION               │
                    │  4. FIX       (LLM)          │
                    │  5. REVIEW    (LLM)          │
                    │  6. PATCH     (Diff Engine)   │
                    │  7. TEST      (pytest)        │
                    │                              │
                    │  if FAIL → retry              │
                    │  if PASS → done ✓            │
                    └──┬──────────────┬───────────┘
                       │              │
              ┌────────▼──┐    ┌──────▼──────┐
              │   Tools   │    │   Ollama    │
              │           │    │  (Local)    │
              │ • search  │    │             │
              │ • semantic│    │ qwen2.5-    │
              │ • read    │    │  coder:3b   │
              │ • patch   │    │ phi3:mini   │
              │ • pytest  │    │ mistral:7b  │
              │ • flake8  │    │             │
              │ • git_diff│    └─────────────┘
              │ • sandbox │
              └───────────┘
```

### 9-Layer Architecture

| Layer | Module | Purpose |
|---|---|---|
| 1. CLI | `main.py` | Argument parsing, mode selection, banner |
| 2. Planner | `app/planner.py` | Task interpretation, file identification |
| 3. Retrieval | `app/memory.py` | FAISS index, semantic chunking, Top-K search |
| 4. Tools | `tools/*` | 8 real tools: search, semantic_search, read, write, test, lint, git, sandbox |
| 5. Agent | `app/agent.py` | ReAct orchestration loop |
| 6. Review | `app/reviewer.py` | Self-critique with APPROVED/REVISE |
| 7. Validation | `tools/test_runner.py` | pytest + flake8 execution feedback |
| 8. Logging | `utils/logger.py` | Structured JSON audit trail |
| 9. Safety | `app/sandbox.py` | Isolated workspace, path validation |

---

## 📁 Project Structure

```
Developer-Code-Intelligence-Agent/
├── app/
│   ├── agent.py            # Core ReAct agent engine
│   ├── planner.py          # Task planning layer
│   ├── reviewer.py         # Self-review module
│   ├── llm.py              # Ollama integration
│   ├── memory.py           # FAISS retrieval + working memory
│   ├── patcher.py          # Unified diff patch engine
│   ├── sandbox.py          # Sandbox workspace manager
│   └── state.py            # Shared state dataclass
├── tools/
│   ├── search.py           # Code search (ripgrep + fallbacks)
│   ├── semantic_search.py  # FAISS semantic search
│   ├── file_ops.py         # Safe file read/write
│   ├── test_runner.py      # pytest runner
│   ├── linter.py           # flake8 linter
│   ├── git_tools.py        # Git diff/commit/push
│   └── benchmark_runner.py # Benchmark evaluation
├── utils/
│   ├── logger.py           # Structured JSON logger
│   ├── config.py           # Centralized configuration
│   └── metrics.py          # Performance metrics
├── benchmarks/
│   ├── divide_by_zero/     # Benchmark: zero division guard
│   ├── missing_validation/ # Benchmark: input validation
│   ├── syntax_error/       # Benchmark: syntax fix
│   ├── import_bug/         # Benchmark: wrong import
│   └── edge_case/          # Benchmark: empty list handling
├── demo_project/           # Sample buggy project
├── docs/
│   └── USER_GUIDE.md       # Full usage guide
├── main.py                 # CLI entry point
├── devagent.py             # Global CLI wrapper
├── devagent.bat            # Windows global shortcut
├── requirements.txt
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## 💻 CLI Reference

```bash
python main.py --task "TASK" --root ./project [OPTIONS]
```

| Flag | Default | Description |
|---|---|---|
| `--task`, `-t` | *(required)* | The coding task for the agent |
| `--root`, `-r` | `.` | Project root directory |
| `--model` | `qwen2.5-coder:3b` | Any Ollama model |
| `--max-steps`, `-m` | `5` | Max ReAct iterations |
| `--benchmark` | off | Run benchmark suite |
| `--sandbox` | off | Run in isolated sandbox |
| `--auto-commit` | off | Git commit on success |
| `--auto-push` | off | Git push after commit |
| `--verbose`, `-v` | off | Verbose output |

### Examples

```bash
# Fix a specific bug
python main.py -t "Fix the TypeError in user_service.py" -r ./backend

# Run in sandbox mode (safe — doesn't touch real files until success)
python main.py -t "Fix divide-by-zero bug" -r ./project --sandbox

# Auto-commit changes on success
python main.py -t "Add input validation" -r ./api --auto-commit

# Use a stronger model
python main.py -t "Refactor auth middleware" -r ./server --model mistral:7b

# Run benchmarks
python main.py --benchmark

# More retries for complex tasks
python main.py -t "Make all tests pass" -r ./project --max-steps 10
```

> 📖 **[Full User Guide →](docs/USER_GUIDE.md)**

---

## 📊 Benchmarks

DevAgent includes 5 built-in benchmarks to evaluate agent performance:

| Benchmark | Bug Type | Difficulty |
|---|---|---|
| `divide_by_zero` | Missing guard clause | Easy |
| `missing_validation` | No input validation | Medium |
| `syntax_error` | Broken syntax | Medium |
| `import_bug` | Wrong module name | Easy |
| `edge_case` | Empty list crash | Medium |

Run benchmarks:

```bash
python main.py --benchmark
python main.py --benchmark --model phi3:mini
```

---

## 🔧 Supported Models

| Model | Size | Speed | Quality | Best For |
|---|---|---|---|---|
| `qwen2.5-coder:3b` | 1.9 GB | ⚡ Fast | ★★★★ | **Default — best for code** |
| `qwen2.5:3b` | 1.9 GB | ⚡ Fast | ★★★☆ | General fallback |
| `phi3:mini` | 2.2 GB | ⚡ Fast | ★★★☆ | Good reasoning |
| `qwen3:4b` | 2.5 GB | ⚡ Fast | ★★★★ | Better understanding |
| `gemma2:2b` | 1.6 GB | ⚡⚡ | ★★☆☆ | Ultra-low resource |
| `mistral:7b` | 4.4 GB | 🐢 | ★★★★★ | Best quality (8GB+ RAM) |

---

## 🗺️ Roadmap

### ✅ Completed (v2.0)

- [x] Core ReAct agent loop
- [x] Self-review module
- [x] Tool system (9 tools)
- [x] Planner layer
- [x] Semantic retrieval (FAISS)
- [x] Patch engine (unified diffs)
- [x] Sandbox mode
- [x] Benchmark system (5 suites)
- [x] Metrics + structured logging
- [x] Git integration
- [x] CLI with all flags

### 🔜 Coming Next

- [ ] **Multi-file support** — Agent works across multiple files simultaneously
- [ ] **Language support** — JavaScript, TypeScript, Go, Rust
- [ ] **Plugin system** — Custom tools via YAML/Python
- [ ] **Watch mode** — Auto-fix on test failure (`--watch`)
- [ ] **VS Code extension** — Run agent from your editor
- [ ] **Conversation memory** — Learn from past runs
- [ ] **Multi-agent mode** — Planner + Coder + Reviewer + Evaluator agents

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

```bash
git checkout -b feature/your-feature
# ... make changes ...
python -m pytest demo_project/ -v
git commit -m "feat: your feature"
git push origin feature/your-feature
```

**Good first issues** are tagged and waiting:
[Browse good first issues →](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/labels/good%20first%20issue)

---

## 📜 License

MIT — use it however you want. See [LICENSE](LICENSE).

---

## ⭐ Star History

If DevAgent helps you, give it a star! It helps others discover the project.

[![Star History Chart](https://api.star-history.com/svg?repos=VedantJadhav701/Developer-Code-Intelligence-Agent&type=Date)](https://star-history.com/#VedantJadhav701/Developer-Code-Intelligence-Agent&Date)

---

<div align="center">

**Built with 🧠 by [Vedant Jadhav](https://github.com/VedantJadhav701)**

*A lightweight local open-source miniature of Claude Code CLI.*

</div>
