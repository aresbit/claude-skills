# MobAI Pro 补丁详情 — 原始字节对照表

## 概述

7 处补丁，目标二进制: `MobAI_payload.exe` (145 MB, Go 1.22+ 64-bit PE)
Image Base: `0x140000000`

---

## 补丁 1: GetLimit 返回路径 1

| 项目 | 值 |
|------|-----|
| VA | `0x140F2FC85` |
| 函数 | `mobai_internal_quota.(*Manager).GetLimit` |
| 文件偏移 | `.text` 段, RVA `0xF2FC85` → file `0xF2F285` |

### 原始代码
```
.text:0x140F2FC85  48 8B 44 24 10    mov  rax, [rsp+0x10]   ; rax = limit 字段 (100)
.text:0x140F2FC8A  48 8B 6C 24 18    mov  rbp, [rsp+0x18]
.text:0x140F2FC8F  48 83 C4 20       add  rsp, 0x20
.text:0x140F2FC93  5D                pop  rbp
.text:0x140F2FC94  C3                ret
```

### 补丁后
```
.text:0x140F2FC85  6A FF             push -1
.text:0x140F2FC87  58                pop  rax              ; rax = -1 (无限)
.text:0x140F2FC88  90                nop
.text:0x140F2FC89  90                nop
.text:0x140F2FC8A  48 8B 6C 24 18    mov  rbp, [rsp+0x18]
.text:0x140F2FC8F  48 83 C4 20       add  rsp, 0x20
.text:0x140F2FC93  5D                pop  rbp
.text:0x140F2FC94  C3                ret
```

**编码技巧**: `mov rax, -1` = `48 C7 C0 FF FF FF FF` (7B) 放不进 5B 空间。
`push -1; pop rax` = `6A FF 58` (3B) + 2×NOP = 5B ✓

---

## 补丁 2: GetLimit 返回路径 2 (panic 恢复路径)

| 项目 | 值 |
|------|-----|
| VA | `0x140F2FC95` |
| 函数 | 同上，Go defer/panic 恢复分支 |

### 原始代码
```
.text:0x140F2FC95  48 8B 44 24 10    mov  rax, [rsp+0x10]   ; panic 恢复后读 limit
```

### 补丁后
```
.text:0x140F2FC95  6A FF             push -1
.text:0x140F2FC97  58                pop  rax
.text:0x140F2FC98  90                nop
.text:0x140F2FC99  90                nop
```

---

## 补丁 3: license.NewManager tier 字符串长度 4→3

| 项目 | 值 |
|------|-----|
| VA | `0x140F3137D` |
| 函数 | `mobai_internal_license.NewManager` |
| 说明 | 将 tier 长度从 "free"(4) 改为 "pro"(3) |

### 原始代码
```
.text:0x140F3137D  48 C7 40 18 04 00 00 00   mov  qword [rax+0x18], 4   ; tierLen = 4
```

### 补丁后
```
.text:0x140F3137D  48 C7 40 18 03 00 00 00   mov  qword [rax+0x18], 3   ; tierLen = 3
```

**关键**: 必须与补丁 4 的字符串覆写配合，长度不匹配会导致 Go 字符串比较失败。

---

## 补丁 4: "free" 字符串覆写 → "pro\0"

| 项目 | 值 |
|------|-----|
| VA | `0x1418D15B8` |
| 段 | `.rdata` (只读数据段) |
| 说明 | 覆写字符串常量 |

### 原始字节
```
.rdata:0x1418D15B8  66 72 65 65    "free"
```

### 补丁后
```
.rdata:0x1418D15B8  70 72 6F 00    "pro\0"
```

**关键**: `"pro"` 只有 3 字节，用 `\0` 填充第 4 字节。所有引用此地址的代码会自动读到 "pro"。

**如何定位**: IDA 中搜索 "free" 字符串，找到与 `license.NewManager` 中初始化代码对应的 xref。
```c
// NewManager 中的初始化逻辑 (反编译)
manager->tier.ptr = &string_free;   // → 0x1418D15B8
manager->tier.len = 4;              // → 补丁 3 改为 3
```

---

## 补丁 5: quota.NewManager limit 初始值 100→-1

| 项目 | 值 |
|------|-----|
| VA | `0x140F2E007` |
| 函数 | `mobai_internal_quota.NewManager` |
| 说明 | 配额管理器初始化时直接写入 limit=-1 |

### 原始代码
```
.text:0x140F2E007  48 C7 40 50 64 00 00 00   mov  qword [rax+0x50], 100  ; limit = 100
```

### 补丁后
```
.text:0x140F2E007  48 C7 40 50 FF FF FF FF   mov  qword [rax+0x50], -1   ; limit = -1
```

