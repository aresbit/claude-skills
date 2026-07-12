# HarmonyOS SA API Reference

## SystemAbility Base Class

All system abilities inherit from `SystemAbility` and implement a domain-specific interface.

```cpp
class LocationService : public SystemAbility, public ILocationService {
    DECLARE_SYSTEM_ABILITY(LocationService)
public:
    void OnStart() override {
        Publish(this);  // Register with SAMgr
        // ... init logic
    }
    void OnStop() override {
        // ... cleanup logic
    }
    double GetLocation() override { return 116.397128; }
};
```

### Key Virtual Methods

| Method | Purpose |
|--------|---------|
| `OnStart()` | Called when SA starts; must call `Publish(this)` |
| `OnStop()` | Called when SA is reclaimed; cleanup resources |
| `OnAddSystemAbility(int32_t systemAbilityId, const std::string& deviceId)` | Called when a dependent SA registers |
| `OnRemoveSystemAbility(int32_t systemAbilityId, const std::string& deviceId)` | Called when a dependent SA goes away |
| `OnDump()` | Debug dump support |

## Registration Macros

### Header Macro (in .h file)
```cpp
DECLARE_SYSTEM_ABILITY(ClassName)
```
Declares SA metadata. Must appear inside the class definition.

### Implementation Macro (in .cpp file)
```cpp
REGISTER_SYSTEM_ABILITY_BY_ID(ClassName, SA_ID, runOnCreate)
```
Parameters:
- `ClassName` — the SA class name
- `SA_ID` — unique numeric SA identifier
- `runOnCreate` — `true` for permanent (boot-time) services; `false` for on-demand

Example:
```cpp
REGISTER_SYSTEM_ABILITY_BY_ID(LocationService, LOCATION_SERVICE_ID, true);
```

## SAMgr Client API

### Obtaining the SAMgr Client
```cpp
sptr<ISystemAbilityManager> samgr =
    SystemAbilityManagerClient::GetInstance().GetSystemAbilityManager();
```

### Core Operations

#### AddSystemAbility
```cpp
// Register a new SA
int32_t result = samgr->AddSystemAbility(saId, new TestAbility());

// Register as distributed SA
ISystemAbilityManager::SAExtraProp saExtra;
saExtra.isDistributed = true;
saExtra.capability = "test_capability";
int32_t result = samgr->AddSystemAbility(saId, new TestAbility(), saExtra);
```

#### GetSystemAbility
```cpp
// Obtain SA proxy by ID
sptr<IRemoteObject> remoteObject = samgr->GetSystemAbility(saId);

// Obtain SA proxy from specific device
sptr<IRemoteObject> remoteObject = samgr->GetSystemAbility(saId, deviceId);
```

#### CheckSystemAbility
```cpp
// Check if SA is registered
sptr<IRemoteObject> result = samgr->CheckSystemAbility(saId);
```

#### LoadSystemAbility (On-Demand)
```cpp
class MyLoadCallback : public SystemAbilityLoadCallbackStub {
    void OnLoadSystemAbilitySuccess(int32_t systemAbilityId,
                                     const sptr<IRemoteObject>& remoteObject) override {
        // SA loaded successfully
    }
    void OnLoadSystemAbilityFail(int32_t systemAbilityId) override {
        // SA failed to load
    }
};

sptr<MyLoadCallback> callback = new MyLoadCallback();
int32_t result = samgr->LoadSystemAbility(saId, callback);
```

#### RemoveSystemAbility
```cpp
int32_t result = samgr->RemoveSystemAbility(saId);
```

#### Subscribe/Unsubscribe
```cpp
// Listen for SA registration
int32_t result = samgr->SubscribeSystemAbility(saId, listener);

// Stop listening
int32_t result = samgr->UnSubscribeSystemAbility(saId, listener);
```

## Proxy/Stub Pattern

### Interface Definition (IRemoteBroker)
```cpp
class ILocator : public IRemoteBroker {
public:
    DECLARE_INTERFACE_DESCRIPTOR(u"LocatorInterface");
    enum {
        GET_LOCATION = 0,
    };
    virtual double GetLocation() = 0;
};
```

### Stub (Server Side)
```cpp
class LocatorStub : public IRemoteStub<ILocator> {
public:
    int OnRemoteRequest(uint32_t code, MessageParcel& data,
                        MessageParcel& reply, MessageOption& option) override {
        switch (code) {
            case GET_LOCATION: {
                double result = GetLocation();
                reply.WriteDouble(result);
                return ERR_NONE;
            }
            default:
                return IPCObjectStub::OnRemoteRequest(code, data, reply, option);
        }
    }
};
```

### Proxy (Client Side)
```cpp
class LocatorProxy : public IRemoteProxy<ILocator> {
public:
    double GetLocation() override {
        MessageParcel data, reply;
        MessageOption option;
        data.WriteInterfaceToken(ILocator::GetDescriptor());
        Remote()->SendRequest(GetDescriptor(), GET_LOCATION, data, reply, option);
        return reply.ReadDouble();
    }
};
```

### Client Usage Pattern
```cpp
// 1. Get SA proxy from SAMgr
sptr<IRemoteObject> object =
    SystemAbilityManagerClient::GetInstance()
        .GetSystemAbility(LOCATION_SERVICE_ID);

// 2. Cast to typed interface
sptr<ILocator> proxy = iface_cast<ILocator>(object);

// 3. Call methods via IPC
double lng = proxy->GetLocation();
```

## Death Notification

### Register Death Callback
```cpp
class MyDeathRecipient : public IRemoteObject::DeathRecipient {
    void OnRemoteDied(const wptr<IRemoteObject>& object) override {
        // Handle SA death — rebind or cleanup
    }
};

sptr<MyDeathRecipient> deathRecipient = new MyDeathRecipient();
proxy->AsObject()->AddDeathRecipient(deathRecipient);
```

### Unregister
```cpp
proxy->AsObject()->RemoveDeathRecipient(deathRecipient);
```

**Constraint**: Anonymous Stub objects (not registered with SAMgr) cannot subscribe to death notifications in RPC.

## Data Transfer Limits

- **IPC (local)**: Max ~1MB (V5+), ~200KB (older versions). For larger data, use anonymous shared memory (`Ashmem`).
- **RPC (cross-device)**: Subject to DSoftBus bandwidth limitations.

## Common Error Codes

| Code | Meaning |
|------|---------|
| `ERR_NONE` (0) | Success |
| `ERR_PERMISSION_DENIED` | Permission check failed |
| `ERR_INVALID_VALUE` | Invalid parameter |
| `ERR_DEAD_OBJECT` | Target SA process has died |

## Relevant Official Docs

| Doc | Slug |
|-----|------|
| IPC Kit V13 Overview | `ipc-rpc-overview` |
| IPC RPC V2 Overview (archived) | `ipc-rpc-overview-0000001427584740-V2` |

Fetch these via:
```bash
python3 scripts/fetch_sa_docs.py --preset ipc
```
