# 🛠️ Troubleshooting Guide

This guide addresses common technical hurdles when running DevAgent in local environments.

## 🦙 Ollama Issues

### Connection Refused
**Error**: `Failed to connect to Ollama at http://localhost:11434`
- **Fix**: Ensure Ollama is running. On Windows, check the system tray. On Linux/macOS, run `ollama serve`.
- **Environment Variable**: If Ollama is on a different host, set `OLLAMA_HOST=http://your-ip:11434`.

### Slow Inference
- **Fix**: DevAgent v3.4.0 is optimized for `qwen2.5-coder:3b`. If you have < 8GB RAM, avoid `7b` models.
- **Hardware Acceleration**: Ensure your GPU is being used. Run `ollama list` to see if the model is loaded in VRAM.

---

## 🔍 Search & Indexing (FAISS)

### "FAISS Not Found"
**Error**: `Semantic search disabled (faiss not installed)`
- **Fix**: `pip install faiss-cpu`. 
- **Note**: On some Windows systems, you may need the [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/).

### Index Out of Date
- **Fix**: If you've made massive changes to your project, DevAgent might use a stale index. Delete the `faiss_index/` folder in your project root to force a re-index.

---

## 🏖️ Environment & Venv Issues

### Venv Creation Failure
- **Error**: `Error: [WinError 2] The system cannot find the file specified` during venv creation.
- **Fix**: Ensure `python` is in your PATH and the `venv` module is available. On Linux (Ubuntu/Debian), you might need: `sudo apt install python3-venv`.

### Dependency Repair Loop
- **Issue**: Agent keeps trying to install the same package.
- **Fix**: Check if the package name is correct. If you are behind a proxy, ensures your environment has `HTTP_PROXY`/`HTTPS_PROXY` set, as the agent's internal `pip` calls need internet access to fetch packages.

---

## 🪟 Windows Specifics

### UnicodeEncodeError
- **Error**: `'charmap' codec can't encode character...`
- **Fix**: We've replaced most UTF-8 symbols in v3.4.0. If you still see this, run `$env:PYTHONIOENCODING="utf-8"` in PowerShell before starting DevAgent.

### Long Path Issues
- **Issue**: Path exceeds 260 characters in deep repositories.
- **Fix**: Enable Long Paths in Windows:
  1. Open Registry Editor.
  2. Navigate to `HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\FileSystem`.
  3. Set `LongPathsEnabled` to `1`.

---

## 🧪 Benchmark Failures

### "No tests ran"
- **Issue**: Pytest fails to find tests in `benchmarks/`.
- **Fix**: Ensure you are running `devagent` from the root of the DevAgent repository. Benchmark paths are relative to the installation root.

---

## 🆘 Still Stuck?
If your issue isn't listed here:
1. Run `devagent doctor` and include the output.
2. Check the logs in `logs/run.json`.
3. Open an issue on [GitHub](https://github.com/VedantJadhav701/Developer-Code-Intelligence-Agent/issues).
