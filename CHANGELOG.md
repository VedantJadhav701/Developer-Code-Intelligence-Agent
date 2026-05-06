# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-05-06

### Added
- **Planner Layer** — LLM-powered task planning with likely file detection and step generation
- **Retrieval Layer** — FAISS + sentence-transformers semantic code search with keyword fallback
- **Memory System** — Short-term working memory + long-term semantic index with chunk deduplication
- **Patch Engine** — Unified diff generation with line-level stats instead of full file rewrites
- **Sandbox Mode** — Isolated workspace copies for safe agent operations (`--sandbox`)
- **Benchmark System** — 5 benchmark suites (divide_by_zero, missing_validation, syntax_error, import_bug, edge_case)
- **Metrics Collector** — Latency, token estimates, retry counts, and performance tracking
- **Configuration Module** — Centralized config with model presets and inference options
- **Semantic Search Tool** — FAISS-powered code retrieval (`semantic_search`)
- **Git Tools** — `git_diff`, `git_status`, `git_commit`, `git_push` integration
- **Standalone Linter** — Separated linter tool with file and project-level support
- **New CLI Flags** — `--benchmark`, `--sandbox`, `--auto-commit`, `--auto-push`, `--verbose`
- **ASCII Banner** — Professional CLI branding on startup
- **Benchmark CLI Mode** — `python main.py --benchmark` runs all benchmark suites

### Changed
- **Default model** upgraded from `qwen2.5:3b` to `qwen2.5-coder:3b`
- **Context window** increased from 2048 to 4096 tokens
- **Max steps** default increased from 3 to 5
- **Agent core** rewritten with retrieval-first architecture
- **Prompt templates** now include retrieved context from semantic memory
- **Action parser** extended with `semantic_search` and `git_diff` actions
- **Logger** now tracks latency, model info, and patch summaries per step
- **State object** expanded with retrieval, planner, patch, and sandbox slots

### Architecture
- Modular multi-layer design: CLI → Planner → Retrieval → Tools → Review → Validation
- Designed for future multi-agent upgrade (Planner → Coder → Reviewer → Evaluator)
- All heavy deps (FAISS, sentence-transformers) are lazy-loaded with graceful fallback

## [1.0.0] - 2026-05-06

### Added
- **ReAct Agent Loop** — Thought → Action → Observation → Fix → Self-Review → Test
- **Self-Review Module** — LLM critiques its own code fixes (APPROVED/REVISE)
- **Tool System** — `search_code`, `read_file`, `write_file`, `run_tests`, `lint_code`
- **Ollama Integration** — Python SDK with `num_ctx=2048` for low-RAM systems
- **Structured Logging** — Every step logged to `logs/run.json`
- **CLI Interface** — `--task`, `--root`, `--max-steps`, `--model` flags
- **Smart Fallbacks** — Auto-extracts filenames from task, keyword search, retry dedup
- **Demo Project** — Calculator with intentional bug for testing
- **Full Documentation** — README, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY

### Technical Details
- Runs fully offline via Ollama
- Default model: `qwen2.5:3b` (1.9 GB, fits in 4 GB VRAM)
- Python 3.11+ required
- ripgrep optional (falls back to findstr/grep)
