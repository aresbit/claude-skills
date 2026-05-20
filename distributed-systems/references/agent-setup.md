# Lamport Agent Setup Guide

How to install and configure the Lamport Agent for AI-assisted formal verification in VS Code.

## Prerequisites

- Visual Studio Code (Insiders recommended)
- GitHub Copilot subscription
- Git

## Step 1: Create Lamport Agent

1. Open VS Code → Ctrl+Shift+P → **Chat: New Custom Agent...**
2. Name: `Lamport`
3. Copy the full prompt from [lamport-agent-prompt.md](lamport-agent-prompt.md)
4. Restart VS Code
5. Verify "Lamport" appears in the mode selector dropdown

## Step 2: Install TLA+ Extension

1. Install **TLA+** extension from VS Code marketplace
2. Open Settings → search `tlaplus`
3. Set a non-zero port for MCP (e.g., `9999`)
4. Restart VS Code

### Verify TLA+ MCP

1. Open a `.tla` file
2. Switch to Agent mode with Lamport selected
3. Check that `tlaplus_parse`, `tlaplus_check` tools are available in Configure Tools

## Step 3: Install Sequential Thinking MCP

For complex multi-step reasoning during Phases 1-3:

```bash
# Clone the MCP server
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/sequentialthinking

# Install and configure in VS Code MCP settings
npm install
```

Add to VS Code MCP configuration:
```json
{
  "mcpServers": {
    "sequential-thinking": {
      "command": "node",
      "args": ["path/to/servers/src/sequentialthinking/index.js"]
    }
  }
}
```

## Step 4: Test Installation

1. Clone a test repo with existing TLA+ specs:
```bash
git clone https://github.com/zfhuang99/lamport-agent.git
```
2. Open `test_mcp/DieHarderInstance.tla`
3. Switch to Agent mode with Lamport selected
4. Run: "Execute this TLA+ specification"
5. Verify the model checker runs and produces output

## Step 5: First Verification

Start with a simple prompt:
```
Let's formally verify the <component> implementation and whether it
maintains consistency between <operations> during <failure scenarios>.
```

The agent will:
1. Create `spec/<feature>/plan.json`
2. Start Phase 1 by exploring the codebase
3. Present findings at each checkpoint for your review

## Tool Inventory

After setup, the Lamport agent has access to:

| Tool | Purpose |
|------|---------|
| `search` / `codebase` | Find relevant files and code |
| `git_log` / `git_show` | Explore git history for safety mechanisms |
| `tlaplus_parse` | Syntax validation |
| `tlaplus_smoke` | Basic reachability check |
| `tlaplus_check` | Full TLC model checking |
| `tlaplus_symbol` | Symbol lookup in TLA+ modules |
| `sequential-thinking` | Multi-step reasoning chains |
| `edit/createFile` | Write spec artifacts |

## Troubleshooting

**TLA+ MCP tools not appearing:** Verify non-zero port in TLA+ extension settings, restart VS Code.

**Model checking hangs:** Reduce state space — use smaller CONSTANTS (2 targets, 2 chunks).

**Sequential thinking MCP missing:** Check the MCP server path in settings, ensure `node` is available.
