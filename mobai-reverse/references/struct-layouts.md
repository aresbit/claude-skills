# Go 运行时数据结构布局

从 IDA Pro 反编译 + PCLNTAB 符号表还原的完整结构体布局。

---

## license.Manager

**大小**: 推测 0x98+ 字节 (含内嵌字段)
**构造函数**: `mobai_internal_license.NewManager` @ `0x140F311C0`

```c
// 从 NewManager 初始化代码反推:
// 0x140F3137D: mov [rax+0x18], 4     ← tier 长度 (补丁 3)
// 各字段由 runtime.newobject 分配后的零值初始化 + 逐字段赋值

struct LicenseManager {
    // 嵌入/指针字段 (从 NewManager 的参数和赋值推断)
    SupabaseClient* supabaseClient;  // +0x00: supabase.Client (构造函数参数1)
    QuotaManager*   quotaManager;    // +0x08: quota.Manager (构造函数参数2)
    
    // Tier 信息
    uint8_t* tierPtr;                // +0x10: Go string.ptr → 指向 "free" 字符串
    int64_t  tierLen;                // +0x18: Go string.len → 初始化 4 (补丁 3→3)
    
    // 同步原语
    void*  rwMutex;                  // +0x20: sync.RWMutex
    
    // 事件系统
    EventEmitter* eventEmitter;      // +0x28: 前端事件推送
    
    // 认证信息
    void* authToken;                 // +0x30: JWT/access token
    int64_t isAuthenticated;          // +0x38: bool (0/1)
    
    // 用户信息
    uint8_t* userEmailPtr;           // +0x40: Go string.ptr
    int64_t  userEmailLen;           // +0x48: Go string.len
    
    // 上下文
    void* ctx;                       // +0x50: context.Context
    
    // 错误状态
    void* lastError;                 // +0x58
    
    // ... 可能还有更多字段
    // GetStatus 返回 8 个值 (Go ABI: 多个返回值编码在栈上)
};
```

### 关键方法

| 方法 | VA | 访问的字段 |
|------|-----|-----------|
| `GetTier()` | `0x140F31500` | 读 `+0x10` (tier ptr), `+0x18` (tier len) |
| `IsPro()` | `0x140F31620` | 调用 GetTier, 比较字符串 `"pro"` |
| `IsAuthenticated()` | `0x140F31640` | 读 `+0x38` (bool) |
| `GetUserEmail()` | `0x140F31660` | 读 `+0x40`, `+0x48` |
| `GetStatus()` | `0x140F35020` | 聚合调用, 组装返回 JSON |

### GetTier 反编译 (伪代码)
```c
// VA: 0x140F31500
GoString GetTier(LicenseManager* m) {
    m->rwMutex.RLock();              // +0x20
    GoString result;
    result.ptr = m->tierPtr;         // +0x10
    result.len = m->tierLen;         // +0x18
    m->rwMutex.RUnlock();
    return result;
}
```

### IsPro 反编译 (伪代码)
```c
// VA: 0x140F31620
bool IsPro(LicenseManager* m) {
    GoString tier = GetTier(m);
    // 直接比较字符串 "pro" (长度 3)
    if (tier.len == 3) {
        uint16_t first2 = *(uint16_t*)tier.ptr;       // "pr" = 0x7270 (LE)
        uint8_t  third  = *(uint8_t*)(tier.ptr + 2);  // "o"  = 0x6F
        if (first2 == 0x7270 && third == 0x6F)
            return true;
    }
    return false;
}
```

---

## quota.Manager

**大小**: 推测 0x90+ 字节
**构造函数**: `mobai_internal_quota.NewManager` @ `0x140F2DEE0`

```c
// 从 NewManager 初始化代码反推:
// 0x140F2DFEC: mov [rax+0x38], ...  ← tier 指针
// 0x140F2DFFB: mov [rax+0x40], 4    ← tierCode = 4
// 0x140F2DFFF: mov [rax+0x48], 100  ← tokensRemaining = 100
// 0x140F2E007: mov [rax+0x50], 100  ← limit = 100 (补丁 5→-1)

struct QuotaManager {
    SupabaseClient* supabaseClient;  // +0x00: supabase.Client
    EventEmitter*   eventEmitter;    // +0x08: 事件通知
    void*           storage;         // +0x10: 本地持久化 (BoltDB?)
    
    // ... 中间字段 (rune/context/mutex等)
    
    uint8_t* tierPtr;                // +0x38: Go string.ptr → "free"/"pro"
    int64_t  tierCode;               // +0x40: tier 数字代码 (4=free, 3=pro?)
    int64_t  tokensRemaining;        // +0x48: 剩余 token 数 (初始 100)
    int64_t  limit;                  // +0x50: 每日限额 (100=free, -1=pro)
    
    void* offlineTicket;             // +0x58: 离线模式票据
    
    // ... 更多字段
};
```

### 关键方法

