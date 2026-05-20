# Lamport Agent — 6-Phase Verification Workflow

Complete workflow template for AI-assisted TLA+ verification. All artifacts go in `./spec/<feature>/`.

## Phase 0: plan.json

```json
{
  "phase": 0,
  "phases": [
    {
      "id": 0, "name": "Planning", "status": "in-progress",
      "tasks": ["Create verification plan file", "List all phases with goals and checkpoints"]
    },
    {
      "id": 1, "name": "Happy Path & Architecture", "status": "not-started",
      "tasks": [
        "Collect happy path workflows and entities from codebase/docs",
        "Discover architecture: components, data structures, interfaces",
        "Document in happy_path.md and architecture.md",
        "Get user validation for Phase 1 artifacts"
      ]
    },
    {
      "id": 2, "name": "Error Handling & Concurrency", "status": "not-started",
      "tasks": [
        "Analyze failure modes and recovery paths",
        "Identify concurrent interactions and potential races",
        "Document behaviors in behavior.md",
        "Create diagrams in diagrams.md",
        "Get user review of Phase 2 artifacts"
      ]
    },
    {
      "id": 3, "name": "Verification Properties", "status": "not-started",
      "tasks": [
        "Draft safety and liveness properties",
        "Prioritize by criticality",
        "Document in properties.md",
        "Review and refine with user"
      ]
    },
    {
      "id": 4, "name": "TLA+ Model", "status": "not-started",
      "tasks": [
        "Create core TLA+ specification",
        "Encode properties and type invariants",
        "Create model checking configuration"
      ]
    },
    {
      "id": 5, "name": "Model Checking & Report", "status": "not-started",
      "tasks": [
        "Run SANY parsing and smoke tests",
        "Run full TLC model checking",
        "Document counterexamples with design implications",
        "Summarize verification in verification_summary.md"
      ]
    }
  ]
}
```

## Phase 1: Happy Path & Architecture

### happy_path.md Structure
```markdown
# <Feature> — Happy Path

## Entities
- **Entity1**: Role and responsibility
- **Entity2**: Role and responsibility

## State / Data
- `variable : Type` — description, constraints

## Happy Path Write Workflow
1. Step one with component interaction
2. Step two with state transition

### Happy-path guarantee
Formal statement of what the system guarantees on success.

## Success Conditions
- Condition 1
- Condition 2
```

### architecture.md Structure
```markdown
# <Feature> — Architecture Overview

## Components
- **Component1** (`path/to/source`): Role, responsibility
- **Component2** (`path/to/source`): Role, responsibility

## Data Structures (Conceptual)
- Per-entity state abstraction
- Configuration structures

## Interfaces and Protocols
- ComponentA → ComponentB: Operation(args)

## Configuration & Parameters
- Key parameters and their defaults

## Simplifications for TLA+ Model
- What we abstract and why
```

## Phase 2: Error Handling & Concurrency

### behavior.md Structure
```markdown
# <Feature> — Error Handling and Concurrency

## 1. Failure Modes
1. **Failure scenario**: Description and affected components
2. ...

## 2. Error Handling — Protocol Under Failure
### 2.1 Component's Perspective
- Detection mechanism
- Recovery procedure
- Consistency outcome

## 3. Concurrency Behavior
### 3.1 Concurrent Operations on Same Resource
### 3.2 Concurrent Reads and Writes
### 3.3 Operations During Failure and Recovery

## 4. Candidate Invariants (Informal)
1. **Safety — Description**: Formal-ish statement
2. **Liveness — Description**: Formal-ish statement
```

## Phase 3: Verification Properties

### Property Priority Order
1. Critical safety (things that must NEVER happen)
2. Data consistency invariants (always true)
3. Protocol correctness (state machine validity)
4. Performance/liveness (eventually happens)

### Property Format
```markdown
## N. Safety: <Short Name>

**Informal:** Plain English description.

**Motivation:** Why this property matters for correctness.

**Semi-formal:** □ ( condition ⇒ □_{future} ( consequence ) )
```

### Target: 7-10 properties per feature
- 5-7 safety properties (invariants)
- 1-3 liveness properties (temporal)

## Phase 4: TLA+ Model

### Specification Structure
```tla
---- MODULE Feature ----
EXTENDS Integers, Sequences, TLC

\* State variables
VARIABLES committed, pending, state, chainVersion

\* Type invariant
TypeOK ==
  /\ committed \in [Targets -> [Chunks -> Nat]]
  /\ state \in [Targets -> {SERVING, OFFLINE, SYNCING, WAITING}]

\* Initial state
Init ==
  /\ committed = [t \in Targets |-> [c \in Chunks |-> 0]]
  /\ state = [t \in Targets |-> SERVING]

\* State transitions
WriteHead(t, c) == ...
CommitTail(t, c) == ...
FailTarget(t) == ...
RecoverTarget(t) == ...

Next == \E t \in Targets, c \in Chunks :
  \/ WriteHead(t, c)
  \/ CommitTail(t, c)
  \/ FailTarget(t)
  \/ RecoverTarget(t)

\* Invariants
NoStaleReads == ...
ServingUpToDate == ...
MonotoneVersions == ...

====
```

### Model Checking Config
```
SPECIFICATION Spec
CONSTANTS Targets = {t1, t2, t3}
          Chunks = {c1, c2}
INVARIANT TypeOK NoStaleReads ServingUpToDate
```

## Phase 5: Model Check & Debug

### Pipeline
```
tlaplus_parse  → check syntax
tlaplus_smoke  → basic reachability
tlaplus_check  → full invariant checking
```

### Counterexample Format
```markdown
# Counterexample: <Property Name>

## Trace
1. State 0: <initial conditions>
2. Step 1: <action taken>
3. Step 2: <action taken>
...
N. State N: <invariant violated>

## Root Cause
Why the implementation allows this violation.

## Suggested Fix
Design-level change to the system, not the spec.
```

### Critical Rule
**Only fix syntax errors in the spec.** When an invariant is violated, the *implementation* or *design* is wrong, not the specification. Fix the system, then re-check.
