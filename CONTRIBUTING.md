# Contributing to DevAgent

First off, **thank you** for considering contributing! 🎉 Every contribution — code, docs, bug reports, feature ideas — makes this project better for everyone.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guide](#style-guide)
- [Community](#community)

## Code of Conduct

This project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### 🐛 Report Bugs

Found a bug? [Open an issue](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/issues/new?template=bug_report.md) with:
- Your OS and Python version
- The Ollama model you used
- Steps to reproduce
- Expected vs actual behavior

### 💡 Suggest Features

Have an idea? [Open a feature request](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/issues/new?template=feature_request.md). We especially welcome:
- New tools (e.g., `git_diff`, `refactor_code`)
- Support for more languages (JS, Go, Rust)
- Better prompting strategies
- Memory/RAG integration ideas

### 🔧 Submit Code

Look for issues tagged:
- [`good first issue`](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/labels/good%20first%20issue) — Great for newcomers
- [`help wanted`](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/labels/help%20wanted) — We'd love your expertise
- [`enhancement`](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/labels/enhancement) — Feature additions

### 📝 Improve Docs

Documentation improvements are always welcome — fix typos, add examples, improve explanations.

## Getting Started

1. **Fork** the repo
2. **Clone** your fork:
   ```bash
   git clone https://github.com/<your-username>/Developer-Code-Intelligence-Agent.git
   cd Developer-Code-Intelligence-Agent
   ```
3. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

```bash
# Create a virtual environment (conda or venv)
conda create -n devagent python=3.11 -y
conda activate devagent

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install flake8 pytest black isort

# Make sure Ollama is running
ollama serve
ollama pull qwen2.5:3b

# Run tests
python -m pytest demo_project/ -v

# Run the agent
python main.py --task "Fix the divide-by-zero bug" --root ./demo_project
```

## Pull Request Process

1. **Update tests** — If you add a feature, add tests for it
2. **Run the linter:**
   ```bash
   flake8 app/ tools/ utils/ --max-line-length=120
   ```
3. **Run tests:**
   ```bash
   python -m pytest demo_project/ -v
   ```
4. **Update README.md** if your change affects usage
5. **Write a clear PR description** explaining what and why
6. **One PR per feature/fix** — keep them focused

### PR Title Convention

```
feat: add git_diff tool for viewing changes
fix: handle empty LLM responses in reviewer
docs: add examples for multi-file projects
refactor: simplify action parsing logic
test: add integration tests for search tool
```

## Style Guide

### Python

- **Python 3.11+** with `from __future__ import annotations`
- **Max line length:** 120 characters
- **Formatting:** We recommend `black` and `isort`
- **Type hints:** Use them everywhere
- **Docstrings:** Google style

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <short description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

### Code Principles

- **Keep prompts SHORT** — Small models have limited context
- **Fail gracefully** — Tools should return error strings, never raise
- **Cap outputs** — Always limit text sent to the LLM
- **No external APIs** — Everything runs locally

## Community

- ⭐ **Star the repo** if you find it useful
- 🐦 **Share on Twitter/X** with `#DevAgent`
- 💬 **Discussions** — Use GitHub Discussions for questions

---

Thank you for helping make DevAgent better! 🚀
