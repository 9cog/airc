# airc — 9cog Framework Role

## Role: User Interface Layer (AI-Enhanced rc Shell)

airc provides the primary user interface for the 9cog framework — a Plan 9
rc shell with integrated AI capabilities that interacts with the AI filesystem.

## Framework Integration

### Shell Functions for AI Filesystem

airc extends the rc shell with functions that operate on the `/ai/` mount point:

```rc
# AI chat via file operations
fn ai {
    if(~ $#* 0) {
        echo 'usage: ai <query>' >[1=2]
        return 1
    }
    # Create session if needed
    if(! test -d /ai/sessions/$pid) {
        echo $user > /ai/sessions/new/ctl
    }
    echo $"* > /ai/sessions/$pid/ctl
    cat /ai/sessions/$pid/history | tail -1
}

# Knowledge graph queries
fn know {
    echo $"* > /ai/knowledge/query
    cat /ai/knowledge/query
}

# Switch AI model
fn model {
    if(~ $#* 0)
        cat /ai/models/active
    if not
        echo $1 > /ai/models/active
}

# Show topology
fn topo {
    cat /ai/topology/lifecycle
    cat /ai/topology/vertices
}
```

### AI-Aware Tab Completion

airc provides tab completion for `/ai/` paths:

```
/ai/sess<TAB>     → /ai/sessions/
/ai/mod<TAB>      → /ai/models/
/ai/know<TAB>     → /ai/knowledge/
```

### Shell Detection for AI Tools

airc includes shell detection support (from `rc-integration.sh`) so that
external AI tools like aichat can properly detect and work with the rc shell.

### Environment Variables

```rc
# Framework environment
NINEP_AI=/ai            # Mount point for AI filesystem
AI_MODEL=claude-sonnet-4-6  # Default model
AI_SESSION=$pid         # Per-process session ID
```

## Architecture

```
┌────────────────────────────────┐
│  User types: ai 'explain 9P'  │
├────────────────────────────────┤
│  airc (this repo)              │
│  rc shell + AI functions       │
│  Tab completion for /ai/       │
├────────────────────────────────┤
│  9P mount of AI filesystem     │
│  /ai/ → localhost:5641         │
├────────────────────────────────┤
│  aifs server (go9p)            │
└────────────────────────────────┘
```

## Key Files

| File | Purpose |
|------|----------|
| `builtins.c` | Built-in shell commands |
| `rc-integration.sh` | Shell detection for AI tools |
| `rc-shell.rc` | Native rc integration script |
| `example.rcrc` | Configuration with framework functions |

## See Also

- [9cog Framework Architecture](https://github.com/9cog/9fs9rc/blob/main/framework/ARCHITECTURE.md)
- [AI Integration Guide](AI_INTEGRATION.md)
