# 📖 User Guide — How to Use DevAgent on Your Projects

## Table of Contents

- [How It Works (30-second version)](#how-it-works-30-second-version)
- [Setup (One-time)](#setup-one-time)
- [Basic Usage](#basic-usage)
- [Real-World Examples](#real-world-examples)
- [What Makes a Good Task](#what-makes-a-good-task)
- [What Your Project Needs](#what-your-project-needs)
- [Tips for Best Results](#tips-for-best-results)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## How It Works (30-second version)

You give DevAgent a **task** and point it at your **project folder**. It will:

1. **Search** your code for relevant files
2. **Read** the file and understand the problem
3. **Generate** a fix using a local AI model
4. **Review** its own fix (like a code review)
5. **Run your tests** to verify the fix works
6. If tests fail → **retry** with the error output

That's it. You don't interact with it. It runs, fixes, and exits.

---

## Setup (One-time)

### Step 1: Install Ollama

Download from [ollama.ai](https://ollama.ai) and install it.

```bash
# Pull a model (only needed once, ~2 GB download)
ollama pull qwen2.5:3b
```

### Step 2: Clone DevAgent

```bash
git clone https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent.git
cd Developer-Code-Intelligence-Agent
```

### Step 3: Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify it works

```bash
python main.py --help
```

You should see:
```
usage: main.py [-h] --task TASK [--root ROOT] [--max-steps MAX_STEPS] [--model MODEL]
```

**Done!** You're ready to use it on any project.

---

## Basic Usage

### The command pattern is always:

```bash
python main.py --task "<what you want fixed>" --root <path-to-your-project>
```

### Example:

```bash
python main.py --task "Fix the login function to handle empty passwords" --root C:\Users\me\projects\my-webapp
```

---

## Real-World Examples

### Example 1: Fix a Failing Test

You have a Python project and `pytest` shows a failing test:

```bash
# First, see what's failing
cd C:\Users\me\projects\my-api
pytest -v
# Output: FAILED test_users.py::test_create_user_validates_email

# Now let DevAgent fix it
cd C:\path\to\Developer-Code-Intelligence-Agent
python main.py \
  --task "Fix test_create_user_validates_email — the create_user function should validate email format" \
  --root C:\Users\me\projects\my-api
```

DevAgent will:
- Search for `create_user` and `email` in your code
- Read the relevant file
- Generate a fix with email validation
- Self-review → approve or revise
- Run pytest → confirm all tests pass

---

### Example 2: Add Error Handling

```bash
python main.py \
  --task "Add try-except error handling to the database connection in db.py" \
  --root ./my-project
```

---

### Example 3: Fix a Specific Bug

```bash
python main.py \
  --task "Fix the TypeError: unsupported operand in calculate_total function in orders.py" \
  --root ./ecommerce-backend
```

---

### Example 4: Use on a Different Project Structure

```bash
# Works on any Python project with tests
python main.py \
  --task "Fix the import error in utils/helpers.py" \
  --root C:\Users\me\projects\ml-pipeline \
  --max-steps 5
```

---

### Example 5: Use a Larger Model for Complex Tasks

```bash
# Use mistral:7b for harder problems (needs 8GB+ RAM)
python main.py \
  --task "Refactor the authentication middleware to use JWT tokens" \
  --root ./api-server \
  --model mistral:7b
```

---

### Example 6: Quick Demo (Try Right Now!)

The repo includes a demo project with an intentional bug:

```bash
# From the DevAgent directory
python main.py \
  --task "Fix the divide-by-zero bug in calculator.py so all tests pass" \
  --root ./demo_project
```

This will fix `calculator.py` in about 30 seconds.

---

## What Makes a Good Task

### ✅ Good Tasks (Specific + Testable)

```
"Fix the divide function to raise ValueError when dividing by zero"
"Add input validation to the register_user function in auth.py"
"Fix the failing test test_calculate_tax in test_billing.py"
"Handle the case where the API response is None in fetch_data.py"
"Fix the IndexError in process_batch when the list is empty"
```

### ❌ Bad Tasks (Too Vague)

```
"Improve the code"           → Too vague, which code?
"Make it faster"             → No clear file or function
"Rewrite everything"         → Too broad for 3 iterations
"Add a new feature"          → What feature? Where?
```

### Rule of Thumb

> **Mention the file name + what's wrong + what should happen.**

---

## What Your Project Needs

### Required:

| Requirement | Why |
|---|---|
| **Python files** (`.py`) | The agent searches and modifies `.py` files |
| **pytest tests** | The agent runs `pytest` to verify its fixes |

### Optional but helpful:

| Nice to have | Why |
|---|---|
| `flake8` installed | Agent will also lint the code after fixing |
| `ripgrep` (`rg`) installed | Faster code search (falls back to findstr/grep) |
| Clear test names | `test_divide_by_zero` is better than `test_case_1` |

### Minimum project structure:

```
your-project/
├── your_code.py          # Any Python file
└── test_your_code.py     # pytest tests
```

That's all you need!

---

## Tips for Best Results

### 1. Be specific in your task description

```bash
# 🟢 Good — mentions file, function, and expected behavior
--task "Fix divide() in calculator.py to raise ValueError when b is 0"

# 🔴 Bad — too vague
--task "Fix the bug"
```

### 2. Make sure your tests actually test the fix

The agent uses test results to know if it succeeded. If your tests don't cover the bug, the agent can't validate its fix.

### 3. Start with `--max-steps 3` (default)

Most fixes happen in 1-2 steps. If you have a complex bug, increase to 5:

```bash
--max-steps 5
```

### 4. Use smaller models for simple fixes

```bash
--model gemma2:2b    # fastest, simple bugs
--model qwen2.5:3b   # good balance (default)
--model mistral:7b   # best quality, complex bugs
```

### 5. Check the logs after each run

```bash
# Windows PowerShell
Get-Content .\your-project\logs\run.json | python -m json.tool

# Or just open logs/run.json in your editor
```

The log shows every thought, action, and decision the agent made.

### 6. Back up your code first

The agent **writes directly to your files**. Use git or make a copy:

```bash
git stash                # save current changes
# ... run the agent ...
git diff                 # see what the agent changed
git stash pop            # get your changes back if needed
```

---

## Troubleshooting

### "model requires more system memory"

Your model + context window is too large for your RAM.

**Fix:** Use `num_ctx=2048` (already set in DevAgent) or use a smaller model:
```bash
--model gemma2:2b      # only 1.6 GB
--model qwen2.5:3b     # 1.9 GB (default)
```

### "No results found for: ..."

The search didn't find your query in any `.py` files.

**Fix:** Make your task mention a keyword that actually exists in your code:
```bash
# Instead of: --task "Fix the authentication"
# Try:        --task "Fix the login function in auth.py"
```

### "pytest not found"

**Fix:**
```bash
pip install pytest
```

### Agent keeps retrying the same action

The agent might be stuck. This usually means the task is too vague.

**Fix:** Be more specific:
```bash
--task "In file X, function Y should do Z when given W"
```

### Agent exits with status "fail"

The agent couldn't fix the issue in the allowed iterations.

**Fix:** Try:
1. More iterations: `--max-steps 5`
2. Better model: `--model qwen3:4b`
3. More specific task description

---

## FAQ

### Q: Does it work with JavaScript / Go / Rust?

Not yet — currently Python only. Language support is on the [roadmap](README.md#-roadmap).

### Q: Does it need internet?

**No.** Everything runs locally via Ollama. No API keys, no cloud, no costs.

### Q: Will it break my code?

It writes files directly, so **always use git** or back up first. Check the logs to see exactly what it changed.

### Q: Can I use it on a large codebase?

Yes, but give it specific tasks. "Fix function X in file Y" works much better than "fix everything."

### Q: What models work best?

For 4-8 GB RAM: `qwen2.5:3b` (default)
For 8-16 GB RAM: `qwen3:4b` or `mistral:7b`

### Q: Can I use it in CI/CD?

Yes! Add it to your pipeline:
```bash
python main.py --task "Make all tests pass" --root . --max-steps 5
# Exit code 0 = success, 1 = failure
```
