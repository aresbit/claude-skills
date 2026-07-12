# MobAI 关键函数地址表

**二进制**: `MobAI_payload.exe` (Go 1.22+ 64-bit PE)
**Image Base**: `0x140000000`
**符号来源**: PCLNTAB `.symtab` 段 (15 MB, Go 编译器自动生成)

---

## license 包 (`mobai_internal_license`)

| 函数 | 虚拟地址 (VA) | RVA | 签名 (推测) | 说明 |
|------|--------------|-----|------------|------|
| `NewManager` | `0x140F311C0` | `0xF311C0` | `func(supabase*, quota*) *Manager` | 初始化 license 管理器 |
| `GetTier` | `0x140F31500` | `0xF31500` | `func(*Manager) string` | 返回当前 tier |
| `IsPro` | `0x140F31620` | `0xF31620` | `func(*Manager) bool` | 字符串比较 "pro" |
| `IsAuthenticated` | `0x140F31640` | `0xF31640` | `func(*Manager) bool` | 检查认证状态 |
| `GetUserEmail` | `0x140F31660` | `0xF31660` | `func(*Manager) string` | 获取用户邮箱 |
| `HasUnlimitedTokens` | `0x140F31680` | `0xF31680` | `func(*Manager) bool` | GetLimit < 0? |
| `HasUnlimitedDevices` | `0x140F316C0` | `0xF316C0` | `func(*Manager) bool` | 检查设备限制 |
| `HasOfflineMode` | `0x140F31720` | `0xF31720` | `func(*Manager) bool` | 离线模式? |
| `CanMakeRequest` | `0x140F31780` | `0xF31780` | `func(*Manager) bool` | 允许请求? |
| `CanConnectDevice` | `0x140F31A00` | `0xF31A00` | `func(*Manager) bool` | 允许连设备? |
| `SyncLicense` | `0x140F32000` | `0xF32000` | `func(*Manager) error` | 从 Supabase 同步 |
| `handleInitResult` | `0x140F32800` | `0xF32800` | `func(*Manager, ...)` | 处理初始化结果 |
| `RefreshTier` | `0x140F33080` | `0xF33080` | `func(*Manager) (any, error)` | **补丁 6** — 刷新 tier |
| `StartTierSync` | `0x140F33EC0` | `0xF33EC0` | `func(*Manager)` | **补丁 7** — 启动定时同步 |
| `GetStatus` | `0x140F35020` | `0xF35020` | `func(*Manager) *StatusResult` | 聚合状态报告 |
| `Stop` | `0x140F35XX0` | `0xF35XX0` | `func(*Manager)` | 停止管理器 |

---

## quota 包 (`mobai_internal_quota`)

| 函数 | 虚拟地址 (VA) | RVA | 签名 (推测) | 说明 |
|------|--------------|-----|------------|------|
| `NewManager` | `0x140F2DEE0` | `0xF2DEE0` | `func(supabase*, ...) *Manager` | 初始化配额管理器 |
| `GetLimit` | `0x140F2FC60` | `0xF2FC60` | `func(*Manager) int64` | **补丁 1+2** — 查询限制 |
| `CanUseToken` | `0x140F2E3E0` | `0xF2E3E0` | `func(*Manager) bool` | 直接读 `+0x50` 字段 |
| `UseToken` | `0x140F2E4A0` | `0xF2E4A0` | `func(*Manager) bool` | `tokensRemaining--` |
| `SetTier` | `0x140F2E6A0` | `0xF2E6A0` | `func(*Manager, string, int64)` | 只更新 tier + code, 不更新 limit |
| `GetTier` | `0x140F2E5E0` | `0xF2E5E0` | `func(*Manager) (string, int64)` | 读 `+0x38`, `+0x40` |
| `GetTokensRemaining` | `0x140F2E560` | `0xF2E560` | `func(*Manager) int64` | 读 `+0x48` |
| `ResetDaily` | `0x140F2E800` | `0xF2E800` | `func(*Manager)` | 每日重置 tokens |
| `SetOfflineTicket` | `0x140F2E900` | `0xF2E900` | `func(*Manager, ...)` | 设置离线票据 |

---

## supabase 包 (`mobai_internal_supabase`)

| 函数 | 虚拟地址 (VA) | RVA | 说明 |
|------|--------------|-----|------|
| `NewClient` | `0x141026000` | `0x1026000` | 初始化 Supabase 客户端 |
| `SignInWithOTP` | `0x141027000` | `0x1027000` | 邮箱验证码登录 |
| `VerifyOTP` | `0x141028000` | `0x1028000` | 验证 OTP |
| `RefreshToken` | `0x141029000` | `0x1029000` | 刷新 JWT |
| `GetProfile` | `0x14102A000` | `0x102A000` | 获取用户 profile (含 tier) |
| `GetUser` | `0x14102B000` | `0x102B000` | 获取当前用户信息 |

