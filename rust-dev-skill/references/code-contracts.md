# Code Contracts for Rust — AI-Assisted Methodology

Distilled from 130K-line Paxos implementation where AI-generated contracts caught subtle safety violations before testing.

## Contract Structure

Every critical function gets three annotation types:

```rust
/// Precondition: <condition that must hold before call>
/// Postcondition: <condition guaranteed after successful return>
/// Invariant: <condition that always holds across the struct lifetime>
fn critical_method(&mut self, input: Message) -> Result<Output> { ... }
```

## Level 1: Writing Contracts with AI

### Prompt Template

```
Write code contracts (preconditions, postconditions, invariants) for the following
Rust function. Consider:
- All possible input states (None, empty, overflow, etc.)
- All possible internal state transitions
- Edge cases specific to this domain
- Invariants that must hold across the struct

Function:
<paste function signature and body>
```

### Review Checklist

When reviewing AI-generated contracts:
1. Are preconditions actually checkable at runtime?
2. Do postconditions cover all return paths (Ok and Err)?
3. Are invariants truly invariant, or do they have legitimate exceptions?
4. Does any contract duplicate Rust's type-system guarantees? Remove those.
5. Are contracts specific enough to catch real bugs?

### Runtime Enforcement

```rust
// In test/debug builds:
#[cfg(debug_assertions)]
macro_rules! contract {
    ($cond:expr, $msg:literal) => {
        if !$cond { panic!("Contract violation: {}", $msg); }
    };
}

// Usage:
fn process_2a(&mut self, msg: Phase2aMessage) -> Result<()> {
    contract!(msg.ballot > 0, "ballot_number must be positive");
    // ... implementation ...
    contract!(self.accepted[slot].is_some(), "accepted proposal must exist after process_2a");
    Ok(())
}
```

## Level 2: Generating Tests from Contracts

### Prompt Template

```
For each postcondition in the following contracts, generate a focused unit test
that verifies it. Cover:
- Happy path
- Each error path listed in the contract
- Boundary values (min, max, just above/below boundaries)

Contracts:
<paste contracts>
```

### Test Naming Convention

```rust
#[test]
fn test_process_2a_postcondition_accepted_proposal_exists() { ... }

#[test]
fn test_process_2a_precondition_ballot_positive_violation() { ... }
```

## Level 3: Property-Based Tests with proptest

### Setup

```toml
[dev-dependencies]
proptest = "1"
```

### Prompt Template

```
Translate these code contracts into proptest property-based tests.
Generate randomized inputs that explore the full state space.
Each contract violation should trigger a panic.

Contracts:
<paste contracts>
```

### Pattern

```rust
use proptest::prelude::*;

proptest! {
    #[test]
    fn prop_process_2a_accepts_valid_proposal(
        ballot in 1u64..1000,
        slot in 0u64..100,
        value in any::<Vec<u8>>()
    ) {
        let mut state = ReplicaState::new();
        let msg = Phase2aMessage { ballot, slot, value };
        let result = state.process_2a(msg);

        // Postcondition: if Ok, proposal must be stored
        if result.is_ok() {
            prop_assert!(state.accepted_proposals[slot as usize].is_some());
        }
    }
}
```

## Real-World Impact

From the Paxos project: one AI-generated contract caught a safety violation where `process_2a` could overwrite an already-accepted proposal with a different value under certain ballot conditions — a classic Paxos safety violation. The contract fired during property-based testing, preventing a replication consistency bug.

## Contract Density Guidelines

| Function Complexity | Typical Contract Count |
|---------------------|----------------------|
| Simple getter/setter | 1-2 |
| Validation logic | 3-5 |
| State machine transition | 5-10 |
| Consensus protocol handler | 10-20 |