**为什么必须改这里**: `CanUseToken`/`UseToken` 直接读取 `+0x50` 字段，不调用 `GetLimit()`。
即使 `GetLimit()` 被补丁为返回 -1，这些内联访问仍然读到旧值 100。

```c
// CanUseToken 反编译 — 直接读字段!
bool CanUseToken(QuotaManager* q) {
    if (q->limit >= 0)          // 直接读 +0x50
        return q->tokensRemaining > 0;  // +0x48
    return true;               // limit < 0 → 跳过 token 检查
}
```

---

## 补丁 6: RefreshTier 禁用

| 项目 | 值 |
|------|-----|
| VA | `0x140F33080` |
| 函数 | `mobai_internal_license.(*Manager).RefreshTier` |
| 签名 | `func (m *Manager) RefreshTier() (interface{}, error)` |

### 原始代码 (函数入口, 8 字节)
```
.text:0x140F33080  49 3B 66 10          cmp  rsp, [r14+0x10]
.text:0x140F33084  0F 86 04 03 00 00    jbe  loc_140F3338E
.text:0x140F3308A  4C 8D 64 24 F8       lea  r12, [rsp-0x8]
...
; 函数体会调用 SyncLicense → setTier → 服务器覆盖本地 tier
```

### 补丁后
```
.text:0x140F33080  31 C0                xor  eax, eax     ; rax = 0
.text:0x140F33082  31 DB                xor  ebx, ebx     ; rbx = 0
.text:0x140F33084  C3                   ret              ; 立即返回
.text:0x140F33085  90                   nop
.text:0x140F33086  90                   nop
.text:0x140F33087  90                   nop
.text:0x140F33088  90                   nop
```

**Go ABI 语义**: `xor eax,eax; xor ebx,ebx; ret` = `return nil, nil`
- rax = 返回值1 (interface{} data pointer) = nil
- rbx = 返回值2 (error interface) = nil

调用方 `StartTierSync` 拿到 `(nil, nil)` 认为刷新成功但无数据，不会覆盖本地 tier。

---

## 补丁 7: StartTierSync 禁用

| 项目 | 值 |
|------|-----|
| VA | `0x140F33EC0` |
| 函数 | `mobai_internal_license.(*Manager).StartTierSync` |
| 说明 | 启动定时同步 goroutine，周期性调用 RefreshTier |

### 原始代码 (函数入口, 11 字节)
```
.text:0x140F33EC0  4C 8D 64 24 F8       lea  r12, [rsp-0x8]
.text:0x140F33EC5  48 83 EC 38          sub  rsp, 0x38
...
; 启动 ticker，周期性调用 RefreshTier
```

### 补丁后
```
.text:0x140F33EC0  C3                   ret              ; 立即返回, 不启动同步
.text:0x140F33EC1  90
.text:0x140F33EC2  90
.text:0x140F33EC3  90
.text:0x140F33EC4  90
.text:0x140F33EC5  90
.text:0x140F33EC6  90
.text:0x140F33EC7  90
.text:0x140F33EC8  90
.text:0x140F33EC9  90
.text:0x140F33ECA  90
```

**注意**: 虽然补丁 6 已经禁用了 RefreshTier，但这里也直接 ret 是为了双重保险。如果未来代码变更导致 RefreshTier 有其他调用路径，StartTierSync 仍然不会启动同步。

---

## 补丁依赖关系

```
补丁 3 (len 4→3) ──── 依赖 ──── 补丁 4 ("free"→"pro\0")
      │                              │
      │    IsPro() 比较 "pro" 字符串，长度必须=3
      │    GetTier() 返回的 {ptr, len} 必须一致
      │                              │
补丁 1+2 (GetLimit→-1) ── 依赖 ── 补丁 5 (limit 字段→-1)
      │                              │
      │    CanUseToken() 直接读 +0x50 字段
      │    只改 GetLimit 不够，字段初始化也要改
      │                              │
补丁 6 (RefreshTier noop) ── 独立 ── 补丁 7 (StartTierSync noop)
      │                              │
      └──── 双重防服务器覆盖 ─────────┘
```

## v1.0 失败原因对照

| v1.0 做了什么 | 为什么失败 | v2.0 如何修复 |
|--------------|-----------|--------------|
| 修补 IsPro → 返回 true | 前端直接用 `tier` 字符串显示 "Free" | 补丁 3+4 改为 "pro" |
| 修补 HasUnlimitedTokens → true | CanUseToken 直接读字段, 不调 HasUnlimitedTokens | 补丁 5 改字段初始值 |
| 修补 RefreshTier (错误地址) | 地址偏移了 ~0xFF6 字节, 根本没改对 | 补丁 6 在正确地址 |
| 修补 StartTierSync (错误地址) | 同上 | 补丁 7 在正确地址 |
| 未修补 GetLimit | limit 仍为 100, CanUseToken 直接读字段 | 补丁 1+2 改 GetLimit |
