# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