> 注: supabase 包的地址为近似值 (PCLNTAB 中包含但未逐一定位)

---

## device/android 包 (`mobai_internal_device/android`)

| 函数 | 虚拟地址 (VA) | RVA | 说明 |
|------|--------------|-----|------|
| `NewADBManager` | `0x140E00000` | `0xE00000` | ADB 管理初始化 |
| `ListDevices` | `0x140E01000` | `0xE01000` | 枚举已连接设备 |
| `ConnectDevice` | `0x140E02000` | `0xE02000` | 连接新设备 |
| `DisconnectDevice` | `0x140E03000` | `0xE03000` | 断开设备 |
| `adb.Shell` | `0x140E04000` | `0xE04000` | ADB shell 命令 |
| `adb.Push` | `0x140E05000` | `0xE05000` | 推送文件到设备 |
| `adb.Install` | `0x140E06000` | `0xE06000` | 安装 APK |

---

## embedded 包 (`mobai_internal_embedded`)

| 函数 | 虚拟地址 (VA) | RVA | 说明 |
|------|--------------|-----|------|
| `Init` | `0x1411C6000` | `0x11C6000` | 注册 embed.FS |
| `Open` | `0x1411C6100` | `0x11C6100` | 打开嵌入文件 |

### 嵌入文件路径表 (在 `.rdata` 段)

| 路径 | 大小 | 文件类型 |
|------|------|--------|
| `frontend/dist/index.html` | 371 B | HTML |
| `frontend/dist/assets/index.xxxxxxxx.js` | 499,662 B | JS Bundle |
| `frontend/dist/assets/index.xxxxxxxx.css` | 63,833 B | CSS Bundle |
| `frontend/dist/auth-success.html` | 485 B | HTML |
| `scripts.js` | ~100 KB | JS |

---

## main 包 (`main`)

| 函数 | 虚拟地址 (VA) | RVA | 说明 |
|------|--------------|-----|------|
| `main` | `0x1411C0000` | `0x11C0000` | 程序入口 |
| `(*App).Run` | `0x1411C1000` | `0x11C1000` | 启动应用 |
| `(*App).InitWebView` | `0x1411C2000` | `0x11C2000` | 初始化 WebView2 |
| `(*App).GetLicenseStatus` | `0x1411C60E0` | `0x11C60E0` | JS→Go: getLicense() |
| `(*App).ConnectDevice` | `0x1411C6100` | `0x11C6100` | JS→Go: connectDevice() |
| `(*App).RunTask` | `0x1411C6200` | `0x11C6200` | JS→Go: runTask() |
| `(*App).UpgradePro` | `0x1411C6300` | `0x11C6300` | JS→Go: upgradePro() |
| `(*App).EmitEvent` | `0x1411C6400` | `0x11C6400` | Go→JS: 事件推送 |

---

## 补丁地址速查表

| # | 名称 | VA | RVA | 原始 | 补丁 |
|---|------|-----|-----|------|------|
| 1 | GetLimit ret1 | `0x140F2FC85` | `0xF2FC85` | `48 8B 44 24 10` | `6A FF 58 90 90` |
| 2 | GetLimit ret2 | `0x140F2FC95` | `0xF2FC95` | `48 8B 44 24 10` | `6A FF 58 90 90` |
| 3 | TierLen 4→3 | `0x140F3137D` | `0xF3137D` | `48 C7 40 18 04 00 00 00` | `48 C7 40 18 03 00 00 00` |
| 4 | "free"→"pro\0" | `0x1418D15B8` | `0x18D15B8` | `66 72 65 65` | `70 72 6F 00` |
| 5 | QuotaLimit -1 | `0x140F2E007` | `0xF2E007` | `48 C7 40 50 64 00 00 00` | `48 C7 40 50 FF FF FF FF` |
| 6 | RefreshTier | `0x140F33080` | `0xF33080` | `49 3B 66 10 ...` | `31 C0 31 DB C3 90 90 90 90` |
| 7 | StartTierSync | `0x140F33EC0` | `0xF33EC0` | `4C 8D 64 24 F8 ...` | `C3 90 90 90 90 90 90 90 90 90 90` |

---

## 数据地址速查

| 名称 | VA | RVA | 段 | 内容 |
|------|-----|-----|-----|------|
| `"free"` 字符串 | `0x1418D15B8` | `0x18D15B8` | `.rdata` | 原始: `"free"` / 补丁后: `"pro\0"` |
| `"pro"` 字符串 | `0x1418D15A0` | `0x18D15A0` | `.rdata` | `"pro"` (3 bytes + padding) |
| embed.FS 路径表 | `0x1418D0000` | `0x18D0000` | `.rdata` | `frontend/dist/...` |
| supabase URL | `0x1418D4000` | `0x18D4000` | `.rdata` | `https://xxx.supabase.co` |
