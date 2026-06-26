# Draft: oh-my-openagent Installation

## Requirements (confirmed)
- **Platform**: OpenCode (Ultimate Edition)
- **Model Access**: OpenRouter (multi-model gateway)
- **Claude Subscription**: NO (using OpenRouter)
- **OpenAI Subscription**: NO (using OpenRouter)
- **Gemini**: NO (using OpenRouter)
- **GitHub Copilot**: NO
- **OpenCode Version**: 1.14.50 ✓

## Technical Decisions
- Use `--claude=no --openai=no --gemini=no --copilot=no` flags
- Skip standard provider OAuth flows
- Configure OpenRouter as primary provider after installation

## Installation Command
```bash
bunx oh-my-openagent install --no-tui --platform=opencode --claude=no --openai=no --gemini=no --copilot=no --skip-auth
```

## Post-Install Configuration
- Configure OpenRouter in opencode.json
- Set up model mappings for agents

## Open Questions
- None remaining
