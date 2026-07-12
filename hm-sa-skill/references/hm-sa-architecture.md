# HarmonyOS SAMgr Architecture

## Overview

SAMgr (System Ability Manager) is the daemon-level service registry and lifecycle manager for all system services in HarmonyOS/OpenHarmony. It plays a role analogous to Android's `servicemanager` + `init` daemon, but with significantly stronger lifecycle governance and native cross-device distributed support.

## Core Roles

SAMgr = **Service Registry** + **Lifecycle Manager** + **IPC Router** + **Capability Scheduler**

| Role | Description |
|------|-------------|
| Service Registry | Central registration table for all SAs (System Abilities); each SA gets a unique ID |
| Lifecycle Manager | Controls OnStart/OnStop, monitors process health, auto-restarts on crash |
| IPC Router | Routes local IPC (Binder driver) and cross-device RPC (DSoftBus) transparently |
| Capability Scheduler | Enforces boot sequence ordering, priority, and on-demand lazy loading |

## Boot Sequence

```
Kernel → init process → mount partitions → parse init .cfg scripts
                                              ↓
                                    SAMgr (SA service registry, started via foundation.cfg)
                                              ↓
                                    foundation (user program mgmt framework)
                                    safwk ≈ system_server; samgr ≈ servicemanager
                                              ↓
                                    appspawn (application spawner)
                                              ↓
                                    Application processes
```

Key points:
- SAMgr is started by `init` via `.cfg` configuration files (e.g., `foundation.cfg`)
- `safwk` acts as the system_server equivalent; `samgr` acts as the servicemanager equivalent
- All SAs must register with SAMgr at startup
- Each SA is assigned a unique numeric ID (e.g., 3001 for PowerManager, 3002 for LocationService, 3400 for BundleMgrService)

## SA Lifecycle

### Five Stages

```
Register → Publish → Discovery → IPC Invocation → System-Controlled Reclamation
```

1. **Register**: SA starts, calls `AddSystemAbility()` to register with SAMgr
2. **Publish**: SA calls `Publish(this)` in `OnStart()` to expose itself
3. **Discovery**: Client calls `GetSystemAbility(ID)` to obtain proxy
4. **IPC Invocation**: Client invokes methods on the proxy; SAMgr routes to the Stub
5. **Reclamation**: System can unilaterally reclaim services (system-driven, not app-driven)

### Lifecycle Callbacks

- `OnStart()` — Called when SA is started; must call `Publish(this)` and perform initialization
- `OnStop()` — Called when SA is being reclaimed; must clean up resources
- `OnAddSystemAbility(id)` — Notified when a dependent SA registers
- `OnRemoveSystemAbility(id)` — Notified when a dependent SA goes away

## Key Internal Data Structures

From `system_ability_manager.h` source analysis:

| Field | Type | Purpose |
|-------|------|---------|
| `abilityMap_` | `map<int32_t, SAInfo>` | Loaded SA ID → proxy object mapping |
| `listenerMap_` | `map<int32_t, Listener>` | SA ID → listener callback mapping |
| `onDemandAbilityMap_` | `map<int32_t, string>` | SA ID → process name for lazy-loaded SAs |
| `startingAbilityMap_` | `map<int32_t, bool>` | In-flight startup tracking to prevent double-start |
| `systemProcessMap_` | `map<string, LocalAbilityManager>` | Process name → per-process SA manager |
| `saProfileMap_` | `map<int32_t, SAProfile>` | SA configuration metadata (runOnCreate, distributed, etc.) |
| `saFrequencyMap_` | `map<int32_t, int>` | SA access frequency for optimization decisions |
| `abilityDeath_` | `DeathRecipient` | Callback when a registered SA process dies |
| `systemProcessDeath_` | `DeathRecipient` | Callback when an entire process hosting multiple SAs dies |

## Service Registration Modes

### 1. Permanent (RunOnCreate)
- Service marked with `runOnCreate: true` in `.cfg`
- Started automatically at boot
- Must complete startup before boot sequence proceeds
- Example: Logging, BundleMgr, InputManager

### 2. On-Demand (Lazy Loading)
- Service marked with `"ondemand": true` in `.cfg`
- NOT started at boot
- Loaded when first `GetSystemAbility()` or `LoadSystemAbility()` is called
- Process name in `.cfg` must match the SA's `.json` configuration
- Callback via `SystemAbilityLoadCallbackStub` to notify success/failure

### 3. Crash Auto-Restart
- SAMgr monitors Binder death notifications
- On detecting SA process death:
  1. Detects process death
  2. Automatically restarts the service
  3. Notifies bound clients to re-establish proxy connections
- Makes failures nearly invisible to applications

## Boot Sequence Governance

SAMgr enforces dependency-ordered startup:
1. Logging services — must start before all others
2. BundleMgr — must precede UI services
3. InputManager — must be the earliest-ready input service
4. Other services — launched according to dependency graph

## Distributed Cross-Device Support

- **Local IPC**: Uses Binder driver (≤1MB per message for newer versions, ≤200KB for older; excess data should use anonymous shared memory)
- **Cross-device RPC**: Uses DSoftBus (soft bus driver)
- SAMgr transparently routes to the correct transport based on SA location
- `SAExtraProp.isDistributed = true` marks an SA as distributed
- Cross-device Proxy objects cannot be re-proxied or passed back to origin device

## Android ServiceManager Comparison

| Dimension | Android | HarmonyOS |
|-----------|---------|-----------|
| Service Management | Dispersed (app-driven) | Unified (system-driven) |
| Lifecycle | App-controlled | System-controlled |
| Cross-device | None built-in | Natively supported |
| Scheduling | Weak | Strong (boot ordering, priority, on-demand) |
| Crash Recovery | Limited | Automatic restart + client notification |
| Service Registration | `addService()` via Binder | `AddSystemAbility()` via SAMgr |

## Implementation Philosophy

HarmonyOS SAs form a "lightweight microservice framework" within the OS:
- Central registry (SAMgr)
- Proxy/stub pattern for communication
- Lifecycle management with health checks
- Scheduling policies with priority and on-demand loading
- Cross-device service discovery transparent to callers
