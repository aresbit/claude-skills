# HarmonyOS SAMgr Source Code Structure

## Repository

- **OpenHarmony Official**: https://gitcode.com/openharmony/systemabilitymgr_samgr
- **Gitee Mirror**: https://gitee.com/openharmony/systemabilitymgr_samgr
- **License**: Apache-2.0

## Subsystem Location

Within the OpenHarmony source tree:
```
/foundation/systemabilitymgr/
├── samgr/          # System Ability Manager (main)
├── safwk/          # System Ability Framework
├── safwk_lite/     # Lightweight SA Framework (IoT)
└── samgr_lite/     # Lightweight SAMgr (IoT)
```

## samgr Directory Structure

```
/foundation/systemabilitymgr/samgr/
├── bundle.json              # Build descriptor and metadata (GN)
├── config.gni               # GN build configuration variables
├── Cargo.toml               # Rust component build support
├── rustfmt.toml             # Rust formatting rules
├── README.md / README_zh.md # Project documentation
├── LICENSE                  # Apache-2.0
├── OAT.xml                  # Open source audit tool config
├── cfi_blocklist.txt        # CFI blocklist for sanitizers
│
├── services/                # SAMgr daemon service implementation
│   └── samgr/
│       └── native/
│           └── source/      # Core C++ service code
│               ├── system_ability_manager.cpp
│               └── system_ability_manager.h
│
├── frameworks/              # Framework implementation
│   └── native/
│       └── source/          # Client-side framework code
│           ├── system_ability_manager_client.cpp
│           └── system_ability_manager_proxy.cpp
│
├── interfaces/              # Public API headers
│   └── innerkits/
│       └── native/
│           └── include/
│               ├── isystem_ability_manager.h
│               ├── system_ability.h
│               ├── system_ability_manager_client.h
│               └── system_ability_load_callback_stub.h
│
├── utils/                   # Utility libraries
│   └── native/
│       └── source/
│
├── test/                    # Unit and integration tests
│   ├── unittest/
│   └── fuzztest/
│
├── etc/                     # Configuration files
│   └── permissions/
│
└── figures/                 # Architecture diagrams (PNG/SVG)
    └── architecture.png
```

## Key Classes

| Class | Location | Role |
|-------|----------|------|
| `SystemAbility` | `interfaces/innerkits/native/include/` | Base class for all SAs; provides OnStart/OnStop/Publish |
| `ISystemAbilityManager` | `interfaces/innerkits/native/include/` | Interface for SAMgr operations (Add, Get, Check, Load) |
| `SystemAbilityManagerClient` | `interfaces/innerkits/native/include/` | Singleton entry point for obtaining SAMgr proxy |
| `SystemAbilityLoadCallbackStub` | `interfaces/innerkits/native/include/` | Base class for on-demand load callbacks |
| `SystemAbilityManager` | `services/samgr/native/source/` | Server-side implementation of SAMgr daemon |

## Key Configuration Files

### bundle.json
GN build descriptor defining the subsystem, components, and build targets.

### config.gni
GN variables including multi-instance SA configuration flags.

### etc/permissions/
Permission configuration files for SA access control.

## Build System

The primary build uses the OpenHarmony GN (Generate Ninja) system:
- `bundle.json` defines the component
- `config.gni` provides build variables
- Individual `BUILD.gn` files in each directory define targets
- Rust components use `Cargo.toml` / `cargo build`

## SA Configuration (.cfg files)

SA startup is controlled by `.cfg` files parsed by `init`:
```
{
    "services": [
        {
            "name": "samgr",
            "path": "/system/bin/samgr",
            "runOnCreate": true
        },
        {
            "name": "location_service",
            "path": "/system/bin/location_sa",
            "runOnCreate": false,
            "ondemand": true
        }
    ]
}
```

Key fields:
- `runOnCreate`: `true` = boot-time permanent service
- `ondemand`: `true` = lazy-load when first accessed
- `path`: executable path
- Process name in `.cfg` must match SA `.json` config

## Related OpenHarmony Subsystems

| Subsystem | Path | Relationship |
|-----------|------|--------------|
| `communication_ipc` | `foundation/communication/ipc` | IPC/RPC transport layer used by SAMgr |
| `ability_ability_runtime` | `foundation/ability/ability_runtime` | App process management; calls SAMgr for SA lookup |
| `distributeddatamgr` | `foundation/distributeddatamgr` | Distributed data; relies on SAMgr cross-device routing |
| `startup_init` | `base/startup/init` | init process that starts SAMgr daemon |
