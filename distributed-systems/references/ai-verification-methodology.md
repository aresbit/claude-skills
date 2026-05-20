# AI-Driven Verification Methodology

The 8-step methodology proven on Azure Storage production code. AI (GitHub Copilot with o3 + Claude 3.7 Sonnet) autonomously generated precise TLA+ specifications and discovered a subtle race condition that escaped traditional review and testing.

## The 8-Step Strategic Plan

### Step 1: Systematic Code Path Cataloging
AI identifies all code paths through the feature. Give it only the feature name + component directory — it autonomously finds relevant files.

**What AI does:**
- Searches the codebase for relevant modules, structs, and function
- Traces call graphs from entry points
- Maps all possible execution paths

### Step 2: Data Structure Extraction
AI extracts all state variables, their types, constraints, and relationships from the source code.

**What AI produces:**
- Per-component state variable inventory
- Type constraints for each variable
- Relationships between variables across components

### Step 3: Behavioral Pattern Extraction
AI identifies patterns in how state changes, including ordering constraints, atomicity guarantees, and observed invariants.

**What AI looks for:**
- Lock ordering patterns
- Atomic write patterns
- Fire-and-forget vs synchronous patterns
- Retry and idempotency mechanisms

### Step 4: Invariant Extraction
AI surfaces invariants from code comments, assertions, commit messages, and PR discussions. Primary safety invariant usually matches what experienced engineers expect.

**Sources AI mines:**
- `debug_assert!` / `assert!` statements
- Comments mentioning "invariant", "must", "always", "never"
- Git commit messages describing safety fixes
- PR discussions about edge cases

### Step 5: Minimal TLA+ Model Construction
AI builds the smallest model that captures the critical behaviors. Includes failure modes: crashes, network partitions, message reordering.

**Key principle:** Model only what's needed to verify the properties. Abstractions should preserve correctness-relevant detail while keeping state space manageable.

### Step 6: Iterative Refinement
AI updates one atomic action at a time. This incremental approach maintains precision throughout refinement.

**User prompting pattern:**
```
I notice <mechanism> is missing from the spec. Investigate how it's used
in the code and update the spec to incorporate it.
```

### Step 7: Git History Deep-Dive
AI analyzes commit history via git MCP. This reveals safety mechanisms and invariants not visible in the current codebase snapshot.

**Real impact:** Git analysis on Azure Storage revealed a pessimistic locking mechanism that was critical to safety but not obvious from reading the current code alone.

**Prompt:**
```
Analyze the git commit history for <feature>. Look for any safety
mechanisms, invariants, or edge-case fixes we might have missed.
```

### Step 8: Model Checking & Violation Analysis
TLC finds violations → AI analyzes counterexample traces → AI identifies the problematic sequence → AI explains the root cause at the design level.

## The Azure Storage Discovery

**The bug:** An old Paxos primary could perform a deletion while a new primary simultaneously added a reference.

**Why it was missed:**
- Traditional code review: too subtle across multiple components
- Testing: required specific interleaving of concurrent operations
- Scale: would have manifested in production at Azure's scale

**How AI found it:**
1. Generated initial spec with 10+ invariants
2. Model checker found invariant violation
3. AI analyzed the counterexample trace
4. AI identified the concurrent deletion + reference addition sequence

## Automation Vision

Based on current capabilities, the full autonomous pipeline:

```
Codebase → AI System Analysis → Invariant Discovery →
TLA+ Model → Auto Model Check → Violations Trigger Tests →
Confirmed Bugs Auto-Fixed → Spec-Impl Discrepancies Drive Refinement →
RL Feedback Loop → Continuous Improvement
```

Each iteration generates training data, enabling AI to continuously improve verification capability. Distributed system correctness becomes a domain with verifiable outcomes — where AI consistently outperforms humans.
