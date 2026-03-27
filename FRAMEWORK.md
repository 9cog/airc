# airc — 9cog Framework Role

## Role: User Interface Layer (AI-Enhanced rc Shell)

airc provides the primary user interface for the 9cog framework — a Plan 9
rc shell with integrated AI capabilities that interacts with the AI filesystem.

## Framework Integration

### Shell Functions

Source `9cog.rc` to get these commands:

- `ai <query>` — Chat with AI via /ai/sessions/
- `aichat <msg>` — Multi-turn conversation
- `know [pattern]` — Query knowledge graph
- `model [name]` — List/switch AI models
- `topo [sub]` — View organizational topology
- `features` — List AI capabilities
- `sessions <cmd>` — Manage sessions
- `9cog status` — Framework status

### Shell Detection

airc includes shell detection support so external AI tools
can properly detect and work with the rc shell.

## See Also

- [9cog Framework Architecture](https://github.com/9cog/9fs9rc/blob/main/framework/ARCHITECTURE.md)
- [AI Integration Guide](AI_INTEGRATION.md)
