# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **DO NOT** open a public issue
2. Email **vedantjadhav701@gmail.com** with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
3. You will receive a response within **48 hours**
4. A fix will be released as soon as possible

## Security Considerations

- This agent executes code locally via `subprocess` (pytest, ripgrep, flake8)
- It writes files to disk based on LLM output
- Always run in a sandboxed environment or on non-critical code
- Never point the agent at system directories or sensitive files

## Best Practices

- Run the agent inside a virtual environment
- Use `--root` to limit the agent's scope to a specific project directory
- Review `logs/run.json` after each run to audit what the agent did
- Back up your code before running the agent on important projects