| 方法 | VA | 访问的字段 |
|------|-----|-----------|
| `GetLimit()` | `0x140F2FC60` | 读 `+0x50` (limit) |
| `CanUseToken()` | `0x140F2E3E0` | 读 `+0x50` (limit), `+0x48` (tokensRemaining) |
| `UseToken()` | `0x140F2E4A0` | 读 `+0x48`, 写 `+0x48` (tokensRemaining--) |
| `SetTier()` | `0x140F2E6A0` | 写 `+0x38` (tier), 写 `+0x40` (tierCode) |
| `GetTier()` | `0x140F2E5E0` | 读 `+0x38` (tier ptr/length) |

### GetLimit 反编译 (伪代码)
```c
// VA: 0x140F2FC60 — 含 panic 恢复!
int64_t GetLimit(QuotaManager* q) {
    // Go defer/panic 框架
    int64_t limit;
    if (__go_recover()) {
        limit = q->limit;           // +0x50 → panic 恢复路径 (补丁 2)
    } else {
        q->mutex.RLock();           // 读锁
        limit = q->limit;           // +0x50 → 正常路径 (补丁 1)
        q->mutex.RUnlock();
    }
    return limit;                   // rax = limit
}
```

### CanUseToken 反编译 (伪代码)
```c
// VA: 0x140F2E3E0 — 直接读字段, 不调用 GetLimit()!
bool CanUseToken(QuotaManager* q) {
    q->mutex.RLock();
    
    int64_t limit = q->limit;              // 直接读 +0x50 — 不调用 GetLimit()!
    
    if (limit >= 0) {
        // free 用户路径 — 检查剩余 token
        int64_t remaining = q->tokensRemaining;  // 直接读 +0x48
        q->mutex.RUnlock();
        return remaining > 0;              // 还有 token → true
    }
    
    // Pro 用户 (limit < 0) — 无限
    q->mutex.RUnlock();
    return true;
}
```

**这就是补丁 5 必须改字段初始值的原因**: CanUseToken 直接读 `+0x50` 字段, 不管 GetLimit 返回什么。

### SetTier 反编译 (伪代码)
```c
// VA: 0x140F2E6A0
void SetTier(QuotaManager* q, GoString tier, int64_t code) {
    q->mutex.Lock();
    q->tierPtr = tier.ptr;           // +0x38
    q->tierLen = tier.len;           // (string 内联)
    q->tierCode = code;              // +0x40
    // ⚠️ 不更新 +0x50 (limit)!  ← 设计缺陷
    q->mutex.Unlock();
}
```

**重要**: `SetTier` 只更新 tier/tierCode, **不更新 limit**。这意味着即使 `SetTier("pro", 3)` 成功, limit 仍为 100。
这是补丁策略必须修改初始化值而非依赖 SetTier 的原因。

---

## supabase.Client

**大小**: 未知 (未完整逆向)
**构造函数**: `mobai_internal_supabase.NewClient`

```c
struct SupabaseClient {
    void* httpClient;                // +0x00: http.Client
    uint8_t* baseURL;                // +0x08: Go string
    uint8_t* anonKey;                // +0x10: Go string (Supabase anon key)
    void* auth;                      // +0x18: Auth 模块
    void* storage;                   // +0x20: JWT 持久化 (localStorage/文件)
};
```

**相关端点** (从 `SyncLicense` 反编译推断):
- `GET /rest/v1/profiles?select=tier&id=eq.{uuid}` → 获取用户 tier
- `POST /auth/v1/verify` → OTP 验证
- `POST /auth/v1/token?grant_type=refresh_token` → 刷新 JWT

---

## Go 运行时类型处理笔记

### Go String 内部表示
```c
// Go 源码: type stringStruct struct { str unsafe.Pointer; len int }
// 在 x86-64 ABI 中:
struct GoString {
    uint8_t* ptr;    // 8 bytes — 字符串数据指针
    int64_t  len;    // 8 bytes — 字符串长度
};
// 总共 16 bytes, 在函数参数/返回值中占用 2 个寄存器或 16 bytes 栈空间
```

### Go Interface 内部表示
```c
// interface{} / error 在 x86-64 ABI 中:
struct GoInterface {
    void* type;      // 8 bytes — 类型描述符 (itab)
    void* data;      // 8 bytes — 数据指针
};
// error 是特殊的 interface (内置接口)
```

### Go ABI0 调用约定 (x86-64)
```
参数传递: 寄存器 RAX, RBX, RCX, RDI, RSI, R8, R9, R10 + 栈
返回值:   RAX (ret0), RBX (ret1), RCX (ret2), ...
          interface{} = {type, data} → 占用 2 个 slot:
            ret0.type = RAX, ret0.data = RBX
            ret1.type = RCX, ret1.data = RDI

栈帧:     R14 = goroutine 指针 (g)
          FS 段基址 = goroutine 的 TLS
```

### PCLNTAB 符号恢复
```
.symtab 段包含:
  - func tab:  {entry, offset} 对 — 快速函数名查找
  - pcln tab:  {pc, line, file} 三元组 — PC→源码行映射
  - 类型描述符: runtime._type 结构 — 类型名/大小/方法集

IDA Pro 自动解析为:
  package_path.(*Type).Method
  package_path.Function
  
示例:
  mobai_internal_license.(*Manager).IsPro
  mobai_internal_quota.NewManager
  main.(*App).GetLicenseStatus
```
