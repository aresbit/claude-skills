# TLA+ Specification Patterns for Distributed Systems

Patterns extracted from the CRAQ chain replication verification in DeepSeek 3FS. Reference for writing properties and models.

## Property Categories

### 1. Stale Read Prevention
The most critical safety property for any replication system.

```
□ ( CompletedWrite(x,v) ⇒
    □_{future} ( ∀ T ∈ Targets : state[T] = SERVING ∧
                 StrictReadResult(T,x,v') ⇒ v' ≥ v ) )
```

**Plain English:** Once a write completes with version v, any subsequent strict read from any serving target returns version ≥ v.

### 2. Monotone Version Numbers
```
□ ( ∀ T,x : committed[T,x] ∈ Nat )
□ ( ∀ T,x : pending[T,x] = None ∨ pending[T,x] = committed[T,x] + 1 )
```

**Plain English:** Committed versions only increase. Pending version is either absent or exactly committed+1.

### 3. Chain Ordering (Predecessor Consistency)
```
□ ( ∀ x, ∀ T,P : Predecessor(P,T) ∧ state[T] = SERVING ∧ state[P] = SERVING
     ⇒ committed[T,x] ≥ committed[P,x] )
```

**Plain English:** No serving node lags behind its predecessor in the chain.

### 4. State Isolation
```
□ ( ∀ T,x : RequestToClient(T,x) ⇒ state[T] ∈ {SERVING, LASTSERV} )
```

**Plain English:** Clients never interact with targets that are offline, waiting, or syncing.

### 5. Single Commit Per Version
```
□ ( ∀ T,x : Changed(committed[T,x]) ⇒ committed'[T,x] = pending[T,x] )
```

**Plain English:** A version is committed at most once per target. Duplicate writes are idempotent.

### 6. Rebuild Correctness
```
□ ( state'[T] = SERVING ∧ state[T] ≠ SERVING
    ⇒ state[T] = SYNCING ∧ Synced[T] )
```

**Plain English:** A target enters SERVING only after completing sync. Once serving, it never falls behind.

### 7. Pending Version Visibility
```
□ ( ∀ T,x,v : state[T] = SERVING ∧ StrictReadResult(T,x,v)
    ⇒ v = committed[T,x] )
```

**Plain English:** Strict reads never see uncommitted (pending) data.

### 8. Write Completion Liveness
```
□ ( IssueWrite(x,data) ⇒ ◇ ( CompletedWrite(x,v) ∨ WriteFailed(x) ) )
```

**Plain English:** Under fairness assumptions, every write eventually completes or definitively fails.

## TLA+ Modeling Patterns

### Fault Injection
```tla
\* Non-deterministic failure at any point
FailTarget(t) ==
  /\ state[t] = SERVING
  /\ state' = [state EXCEPT ![t] = OFFLINE]
  /\ UNCHANGED <<committed, pending>>

\* Recovery with sync
RecoverTarget(t) ==
  /\ state[t] = OFFLINE
  /\ state' = [state EXCEPT ![t] = SYNCING]
  /\ UNCHANGED <<committed, pending>>
```

### Bounded Model Checking
```tla
\* Limit state space explosion
CONSTANTS MaxVersion, MaxChainLength

\* Constraint in cfg
CONSTRAINT Version <= MaxVersion
```

### Type Invariants (Always Run These)
```tla
TypeOK ==
  /\ committed \in [Targets -> [Chunks -> Nat]]
  /\ pending   \in [Targets -> [Chunks -> Nat \union {NULL}]]
  /\ state     \in [Targets -> {SERVING, OFFLINE, SYNCING, WAITING, LASTSERV}]
  /\ chainVersion \in Nat
```

### Common Pitfalls
1. **Symmetry explosion** — Use CONSTANTS with small sets (2-3 targets, 2 chunks) first
2. **Unconstrained Next** — Ensure Next is always enabled in reachable states
3. **Missing type invariants** — TypeOK catches trivial errors before property checking
4. **Too few fault injection points** — Use non-deterministic FailTarget at every step
5. **Over-abstraction** — Keep enough state to distinguish real bugs from modeling artifacts

## Mapping Code to TLA+

| Code Concept | TLA+ Representation |
|-------------|---------------------|
| `Mutex<HashMap>` lock | Atomic action with precondition (lock free) |
| Async RPC call | Action that may or may not fire (Next disjunction) |
| Timeout | Action with fairness constraint |
| Heartbeat failure | `FailTarget` action enabled non-deterministically |
| Chain reconfiguration | Action that increments `chainVersion` and reorders members |
| Idempotent retry | Action that checks precondition `pending = None` before writing |
