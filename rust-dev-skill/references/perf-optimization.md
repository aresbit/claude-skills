# Rust Performance Optimization — AI-Assisted Loop

Based on the 12x throughput improvement (23K → 300K ops/sec) achieved in a multi-Paxos implementation through systematic AI-assisted optimization.

## The Loop

```
┌──────────────┐
│ 1. Instrument │  ← Add tracing spans to all hot paths
└──────┬───────┘
       ▼
┌──────────────┐
│ 2. Measure    │  ← Run benchmarks, collect traces
└──────┬───────┘
       ▼
┌──────────────┐
│ 3. Analyze    │  ← AI writes analysis scripts
└──────┬───────┘
       ▼
┌──────────────┐
│ 4. Optimize   │  ← Apply ONE optimization
└──────┬───────┘
       │
       └──────────→ back to 2
```

## Step 1: Instrument

### Prompt
```
Add tracing instrumentation to all public methods and internal code paths
in this module. Use the `tracing` crate. Each span should include:
- Function name
- Key parameters (slot number, ballot, etc.)
- Return value summary

Use `#[tracing::instrument]` where possible; manual spans for complex paths.
```

### Cargo.toml
```toml
[dependencies]
tracing = "0.1"
tracing-subscriber = { version = "0.3", features = ["json"] }
```

### Pattern
```rust
#[tracing::instrument(skip(self), fields(slot = msg.slot, ballot = msg.ballot))]
fn process_2a(&mut self, msg: Phase2aMessage) -> Result<()> {
    // ...
}
```

## Step 2: Measure

```bash
# Run with JSON tracing for analysis
RUST_LOG=trace cargo bench --bench paxos_bench -- --output-format json > trace.json
```

## Step 3: Analyze

### Prompt
```
Analyze this trace JSON. Write a Python script that:
1. Calculates p50, p95, p99 latency per operation type
2. Identifies the top 5 bottlenecks by cumulative time
3. Shows the call-path contribution (self-time vs children)
4. Outputs a ranked list of optimization targets

Trace file: trace.json
```

### Analysis Script Pattern
```python
import json
import numpy as np

def analyze_trace(trace_path):
    spans = []
    with open(trace_path) as f:
        for line in f:
            spans.append(json.loads(line))

    # Group by span name, calculate quantiles
    by_name = {}
    for s in spans:
        dur = s['duration_ms']
        by_name.setdefault(s['name'], []).append(dur)

    for name, durs in sorted(by_name.items(),
                             key=lambda x: sum(x[1]), reverse=True):
        arr = np.array(durs)
        print(f"{name}: total={sum(durs):.1f}ms, "
              f"p50={np.percentile(arr,50):.1f}ms, "
              f"p99={np.percentile(arr,99):.1f}ms")
```

## Step 4: Optimize — Rust-Specific Targets

Apply ONE optimization at a time, re-measure after each.

### Priority Order

**1. Minimize Allocations** (highest impact)
```rust
// BEFORE: allocates on every call
fn process(&self, data: &[u8]) -> Result<()> {
    let owned = data.to_vec(); // allocation
    // ...
}

// AFTER: borrow when possible
fn process(&self, data: &[u8]) -> Result<()> {
    // work directly with the slice
}
```

**2. Zero-Copy Deserialization**
```rust
// Use Bytes instead of Vec<u8> for shared buffers
use bytes::Bytes;

// Use Cow for optionally-owned data
use std::borrow::Cow;
```

**3. Lock Contention**
```rust
// BEFORE: single lock, high contention
use std::sync::Mutex;
struct State { data: Mutex<HashMap<u64, Entry>> }

// AFTER: sharded locks
use parking_lot::RwLock;
struct State { shards: Vec<RwLock<HashMap<u64, Entry>>> }

fn shard_for(&self, key: u64) -> &RwLock<HashMap<u64, Entry>> {
    &self.shards[key as usize % self.shards.len()]
}
```

**4. Remove Unnecessary Async**
```rust
// BEFORE: spawn for trivial work
tokio::spawn(async move { state.inc_counter() });

// AFTER: inline if work is trivial
state.inc_counter();
```

**5. Batch Operations**
```rust
// BEFORE: one syscall per message
for msg in batch {
    socket.send(msg)?;
}

// AFTER: gather and send once
let combined = batch.iter().flat_map(|m| m.serialize()).collect::<Vec<_>>();
socket.send(&combined)?;
```

## Optimization Prompt Template

```
Current throughput: <N> ops/sec on <hardware spec>

The trace shows these bottlenecks:
1. <bottleneck 1> — <p99 latency>
2. <bottleneck 2> — <p99 latency>

Propose 3 specific Rust optimizations to address the top bottleneck.
For each: estimate the expected improvement and explain the Rust-specific
mechanism (e.g., avoiding Clone, using Cow, lock sharding, etc.).

Implement only one at my direction; we'll re-measure after each.
```

## Throughput Tracking

Keep a running log:

| Change | Throughput | Delta | Mechanism |
|--------|-----------|-------|-----------|
| Baseline | 23K | - | - |
| Arena allocator | 45K | +96% | Reduce alloc |
| Sharded locks | 78K | +73% | Contention |
| Zero-copy deser | 120K | +54% | Borrow |
| Remove spawn | 180K | +50% | Async overhead |
| Batch writes | 300K | +67% | Syscall amortization |
