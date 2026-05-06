# 🎬 Elite Demo Recording Guide

Engineers trust visible execution. Use this guide to record high-impact GIF demos for the README and landing page.

## Recommended Tools
- **Windows**: [ScreenToGif](https://www.screentogif.com/) (Highly recommended for high-quality, small file size GIFs).
- **macOS/Linux**: [Asciinema](https://asciinema.org/) + [Agg](https://github.com/asciinema/agg) for terminal-perfect GIFs.

---

## Scenario 1: Autonomous Environment Repair
**The Goal**: Show DevAgent fixing a `ModuleNotFoundError`.
1. Create a file `buggy.py` with `import non_existent_package`.
2. Run:
   ```bash
   devagent run --task "Fix the import error in buggy.py" --verbose
   ```
3. **Capture**: The moment the agent sees the error, calls `repair_environment`, installs the package, and then succeeds.

## Scenario 2: Surgical Patching & Dry-Run
**The Goal**: Show the agent proposing a precision diff without applying it.
1. Run:
   ```bash
   devagent run --task "Add a docstring to utils.py" --dry-run
   ```
2. **Capture**: The colorized diff output in the terminal and the "DRY RUN: No changes applied" message.

## Scenario 3: Safety Rollback
**The Goal**: Show how easily a developer can revert agent changes.
1. Run a successful task:
   ```bash
   devagent run --task "Refactor calculator.py"
   ```
2. Immediately run:
   ```bash
   devagent rollback
   ```
3. **Capture**: The "Snapshot restored successfully" message and the git diff returning to zero.

## Scenario 4: Explain Mode
**The Goal**: Show the agent's "thought process."
1. Run:
   ```bash
   devagent run --task "Optimize the sorting algorithm" --explain
   ```
2. **Capture**: The "Step-by-step breakdown" at the end of the run, showing the logical flow.

---

## Tips for Elite GIFs
- **Terminal Theme**: Use a clean, dark theme (e.g., One Half Dark or Dracula).
- **Font**: Use a modern monospace font like `JetBrains Mono` or `Fira Code`.
- **Window Size**: Keep the terminal window small (around 80x24 characters) so the text is legible in the README.
- **Speed**: If the LLM is slow, speed up the GIF in post-processing to keep it snappy.
