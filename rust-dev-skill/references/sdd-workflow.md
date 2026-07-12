# Lightweight Spec-Driven Development for Rust

How to use `/specify` and `/clarify` (spec-kit) to drive Rust feature development. Based on the workflow that produced 130K lines of correct Paxos implementation.

## Why Lightweight SDD

Rigid SDD (requirements.md → design.md → task-list.md) fails because:
- Documents drift from code as implementation reveals new constraints
- Keeping three docs consistent is overhead, not value
- AI agents perform best on focused, single-session tasks

**The fix:** One spec markdown per feature. Clarify interactively. Implement one user story at a time.

## Full Workflow

### Step 1: `/specify` — Generate the Spec

```
/specify: Add snapshotting to the multi-Paxos replica.
The replica should periodically create state snapshots to truncate the log.
Snapshots include: current state machine state, last applied slot, membership configuration.
```

AI generates a spec with user stories like:

```markdown
# Snapshotting

## User Stories

### US1: Periodic Snapshot Creation
As a replica operator, I want the system to automatically create snapshots
every N log entries so that log size stays bounded.

Acceptance Criteria:
- Snapshot is created when log_count % N == 0
- Snapshot includes: applied_state, last_applied_slot, config
- Snapshot is written atomically to persistent storage
- Previous snapshot is retained until new one is complete

### US2: Snapshot-Based Recovery
...
```

### Step 2: `/clarify` — Refine and Expand

```
/clarify
```

The AI self-critiques and asks targeted questions. Spend most of your time here — this is where correctness is designed.

Example `/clarify` interaction:

```
● Question 1: Snapshot Failure Handling

  What should happen when snapshot creation fails mid-write?

  Recommended: Option A — Retry with exponential backoff, alert after 3 failures

  This balances robustness with operational visibility. Retrying handles
  transient I/O errors; alerting prevents silent snapshot degradation.

  | Option | Description |
  |--------|-------------|
  | A      | Retry with backoff, alert after 3 failures |
  | B      | Skip this snapshot, try again at next interval |
  | C      | Panic — snapshot failure is critical |
  | D      | Fall back to in-memory snapshot only |
```

**Critical `/clarify` prompts to add:**
- "Suggest additional user stories not in the initial spec"
- "Identify edge cases for each acceptance criterion"
- "What assumptions am I making that could be wrong?"

### Step 3: Plan Mode — One User Story

Enter plan mode for a single user story. This is the sweet spot — AI handles this scope well without context loss.

```
/plan: Implement US1 - Periodic Snapshot Creation
```

The plan should cover:
- Files to create/modify
- Data structures (SnapshotMetadata, SnapshotWriter)
- Error handling strategy
- Integration points (log truncation, recovery path)

### Step 4: Implement

Implement the user story. Along the way:
- Discover additions/tweaks → handle in the same session
- Don't worry about context compression for a single user story
- Write contracts for all new public functions
- Generate tests from contracts

### Step 5: Repeat

Move to the next user story. Each story is self-contained enough that ordering is usually flexible.

## User Story Sizing

A well-sized user story:
- Can be implemented in one coding session (~2-4 hours of AI-assisted work)
- Touches 2-5 files
- Has 3-8 acceptance criteria
- Is independently testable
- Maps to a clear capability (not a technical layer)

**Too large:** "Implement multi-Paxos consensus"
**Too small:** "Add a getter for ballot_number"
**Just right:** "Implement proposer phase 1 (prepare/ballot)"
