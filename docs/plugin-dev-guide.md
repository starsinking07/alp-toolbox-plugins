# Alp Toolbox 自制扩展与插件开发教程

本指南说明如何为 [**Alp 工具箱（Alp Toolbox）**](https://github.com/starsinking07/alp-toolbox) 设计、打包、校验并提交可选扩展或插件（结构规范以 [schemas/catalog.schema.json](../schemas/catalog.schema.json) 与 [schemas/plugin.schema.json](../schemas/plugin.schema.json) 为准）。

---

## 1. 扩展架构与运行形态概览

### 当前已落地的官方形态：`optional-installer`

- **独立安装隔离**：将可选辅助二进制、许可协议与单独卸载入口拆出主安装包，按需安装到 `Program Files\Alp Toolbox Extensions\<ExtensionName>\v<Major>`（64 位受保护目录，避免普通进程或第三方篡改）。
- **零猜测强校验**：Alp 工具箱主程序不在安装阶段盲信磁盘文件名，也不从临时目录或源码路径顺手加载，而是在定位受保护目录内的核心载荷文件时计算**小写 64 位 SHA-256 摘要**；只有哈希严格匹配已签名清单时才激活该扩展模块，其余情形自动退回为「未安装」并保留用户已有配置。
- **零进程注入**：不向游戏或系统进程注入 DLL；以官方 [performance-overlay](../plugins/performance-overlay/README.md) 为例，帧率采集仅通过独立可信进程读取 Intel PresentMon ETW 会话并由工具箱界面按需刷新。
- **独立生命周期与卸载**：扩展单独在注册表 `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\<Key>` 登记卸载项，既可从 Windows「已安装的应用」卸载，也可在 **设置 → 扩展** 卡片右上角直接拉起卸载器。

### 后续规划形态：`sidecar` / `ui-module`

- [catalog.schema.json](../schemas/catalog.schema.json) 与 [plugin.schema.json](../schemas/plugin.schema.json) 同时为后续按需拉起的独立守护进程（`sidecar`）与纯界面模块（`ui-module`）预留了清单枚举字段（见 [examples/catalog.sample.json](../examples/catalog.sample.json)）；当前核心主程序按扩展专用识别逻辑加载官方扩展，若需让第三方扩展在面板直接显示，需同时向主仓库提交宿主接入 PR（见第 4 节）。

---

## 2. 目录结构与清单字段规范

每个扩展目录应放在 `plugins/<slug>/` 下（建议使用小写字母、数字和短横线），典型结构如下：

```text
plugins/<slug>/
├─ README.md                       # 扩展简介、安装/卸载说明、SHA-256 与版本要求
├─ plugin.json                     # 扩展元数据清单（必须匹配 plugin.schema.json）
├─ installer/<slug>.nsi            # NSIS Unicode 安装脚本（推荐写入 Program Files\Alp Toolbox Extensions\...）
├─ licenses/                       # 若携带任何第三方二进制，必须随附原始 LICENSE 与 NOTICE
└─ dist/
   ├─ Alp-<Name>-setup-v1.exe      # 独立扩展安装包
   └─ SHA256SUMS.txt               # `<sha256>  <filename>` 格式校验文件
```

### `plugin.json` 核心字段

| 字段 | 类型 / 格式 | 说明 |
| --- | --- | --- |
| `id` | `^[a-z0-9][a-z0-9.-]{1,63}$` | 全局唯一 ID，建议使用 `<vendor>.<name>`（例如 `alp.performance-overlay`） |
| `name` | string | 扩展显示名称（支持中文，如 `性能浮窗`） |
| `description` | string | 一句话功能说明，将显示在「设置 → 扩展」卡片头部 |
| `version` | `X.Y.Z` | 语义化版本号 |
| `category` | `telemetry \| hardware \| ui \| integration \| utility` | 扩展分类 |
| `runtime` | `optional-installer \| sidecar \| ui-module` | 运行形态 |
| `uiSlot` | `settings-extensions \| sidebar-page \| tray-menu \| none` | 界面挂载位置 |
| `platform` | `windows-amd64` | 目标平台 |
| `minCoreVersion` | string | 最低兼容主程序版本号（如 `0.2.2-beta-v8-Preview`） |
| `installerName` | `*.exe` | `dist/` 中安装器文件名 |
| `installDir` | string | 默认安装目录说明，建议遵循 `Program Files\Alp Toolbox Extensions\<Name>\v1` |
| `downloadUrl` | `https://...` | 对 `alp-toolbox-plugins` 仓库一般为 `https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/<slug>/dist/<installerName>` |
| `sha256` | 64 位小写十六进制 | `installerName` 安装包本体的 SHA-256 |
| `payloadSha256` | 64 位小写十六进制 | 核心载荷文件（如采集器主 exe）的 SHA-256 |
| `size` | 正整数 | 安装包字节大小 |
| `restartRequired` | boolean | 安装/卸载后是否需要从托盘完全退出并重开工具箱 |

---

## 3. 零基础制作一个自制扩展（完整步骤）

仓库内的 [templates/extension-template/](../templates/extension-template/README.md) 提供了可直接改写的全套起步文件：

1. **复制模板目录**
   - 将 `templates/extension-template/` 复制为 `plugins/<your-ext>/`（例如 `plugins/my-fan-sensor/`）。
2. **编写 `plugin.json` 与 `README.md`**
   - 修改 `id`、`name`、`description`、`installerName`、`installDir` 与 `licenses/`（如有第三方可执行文件或库，务必保留原始许可证文件）。
3. **编写 NSIS 安装脚本**
   - 参考 `templates/extension-template/installer/extension-template.nsi` 与官方 [Alp-performance-overlay.nsi](../plugins/performance-overlay/installer/Alp-performance-overlay.nsi)：
     - 开启 `Unicode true` 与 `ManifestDPIAware true`；
     - `RequestExecutionLevel admin` 并使用 `SetRegView 64`，固定写入 `$PROGRAMFILES64\Alp Toolbox Extensions\<Name>\v1`；
     - 在写入 `Uninstall.exe` 的同时写入 `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall\<Key>` 键值（`DisplayName`、`DisplayVersion`、`InstallLocation`、`UninstallString`、`NoModify=1`、`NoRepair=1`），并在 `Section "Uninstall"` 中检测关键文件若正被工具箱占用则友好提示退出后再卸载。
4. **构建安装包并计算 SHA-256**
   - 用 NSIS 3.x 编译 `.nsi` 生成 `dist/<installerName>`；
   - 计算安装包本体 `sha256`、精确字节数 `size` 以及核心载荷 `payloadSha256`，同步写入 `dist/SHA256SUMS.txt`、`plugins/<your-ext>/plugin.json` 与根目录 `catalog.json`：
     ```powershell
     Get-FileHash .\plugins\<your-ext>\dist\<installerName> -Algorithm SHA256
     ```
5. **运行仓库离线校验**
   - 在仓库根目录执行：
     ```bash
     python scripts/verify_repo.py
     ```
   - 确认所有 JSON、Schema 字段、SHA-256/文件大小、相对链接、示例代码语法和隐私规范全部通过（0 报错）。

---

## 4. 在 Alp 工具箱主程序接入扩展界面

Alp 工具箱在 **设置 → 扩展** 中已封装标准化组件 [brb02/gui/extensions_ui.py](https://github.com/starsinking07/alp-toolbox/blob/main/brb02/gui/extensions_ui.py)，风格对齐 FanControl 卡片规范（也可对照 [templates/extension-template/host-snippet/card_example.py](../templates/extension-template/host-snippet/card_example.py)）：

- **`ExtensionsPanel`**：提供搜索输入框（`#ExtSearch`，36px 高度配 18px 圆角）、四态筛选切换按钮（`全部` / `已安装` / `运行中` / `未安装`，`#ExtFilterPill` 34px 高配 14px 圆角）、卡片列表容器 `add_card(...)` 与无结果提示空态卡 `empty_card`。
- **`ExtensionCard`**：继承玻璃质感容器 `GlassFrame`（切记**不要**在折叠抽屉 `drawer_layout` 里再嵌套 `GlassFrame`，以免产生双重模糊折射；子分区统一使用 `make_extension_subcard(title, hint)` 创建边框 `QFrame`）。主要构造参数：
  - `ext_id`, `name`, `version`, `mode_label`, `description`
  - `status`：`'running'`（运行中）、`'ready'`（已安装未启动）、`'absent'`（未安装）
  - `toggle_widget`：右上角状态开关（未安装态可传禁用的惰性 `Toggle(False)`）
  - `installed`：`bool`，决定抽屉按钮文案（`展开设置`/`收起设置` 或 `安装说明`/`收起说明`）与筛选分组
  - `icon_kind` / `accent_color` / `secondary_label` / `on_secondary` / `secondary_enabled` / `expanded` / `keywords`
- **常用联动方法**：
  - `card.set_status('running' | 'ready' | 'absent')`：实时刷新右上状态徽章配色并触发 `QStyle` 重绘；
  - `card.set_accent(colors['primary'])`：跟随用户自定义主题强调色切换；
  - `extensions_panel.apply_filters()`：搜索词与筛选状态变更时自动刷新可见性。

---

## 5. 安全与提交检查清单

提交 PR 到 `alp-toolbox-plugins` 前请逐项确认：

- [ ] 不向游戏或系统进程注入任何 DLL；核心辅助文件采用强 SHA-256 白名单校验；
- [ ] 所有第三方组件已在 `licenses/` 附带完整原始 `LICENSE` 与 `NOTICE`；
- [ ] `plugin.json`、`catalog.json`、`dist/SHA256SUMS.txt` 与实际 `.exe` 的哈希与字节数完全一致；
- [ ] 所有文档、清单、NSIS 与脚本中不含任何本机路径、个人用户名、密钥或真实硬件 MAC 地址；
- [ ] 本地执行 `python scripts/verify_repo.py` 全部通过。
