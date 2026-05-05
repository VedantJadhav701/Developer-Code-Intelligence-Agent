<div align="center">

# 🧠 DevAgent

### The AI Coding Agent That Runs Entirely on Your Machine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-black.svg?logo=ollama)](https://ollama.ai)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![GitHub stars](https://img.shields.io/github/stars/VedantJadhav701/Developer-Code-Intelligence-Agent?style=social)](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent)

**Give your codebase an AI teammate that finds bugs, writes fixes, reviews its own code, and validates with tests — all offline, all local, zero API costs.**

[Quick Start](#-quick-start) •
[How It Works](#-how-it-works) •
[Demo](#-demo) •
[Roadmap](#-roadmap) •
[Contributing](#-contributing)

---

</div>

## 🤔 Why DevAgent?

Most AI coding tools are **chatbots** — they suggest code, you copy-paste, you pray it works.

DevAgent is different. It's a **real agent** that:

| | Chatbot | DevAgent |
|---|---|---|
| Searches your codebase | ❌ | ✅ ripgrep-powered |
| Modifies files | ❌ | ✅ Reads, writes, patches |
| Runs your tests | ❌ | ✅ pytest integration |
| Reviews its own output | ❌ | ✅ Self-critique loop |
| Retries on failure | ❌ | ✅ Up to N iterations |
| Works offline | ❌ | ✅ 100% local via Ollama |
| Costs money | 💸 | ✅ Free forever |

> **Philosophy:** Execution > Reasoning. Tools > Hallucination. Reliability > Intelligence.

---

## ✨ Features

🔁 **ReAct Loop** — Structured Thought → Action → Observation → Fix → Review → Test cycle

🔍 **Code Search** — Finds relevant code using ripgrep (with fallback for any OS)

📝 **Self-Review** — LLM critiques its own fixes, revises until approved

🧪 **Test-Driven** — Runs pytest after every fix, retries on failure

📊 **Full Audit Trail** — Every step logged to `logs/run.json` as structured JSON

🔒 **100% Offline** — Runs on Ollama with small models (2-4 GB)

⚡ **Low Resource** — Works on 4 GB VRAM / 12 GB RAM

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

# 3. Pull a model (if you don't have one)
ollama pull qwen2.5:3b

# 4. Run!
python main.py --task "Fix the divide-by-zero bug in calculator.py" --root ./demo_project
```

That's it. No API keys. No sign-ups. No cloud.

---

## 🎬 Demo

### The agent fixes a real bug in 2 iterations:

```
+==========================================================+
|             DEVELOPER CODE INTELLIGENCE AGENT            |
|                     Model: qwen2.5:3b                    |
+==========================================================+

  Task: Fix the divide-by-zero bug in calculator.py
  Project: ./demo_project
  Max iterations: 3

  ----------------------------------------
  ITERATION 1/3
  ----------------------------------------
  [TOOL] Executing: search_code(divide)
  >> Found: calculator.py:18:def divide(a, b)
  >> Tests: 1 failed, 4 passed

  ----------------------------------------
  ITERATION 2/3
  ----------------------------------------
  [TOOL] Executing: read_file(calculator.py)
  >> Generated fix: Added zero-division guard
  [REVIEW] #1: APPROVED
  >> Tests: 5 passed ✓

  [OK]  AGENT COMPLETED SUCCESSFULLY

  Status:     success
  Steps used: 2/3
```

### What the agent actually wrote:

```diff
 def divide(a, b):
-    # BUG: No zero-division guard
-    return a / b
+    if b == 0:
+        raise ValueError("Cannot divide by zero")
+    return a / b
```

---

## 🏗️ How It Works

```
                    ┌─────────────────────────┐
                    │      CLI (main.py)       │
                    │   --task --root --model  │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │    ReAct Agent Loop      │
                    │                         │
                    │  1. THOUGHT   (LLM)     │
                    │  2. ACTION    (Tool)     │
                    │  3. OBSERVATION          │
                    │  4. FIX       (LLM)     │
                    │  5. REVIEW    (LLM)     │
                    │  6. TEST     (pytest)    │
                    │                         │
                    │  if FAIL → retry        │
                    │  if PASS → done ✓       │
                    └──┬──────────────┬───────┘
                       │              │
              ┌────────▼──┐    ┌──────▼──────┐
              │   Tools   │    │   Ollama    │
              │           │    │  (Local)    │
              │ • search  │    │             │
              │ • read    │    │ qwen2.5:3b  │
              │ • write   │    │ phi3:mini   │
              │ • pytest  │    │ mistral:7b  │
              │ • flake8  │    │ gemma2:2b   │
              └───────────┘    └─────────────┘
```

### Shared State Object

The agent maintains a single state object passed through every step:

```python
state = {
    "task": "Fix the divide-by-zero bug",
    "current_file": "calculator.py",
    "attempts": 2,
    "status": "success",
    "test_output": "5 passed",
    "history": [...]
}
```

### Self-Review Loop

The agent doesn't just generate code — it **critiques its own output**:

```
LLM generates fix
    → LLM reviews: "APPROVED" or "REVISE: missing edge case"
        → If REVISE: regenerate with feedback
        → If APPROVED: write to file and test
```

---

## 📁 Project Structure

```
Developer-Code-Intelligence-Agent/
├── app/
│   ├── agent.py            # Core ReAct agent engine
│   ├── llm.py              # Ollama integration (Python SDK)
│   ├── reviewer.py         # Self-review module
│   └── state.py            # Shared state dataclass
├── tools/
│   ├── search.py           # Code search (ripgrep + fallbacks)
│   ├── file_ops.py         # Safe file read/write
│   └── test_runner.py      # pytest & flake8 runner
├── utils/
│   └── logger.py           # Structured JSON logger
├── demo_project/           # Sample buggy project for testing
│   ├── calculator.py       #   └─ has intentional divide-by-zero bug
│   └── test_calculator.py  #   └─ 5 tests (1 fails until fixed)
├── main.py                 # CLI entry point
├── requirements.txt
├── CONTRIBUTING.md
├── CHANGELOG.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
└── README.md
```

---

## 💻 Usage

### Basic

```bash
python main.py --task "Fix the failing test" --root ./my_project
```

### All Options

| Flag | Default | Description |
|---|---|---|
| `--task`, `-t` | *(required)* | The coding task for the agent |
| `--root`, `-r` | `.` | Project root directory |
| `--max-steps`, `-m` | `3` | Max ReAct iterations |
| `--model` | `qwen2.5:3b` | Any Ollama model |

### Examples

```bash
# Fix a specific bug
python main.py -t "Fix the TypeError in user_service.py" -r ./backend

# Add error handling
python main.py -t "Add input validation to the create_user function" -r ./api

# Make tests pass
python main.py -t "Make all tests in test_auth.py pass" -r ./project

# Use a different model
python main.py -t "Refactor the database module" -r ./app --model mistral:7b
```

---

## 📊 Structured Logs

Every run produces a complete audit trail at `logs/run.json`:

```json
[
  {
    "timestamp": "2026-05-06T00:08:33Z",
    "step": 1,
    "thought": "Need to find the divide function and check for zero handling",
    "action": "search_code: divide",
    "observation": "calculator.py:18:def divide(a, b): ...",
    "review": "",
    "test_result": "1 failed, 4 passed",
    "status": "fail"
  },
  {
    "timestamp": "2026-05-06T00:08:43Z",
    "step": 2,
    "thought": "Reading calculator.py to generate fix",
    "action": "read_file: calculator.py",
    "observation": "File content loaded",
    "review": "APPROVED",
    "test_result": "5 passed",
    "status": "success"
  }
]
```

---

## 🔧 Supported Models

Any Ollama model works. Tested and recommended:

| Model | Size | Speed | Quality | Best For |
|---|---|---|---|---|
| `qwen2.5:3b` | 1.9 GB | ⚡ Fast | ★★★☆ | **Default — best balance** |
| `qwen3:4b` | 2.5 GB | ⚡ Fast | ★★★★ | Better code understanding |
| `gemma2:2b` | 1.6 GB | ⚡⚡ | ★★☆☆ | Ultra-low resource |
| `phi3:mini` | 2.2 GB | ⚡ Fast | ★★★☆ | Good reasoning |
| `llama3.2:3b` | 2.0 GB | ⚡ Fast | ★★★☆ | General purpose |
| `mistral:7b` | 4.4 GB | 🐢 | ★★★★★ | Best quality (needs 8GB+) |
| `qwen2.5:latest` | 4.7 GB | 🐢 | ★★★★★ | Best quality (needs 8GB+) |

---

## 🗺️ Roadmap

We're building DevAgent in the open. Here's what's coming:

- [x] Core ReAct agent loop
- [x] Self-review module
- [x] Tool system (search, read, write, test, lint)
- [x] Structured JSON logging
- [x] CLI interface
- [ ] **Multi-file support** — Agent works across multiple files
- [ ] **Git integration** — `git diff`, `git stash`, auto-commit
- [ ] **RAG / Embeddings** — Codebase-aware context retrieval
- [ ] **Language support** — JavaScript, TypeScript, Go, Rust
- [ ] **Plugin system** — Custom tools via YAML/Python
- [ ] **Watch mode** — Auto-fix on test failure (`--watch`)
- [ ] **VS Code extension** — Run agent from your editor
- [ ] **Conversation memory** — Learn from past runs
- [ ] **Multi-agent** — Planner + Coder + Reviewer agents

Want to work on any of these? Check [CONTRIBUTING.md](CONTRIBUTING.md)!

---

## 🤝 Contributing

We welcome contributions of all kinds! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

```bash
# Fork → Clone → Branch → Code → Test → PR
git checkout -b feature/your-feature
# ... make changes ...
python -m pytest demo_project/ -v
git commit -m "feat: your feature"
git push origin feature/your-feature
```

**Good first issues** are tagged and waiting for you:
[Browse good first issues →](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/labels/good%20first%20issue)

---

## 📜 License

MIT — use it however you want. See [LICENSE](LICENSE).

---

## ⭐ Star History

If DevAgent helps you, please give it a star! It helps others discover the project.

[![Star History Chart](https://api.star-history.com/svg?repos=VedantJadhav701/Developer-Code-Intelligence-Agent&type=Date)](https://star-history.com/#VedantJadhav701/Developer-Code-Intelligence-Agent&Date)

---

<div align="center">

**Built with 🧠 by [Vedant Jadhav](https://github.com/VedantJadhav701)**

*If you find this useful, consider giving it a ⭐ — it means a lot!*

</div>
