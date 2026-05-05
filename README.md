# Developer Code Intelligence Agent

A production-grade **local** AI coding agent that autonomously finds bugs, fixes code, and validates via tests — powered entirely by [Ollama](https://ollama.ai) running offline on your machine.

> **Not a chatbot.** This is a real agent system with a ReAct loop, self-review, and tool execution.

---

## ✨ Features

| Feature | Description |
|---|---|
| **ReAct Loop** | Thought → Action → Observation → Fix → Review → Test |
| **Self-Review** | LLM critiques its own output; revises until approved |
| **Tool Execution** | `search_code`, `read_file`, `write_file`, `run_tests`, `lint_code` |
| **Retry Logic** | Up to N iterations (default 3) with test-driven feedback |
| **Structured Logging** | Every step logged to `logs/run.json` |
| **Fully Offline** | Runs on Ollama (phi3:mini) — no API keys, no internet |
| **Low VRAM** | Works on 4 GB GPU |

---

## 📁 Project Structure

```
Developer-Code-Intelligence-Agent/
├── app/
│   ├── agent.py          # Core ReAct agent engine
│   ├── llm.py            # Ollama integration layer
│   ├── reviewer.py       # Self-review module
│   └── state.py          # Shared state object
├── tools/
│   ├── search.py         # Code search (ripgrep / fallback)
│   ├── file_ops.py       # File read/write operations
│   └── test_runner.py    # pytest & flake8 runner
├── utils/
│   └── logger.py         # Structured JSON logger
├── demo_project/         # Sample buggy project for testing
│   ├── calculator.py
│   └── test_calculator.py
├── main.py               # CLI entry point
├── requirements.txt
└── README.md
```

---

## 🚀 Setup

### Prerequisites

1. **Ollama** installed and running:
   ```bash
   # Install from https://ollama.ai
   ollama pull phi3:mini
   ollama serve    # must be running
   ```

2. **Python 3.11+** with conda:
   ```bash
   conda activate thermo_agent
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **(Optional)** Install [ripgrep](https://github.com/BurntSushi/ripgrep) for faster code search:
   ```bash
   # Windows (scoop)
   scoop install ripgrep
   # or via choco
   choco install ripgrep
   ```

---

## 💻 Usage

### Basic Usage

```bash
python main.py --task "Fix the divide-by-zero bug in calculator.py"
```

### Full Options

```bash
python main.py \
  --task "Fix the failing test in test_calculator.py" \
  --root ./demo_project \
  --max-steps 3 \
  --model phi3:mini
```

| Flag | Default | Description |
|---|---|---|
| `--task`, `-t` | *(required)* | The coding task to complete |
| `--root`, `-r` | `.` | Project root directory |
| `--max-steps`, `-m` | `3` | Max ReAct iterations |
| `--model` | `phi3:mini` | Ollama model name |

---

## 🧪 Example Run

```bash
# Run the agent on the included demo project
python main.py --task "Fix the divide-by-zero bug so test_divide_by_zero passes" --root ./demo_project
```

### What Happens:

1. **Step 1 — THOUGHT:** Agent decides to search for the divide function
2. **Step 1 — ACTION:** `search_code("divide")` → finds `calculator.py`
3. **Step 1 — OBSERVATION:** Reads the file, sees no zero-guard
4. **Step 1 — FIX:** Generates a fix adding `if b == 0: raise ValueError`
5. **Step 1 — REVIEW:** LLM reviews → APPROVED
6. **Step 1 — TEST:** Runs pytest → all 5 tests pass ✅

### Output:

```
╔══════════════════════════════════════════════════════╗
║       DEVELOPER CODE INTELLIGENCE AGENT              ║
║       Model: phi3:mini                               ║
╚══════════════════════════════════════════════════════╝

  ──────────────────────────────
  ITERATION 1/3
  ──────────────────────────────
  🔧 Executing: search_code(divide)
  📝 Review #1: APPROVED
  ✅ AGENT COMPLETED SUCCESSFULLY

  FINAL SUMMARY
  ─────────────────────────────────
  Status:     success
  Steps used: 1/3
  Attempts:   1
  Last file:  demo_project/calculator.py
  Log file:   demo_project/logs/run.json
```

---

## 📋 Log Output

Every run produces a structured JSON log at `logs/run.json`:

```json
[
  {
    "timestamp": "2026-05-06T00:00:00+00:00",
    "step": 1,
    "thought": "Need to find the divide function and add zero-division guard",
    "action": "search_code: divide",
    "observation": "calculator.py:24: return a / b",
    "review": "APPROVED",
    "test_result": "5 passed",
    "status": "success"
  }
]
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│                  main.py                     │
│              (CLI Entry Point)               │
└─────────────┬───────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────┐
│              Agent (ReAct Loop)              │
│                                             │
│  ┌─────────┐   ┌──────────┐   ┌──────────┐ │
│  │ THOUGHT │──▶│  ACTION  │──▶│OBSERVATION│ │
│  └─────────┘   └──────────┘   └──────────┘ │
│       ▲                             │       │
│       │         ┌──────────┐        │       │
│       │         │   TEST   │◀───────┘       │
│       │         └──────────┘                │
│       │              │                      │
│       │    ┌─────────▼─────────┐            │
│       │    │   SELF-REVIEW     │            │
│       │    │ APPROVED / REVISE │            │
│       │    └───────────────────┘            │
│       │              │                      │
│       └──────────────┘ (retry if fail)      │
└─────────────────────────────────────────────┘
              │
     ┌────────┴────────┐
     ▼                 ▼
┌──────────┐    ┌──────────────┐
│  Tools   │    │   Ollama     │
│ rg/pytest│    │  phi3:mini   │
│ file I/O │    │  (local LLM) │
└──────────┘    └──────────────┘
```

---

## 🔧 Supported Models

Any Ollama model works. Recommended for 4 GB VRAM:

| Model | Size | Speed | Quality |
|---|---|---|---|
| `phi3:mini` | 2.2 GB | ⚡ Fast | ★★★☆ |
| `qwen2.5:3b` | 1.9 GB | ⚡ Fast | ★★★☆ |
| `gemma2:2b` | 1.6 GB | ⚡⚡ Fastest | ★★☆☆ |
| `qwen3:4b` | 2.5 GB | ⚡ Fast | ★★★★ |
| `mistral:7b` | 4.4 GB | 🐢 Slower | ★★★★ |

---

## License

MIT
