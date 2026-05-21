# NAPI API Reference

Full Node-API symbol reference for HarmonyOS, based on the official
[Node-API reference](https://developer.huawei.com/consumer/cn/doc/harmonyos-references/napi).

## Module & Lifecycle

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_module_register` | Register native module | 10 |
| `napi_open_handle_scope` | Create handle scope context | 10 |
| `napi_close_handle_scope` | Close handle scope, release all refs | 10 |
| `napi_open_escapable_handle_scope` | Create escapable scope (promote values to parent) | 10 |
| `napi_close_escapable_handle_scope` | Close escapable scope | 10 |
| `napi_escape_handle` | Promote JS object to parent scope | 10 |
| `napi_create_reference` | Create ref to extend object lifetime | 10 |
| `napi_delete_reference` | Delete ref | 10 |
| `napi_reference_ref` | Increment ref count | 10 |
| `napi_reference_unref` | Decrement ref count | 10 |
| `napi_get_reference_value` | Get JS object from ref | 10 |
| `napi_add_env_cleanup_hook` | Register env cleanup hook | 11 |
| `napi_remove_env_cleanup_hook` | Unregister cleanup hook | 11 |
| `napi_add_async_cleanup_hook` | Register async cleanup hook | 11 |
| `napi_remove_async_cleanup_hook` | Unregister async cleanup hook | 11 |
| `napi_set_instance_data` | Bind data to current env | 11 |
| `napi_get_instance_data` | Retrieve env-bound data | 11 |
| `napi_add_finalizer` | Register GC finalizer callback | 11 |

## Value Creation

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_create_array` | Create JS Array | 10 |
| `napi_create_array_with_length` | Create JS Array with length | 10 |
| `napi_create_arraybuffer` | Create ArrayBuffer (returns `void** data`) | 10 |
| `napi_create_buffer` | Create ArrayBufferLike (max 2MB) | 10 |
| `napi_create_buffer_copy` | Create buffer with initial data copy | 10 |
| `napi_create_external_buffer` | Create buffer wrapping external memory | 10 |
| `napi_create_external` | Create JS value with external data | 10 |
| `napi_create_external_arraybuffer` | Create ArrayBuffer with external data | 10 |
| `napi_create_object` | Create default JS Object | 10 |
| `napi_create_symbol` | Create JS Symbol | 10 |
| `napi_create_typedarray` | Create TypedArray from ArrayBuffer | 10 |
| `napi_create_dataview` | Create DataView from ArrayBuffer | 10 |
| `napi_create_int32` | int32_t → JS Number | 10 |
| `napi_create_uint32` | uint32_t → JS Number | 10 |
| `napi_create_int64` | int64_t → JS Number | 10 |
| `napi_create_double` | double → JS Number | 10 |
| `napi_create_string_latin1` | ISO-8859-1 C string → JS String | 10 |
| `napi_create_string_utf8` | UTF-8 C string → JS String | 10 |
| `napi_create_string_utf16` | UTF-16 C string → JS String | 10 |
| `napi_create_function` | Create native function for JS call | 10 |
| `napi_create_date` | double → JS Date | 10 |
| `napi_create_bigint_int64` | int64_t → JS BigInt | 10 |
| `napi_create_bigint_uint64` | uint64_t → JS BigInt | 10 |
| `napi_create_bigint_words` | uint64 array → JS BigInt | 10 |

## Value Access

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_get_array_length` | Get array length | 10 |
| `napi_get_arraybuffer_info` | Get ArrayBuffer data ptr & byte_length | 10 |
| `napi_get_buffer_info` | Get Buffer data ptr & length | 10 |
| `napi_get_typedarray_info` | Get TypedArray props (note: length = bytes, not elements in HM) | 10 |
| `napi_get_dataview_info` | Get DataView props | 10 |
| `napi_get_value_bool` | JS Boolean → C bool | 10 |
| `napi_get_value_double` | JS Number → C double | 10 |
| `napi_get_value_int32` | JS Number → C int32_t | 10 |
| `napi_get_value_int64` | JS Number → C int64_t | 10 |
| `napi_get_value_uint32` | JS Number → C uint32_t | 10 |
| `napi_get_value_string_latin1` | JS String → ISO-8859-1 | 10 |
| `napi_get_value_string_utf8` | JS String → UTF-8 | 10 |
| `napi_get_value_string_utf16` | JS String → UTF-16 | 10 |
| `napi_get_value_external` | Get external data pointer | 10 |
| `napi_get_value_bigint_int64` | JS BigInt → int64_t | 10 |
| `napi_get_value_bigint_uint64` | JS BigInt → uint64_t | 10 |
| `napi_get_value_bigint_words` | JS BigInt → words | 10 |
| `napi_get_date_value` | JS Date → C double | 10 |
| `napi_get_cb_info` | Get callback info (args, this, data) | 10 |

## Constants

| Symbol | Description |
|--------|-------------|
| `napi_get_boolean` | Get JS true/false singleton |
| `napi_get_global` | Get global object |
| `napi_get_null` | Get null singleton |
| `napi_get_undefined` | Get undefined singleton |

## Object Operations

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_get_prototype` | Get prototype | 10 |
| `napi_set_property` | Set property by napi_value key | 10 |
| `napi_get_property` | Get property by napi_value key | 10 |
| `napi_has_property` | Check property existence | 10 |
| `napi_delete_property` | Delete property | 10 |
| `napi_has_own_property` | Check own property | 10 |
| `napi_set_named_property` | Set property by C string name | 10 |
| `napi_get_named_property` | Get property by C string name | 10 |
| `napi_has_named_property` | Has property by C string name | 10 |
| `napi_set_element` | Set array element at index | 10 |
| `napi_get_element` | Get array element at index | 10 |
| `napi_has_element` | Check element at index | 10 |
| `napi_delete_element` | Delete element at index | 10 |
| `napi_define_properties` | Batch define properties | 10 |
| `napi_get_property_names` | Get enumerable property names | 10 |
| `napi_get_all_property_names` | Get filtered property names | 10 |
| `napi_object_freeze` | Freeze object | 10 |
| `napi_object_seal` | Seal object | 10 |

## Type Checking

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_typeof` | Get JS type of value | 10 |
| `napi_instanceof` | Check constructor instance | 10 |
| `napi_is_array` | Check if array | 10 |
| `napi_is_arraybuffer` | Check if ArrayBuffer | 10 |
| `napi_is_buffer` | Check if Buffer | 10 |
| `napi_is_typedarray` | Check if TypedArray | 10 |
| `napi_is_dataview` | Check if DataView | 10 |
| `napi_is_date` | Check if Date | 10 |
| `napi_is_error` | Check if Error | 10 |
| `napi_is_promise` | Check if Promise | 10 |
| `napi_is_detached_arraybuffer` | Check if detached | 10 |
| `napi_strict_equals` | Strict equality check | 10 |

## Coercion

| Symbol | Description |
|--------|-------------|
| `napi_coerce_to_bool` | Coerce to Boolean |
| `napi_coerce_to_number` | Coerce to Number |
| `napi_coerce_to_object` | Coerce to Object |
| `napi_coerce_to_string` | Coerce to String |

## Error Handling

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_throw` | Throw JS value | 10 |
| `napi_throw_error` | Throw Error with text | 10 |
| `napi_throw_type_error` | Throw TypeError | 10 |
| `napi_throw_range_error` | Throw RangeError | 10 |
| `napi_throw_business_error` | Throw Error with numeric code | 23 |
| `napi_create_error` | Create Error object | 10 |
| `napi_create_type_error` | Create TypeError object | 10 |
| `napi_create_range_error` | Create RangeError object | 10 |
| `napi_get_last_error_info` | Get last error info | 10 |
| `napi_get_and_clear_last_exception` | Get+clear last exception | 10 |
| `napi_is_exception_pending` | Check if exception pending | 10 |
| `napi_fatal_error` | Raise fatal error, terminate | 10 |
| `napi_fatal_exception` | Throw UncaughtException | 12 |

## Async Work

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_create_async_work` | Create async work object | 10 |
| `napi_delete_async_work` | Delete async work object | 10 |
| `napi_queue_async_work` | Enqueue async work | 10 |
| `napi_queue_async_work_with_qos` | Enqueue with QoS priority | 10 |
| `napi_cancel_async_work` | Cancel queued async work | 10 |

## Promise

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_create_promise` | Create deferred + promise | 10 |
| `napi_resolve_deferred` | Resolve promise | 10 |
| `napi_reject_deferred` | Reject promise | 10 |
| `napi_is_promise` | Check if value is Promise | 10 |

## Async Context (async_hooks unsupported in HM)

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_async_init` | Create async context (no async_hooks) | 11 |
| `napi_make_callback` | Call JS in async context | 11 |
| `napi_async_destroy` | Destroy async context | 11 |
| `napi_open_callback_scope` | Open callback scope | 11 |
| `napi_close_callback_scope` | Close callback scope | 11 |

## Thread-Safe Functions

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_create_threadsafe_function` | Create TSFN (thread_count max 128) | 10 |
| `napi_get_threadsafe_function_context` | Get TSFN context | 10 |
| `napi_call_threadsafe_function` | Call TSFN from any thread | 10 |
| `napi_call_threadsafe_function_with_priority` | Call TSFN with priority | 12 |
| `napi_acquire_threadsafe_function` | Indicate TSFN in use | 10 |
| `napi_release_threadsafe_function` | Release TSFN | 10 |
| `napi_ref_threadsafe_function` | Prevent event loop exit | 10 |
| `napi_unref_threadsafe_function` | Allow event loop exit | 10 |

## Class / Object Binding

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_define_class` | Define JS class from C++ class | 10 |
| `napi_wrap` | Bind native object to JS object | 10 |
| `napi_unwrap` | Get native object from JS object | 10 |
| `napi_remove_wrap` | Remove binding, get native object | 10 |
| `napi_type_tag_object` | Associate tag with object | 10 |
| `napi_check_object_type_tag` | Check tag association | 10 |
| `napi_call_function` | Call JS function from native | 10 |
| `napi_new_instance` | Construct instance | 10 |
| `napi_get_new_target` | Get new.target | 10 |

## Runtime & Engine

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_get_uv_event_loop` | Get libuv loop instance | 10 |
| `napi_get_node_version` | Get node version (empty impl in HM) | 10 |
| `napi_get_version` | Get max supported N-API version | 10 |
| `node_api_get_module_file_name` | Get loading module's absolute path | 11 |
| `napi_run_script` | Run JS code (empty impl, use napi_run_script_path) | 10 |

## HarmonyOS Extensions (non-standard)

| Symbol | Description | API |
|--------|-------------|-----|
| `napi_queue_async_work_with_qos` | QoS async scheduling | 10 |
| `napi_run_script_path` | Run .abc file | 10 |
| `napi_load_module` | Load .abc as module | 11 |
| `napi_load_module_with_info` | Load module in standalone runtime | 12 |
| `napi_create_object_with_properties` | Create object from descriptor array | 11 |
| `napi_create_object_with_named_properties` | Create object from named values | 11 |
| `napi_coerce_to_native_binding_object` | Cross-thread native binding | 11 |
| `napi_create_ark_runtime` | Create standalone ArkTS runtime | 12 |
| `napi_destroy_ark_runtime` | Destroy standalone runtime | 12 |
| `napi_run_event_loop` | Trigger event loop | 12 |
| `napi_stop_event_loop` | Stop event loop | 12 |
| `napi_serialize` | ArkTS object → native data | 12 |
| `napi_deserialize` | Native data → ArkTS object | 12 |
| `napi_delete_serialization_data` | Free serialization data | 12 |
| `napi_call_threadsafe_function_with_priority` | TSFN with priority | 12 |
| `napi_is_sendable` | Check if Sendable | 12 |
| `napi_define_sendable_class` | Create Sendable class | 12 |
| `napi_create_sendable_object_with_properties` | Create Sendable object | 12 |
| `napi_create_sendable_array` | Create Sendable array | 12 |
| `napi_create_sendable_array_with_length` | Create sized Sendable array | 12 |
| `napi_create_sendable_arraybuffer` | Create Sendable ArrayBuffer | 12 |
| `napi_create_sendable_typedarray` | Create Sendable TypedArray | 12 |
| `napi_wrap_sendable` | Wrap native in Sendable | 12 |
| `napi_wrap_sendable_with_size` | Wrap native with size tracking | 12 |
| `napi_unwrap_sendable` | Unwrap Sendable native | 12 |
| `napi_remove_wrap_sendable` | Remove Sendable wrap | 12 |
| `napi_wrap_enhance` | Wrap with GC-size-tracking, optional async finalize | 18 |
| `napi_create_ark_context` | Create runtime context | 20 |
| `napi_switch_ark_context` | Switch runtime context | 20 |
| `napi_destroy_ark_context` | Destroy runtime context | 20 |
| `napi_open_critical_scope` | Open critical scope | 21 |
| `napi_close_critical_scope` | Close critical scope | 21 |
| `napi_get_buffer_string_utf16_in_critical_scope` | Get UTF-16 buffer in critical scope | 21 |
| `napi_create_strong_reference` | Create strong ArkTS ref | 21 |
| `napi_delete_strong_reference` | Delete strong ref | 21 |
| `napi_get_strong_reference_value` | Get value from strong ref | 21 |
| `napi_create_external_string_utf16` | Zero-copy UTF-16 string | 22 |
| `napi_create_external_string_ascii` | Zero-copy ASCII string | 22 |
| `napi_create_strong_sendable_reference` | Strong Sendable ref | 22 |
| `napi_delete_strong_sendable_reference` | Delete strong Sendable ref | 22 |
| `napi_get_strong_sendable_reference_value` | Get value from strong Sendable ref | 22 |
| `napi_throw_business_error` | Throw Error with numeric code | 23 |

## napi_qos_t Enum

```cpp
typedef enum {
    napi_qos_background = 0,      // invisible tasks: sync, backup
    napi_qos_utility = 1,         // no immediate response needed: download, import
    napi_qos_default = 2,         // default
    napi_qos_user_initiated = 3,  // user-triggered with visible progress
} napi_qos_t;
```

## napi_event_mode Enum

```cpp
typedef enum {
    napi_event_mode_default = 0,  // blocking loop until empty
    napi_event_mode_nowait = 1,   // non-blocking, process one task then exit
} napi_event_mode;
```

## HM vs Standard Node-API Differences (key items)

- **napi_throw_error/type_error/range_error**: HM allows code=null, standard returns napi_invalid_arg
- **napi_create_type_error/range_error**: HM creates Error type, standard creates TypeError/RangeError
- **napi_create_reference**: HM accepts any value type, standard only Object/Function/Symbol
- **napi_get_typedarray_info**: HM `length` = bytes, standard = element count
- **napi_wrap**: HM returns strong ref when result non-null, standard returns weak ref
- **napi_delete_reference**: HM triggers finalize callback for strong refs, standard does not
- **napi_create_buffer**: HM max 2MB (2097152 bytes), type is ArrayBufferLike
- Buffer limit 2MB for `napi_create_buffer`, `napi_create_buffer_copy`, `napi_create_external_buffer`
