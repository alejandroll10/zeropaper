# Claude Code Sandbox & Permissions

**Sources**:
- https://code.claude.com/docs/en/sandboxing.md
- https://code.claude.com/docs/en/permissions.md
- https://code.claude.com/docs/en/security.md
- https://code.claude.com/docs/en/settings.md

## Overview

Two complementary security layers:

| Layer | Controls | Applies To | Enforcement |
|-------|----------|-----------|-------------|
| **Permissions** | Which tools Claude can use | All tools | User prompt allow/deny |
| **Sandboxing** | What Bash commands can access | Bash + child processes | OS-level (bubblewrap on Linux) |

## Linux/Ubuntu Setup

```bash
sudo apt-get update
sudo apt-get install bubblewrap socat
```

| Platform | Technology | Status |
|----------|-----------|--------|
| macOS | Seatbelt | Works out of the box |
| Linux | bubblewrap | Requires `bubblewrap` + `socat` |
| WSL2 | bubblewrap | Requires installation |
| WSL1 | N/A | Not supported |

## 5 Permission Modes

| Mode | Description |
|------|-------------|
| `default` | Standard: prompts for permission on first use |
| `acceptEdits` | Auto-accept file edits; prompts for bash |
| `plan` | Read-only analysis, no modifications |
| `dontAsk` | Auto-deny unless pre-approved via allow rules |
| `bypassPermissions` | Skip ALL permission prompts |

Set via CLI: `claude --permission-mode plan`
Set via settings: `"defaultMode": "acceptEdits"`

## --dangerously-skip-permissions

```bash
claude --dangerously-skip-permissions
```

Skips ALL permission prompts. Auto-approves everything.

### NEVER run on host machine. Always use in a container:

```bash
docker run --rm --network none \
  -v "$(pwd):/work" \
  my-claude-sandbox \
  --dangerously-skip-permissions
```

### Risks without isolation:
- File modification/deletion without confirmation
- Irreversible changes
- Data exfiltration (SSH keys, credentials)
- Prompt injection attacks execute without approval

## Sandbox Configuration

### Enable
```bash
/sandbox
```

### Full settings.json config

```json
{
  "sandbox": {
    "enabled": true,
    "mode": "auto-allow",
    "filesystem": {
      "allowWrite": ["./", "//tmp/build"],
      "denyWrite": ["~/.ssh", "~/.aws", "//etc"],
      "allowRead": ["."],
      "denyRead": ["~/secrets"]
    },
    "network": {
      "allowedDomains": ["github.com", "npm.org"],
      "deniedDomains": ["malicious.com"],
      "httpProxyPort": 8080,
      "socksProxyPort": 8081,
      "allowUnixSockets": [],
      "allowLocalBinding": false
    },
    "allowManagedDomainsOnly": false,
    "allowUnsandboxedCommands": true,
    "excludedCommands": ["docker", "watchman"],
    "enableWeakerNestedSandbox": false
  }
}
```

### Path Prefixes

| Prefix | Meaning | Example |
|--------|---------|---------|
| `//` | Absolute from root | `//tmp/build` → `/tmp/build` |
| `~/` | Home directory | `~/.kube` → `$HOME/.kube` |
| `/` | Relative to settings file | `/build` → `$SETTINGS_DIR/build` |
| `./` | Relative path | `./output` |

### Sandbox Modes
- **auto-allow**: Bash commands auto-allowed inside sandbox; unsandboxable commands fall back to permission flow
- **Regular**: All bash commands go through standard permission flow

## Permission Rules

### Syntax: `Tool` or `Tool(specifier)`

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run build)",
      "Bash(git *)",
      "Read(./.env)",
      "WebFetch(domain:example.com)",
      "Edit(/src/**/*.ts)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(sudo *)"
    ],
    "ask": [
      "Bash(curl *)"
    ]
  }
}
```

### Evaluation Order: Deny → Ask → Allow
First matching rule wins. Deny always takes precedence.

### Wildcards
- `Bash(npm run *)` — matches commands starting with `npm run `
- `Edit(/src/**/*.ts)` — gitignore-style patterns
- `Bash(git * main)` — multiple wildcards

## Docker-Based Safe Sandbox for Ubuntu

### Dockerfile

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    bubblewrap socat git curl nodejs npm

RUN useradd -m claude
USER claude
WORKDIR /home/claude

ENTRYPOINT ["claude"]
```

### Run with full isolation

```bash
docker build -t claude-safe .

docker run --rm \
  --network none \
  -v /safe/project:/home/claude/project \
  claude-safe --dangerously-skip-permissions
```

### Defense-in-depth: container + sandbox + permissions

```json
{
  "defaultMode": "acceptEdits",
  "sandbox": {
    "enabled": true,
    "mode": "auto-allow",
    "filesystem": {
      "allowWrite": ["./"],
      "denyWrite": ["~/.ssh", "~/.aws", "~/.claude"]
    },
    "network": {
      "allowedDomains": ["github.com", "npm.org"]
    }
  },
  "permissions": {
    "allow": ["Read", "Bash(git *)", "Bash(npm run *)"],
    "deny": ["Bash(rm -rf *)", "Bash(sudo *)"]
  }
}
```

## Settings Precedence (highest to lowest)

1. **Managed settings** (cannot be overridden)
2. **CLI arguments** (`--permission-mode`, `--dangerously-skip-permissions`)
3. **Local project** (`.claude/settings.local.json`)
4. **Shared project** (`.claude/settings.json`)
5. **User settings** (`~/.claude/settings.json`)

## Excluded Commands

Some tools are incompatible with sandbox:

```json
{
  "sandbox": {
    "excludedCommands": ["docker", "watchman"]
  }
}
```

These run outside sandbox with normal permission flow.

## Open Source Sandbox Runtime

```bash
npx @anthropic-ai/sandbox-runtime <command>
```

GitHub: https://github.com/anthropic-experimental/sandbox-runtime
