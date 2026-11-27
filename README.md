# Alp 工具箱官方插件与扩展仓库 (`alp-toolbox-plugins`)

本仓库为 [**Alp 工具箱（Alp Toolbox）**](https://github.com/starsinking07/alp-toolbox) 的独立扩展与插件仓库，参考 [`FanControl-Plugins`](https://github.com/Eureka-o/FanControl-Plugins) 组织形式，统一托管官方可选扩展安装包、目录索引 `catalog.json`（`schemaVersion: 1`）、JSON Schema、开源许可，以及第三方**自制扩展开发教程与起步模板**。

> **Official Extensions & Plugins Repository** for [Alp Toolbox](https://github.com/starsinking07/alp-toolbox): verified extension installers, catalog metadata, JSON schemas, DIY developer tutorial, starter template, and validation scripts.

---

## 目录结构

```text
alp-toolbox-plugins/
├─ README.md                                       # 仓库首页、官方扩展下载与使用说明
├─ LICENSE                                         # MIT 开源许可
├─ .gitignore
├─ catalog.json                                    # 官方扩展目录总索引 (schemaVersion: 1)
├─ docs/
│  ├─ README.md                                    # 文档导航
│  └─ plugin-dev-guide.md                          # 自制扩展开发与打包教程（含 UI 接入说明）
├─ schemas/
│  ├─ catalog.schema.json                          # catalog.json 校验 Schema
│  └─ plugin.schema.json                           # 单扩展 plugin.json 校验 Schema
├─ examples/
│  └─ catalog.sample.json                          # 多形态目录索引示例（含 sidecar 规划字段）
├─ plugins/
│  ├─ README.md                                    # 官方扩展索引说明
│  └─ performance-overlay/                         # 官方扩展：性能浮窗 (v1.0.0)
│     ├─ README.md                                 # 安装、配置、SHA-256 校验与卸载说明
│     ├─ plugin.json                               # 扩展清单元数据
│     ├─ installer/Alp-performance-overlay.nsi     # 官方 NSIS 安装脚本
│     ├─ licenses/PresentMon-LICENSE.txt           # 第三方许可声明
│     ├─ licenses/PresentMon-NOTICE.txt            # 版权与通知
│     └─ dist/
│        ├─ Alp-Performance-Overlay-setup-v1.exe   # 官方独立安装包 (284,665 B)
│        └─ SHA256SUMS.txt                         # 安装包 SHA-256 校验值
├─ templates/
│  └─ extension-template/                          # 自制扩展起步模板（可直接复制修改）
│     ├─ README.md
│     ├─ plugin.json
│     ├─ installer/extension-template.nsi
│     └─ host-snippet/card_example.py              # Alp 宿主 ExtensionCard 接入示例
└─ scripts/
   └─ verify_repo.py                               # 仓库完整性、SHA-256 与安全合规自检脚本
```

---

## 官方扩展一览

| ID | 名称 | 版本 | 运行形态 (`runtime`) | 界面位置 (`uiSlot`) | 最低主程序版本 | 直接下载 | 安装包 SHA-256 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `alp.performance-overlay` | 性能浮窗 | `1.0.0` | `optional-installer` | `settings-extensions` | `0.2.2-beta-v8-Preview` | [Alp-Performance-Overlay-setup-v1.exe](https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/performance-overlay/dist/Alp-Performance-Overlay-setup-v1.exe) | `6e3e6a771661e03b2be152366b444c678626bf55a55c9defa5e9b42757f7c6e3` |

详细说明见 [plugins/performance-overlay/README.md](plugins/performance-overlay/README.md)。

---

## 安装与卸载官方扩展

1. 下载上表中的安装包（例如 [Alp-Performance-Overlay-setup-v1.exe](https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/performance-overlay/dist/Alp-Performance-Overlay-setup-v1.exe)），核对 SHA-256 一致后双击安装（默认写入 `Program Files\Alp Toolbox Extensions\Performance Overlay\v1`）。
2. **从系统托盘完全退出 Alp 工具箱并重新启动**，使主程序按精确 SHA-256 核验并启用扩展模块（或在「设置 → 扩展」说明框点击「重新检测」后重启生效）。
3. 进入 **设置 → 扩展**，即可展开性能浮窗设置（显示项、布局、刷新节拍、位置与快捷键 `Ctrl+Alt+F3`）并通过右侧开关控制运行。
4. 如需移除，可在扩展卡片右上角点击「卸载」或通过 Windows「设置 → 应用 → 已安装的应用」卸载 `Alp 性能浮窗扩展`。

---

## 自制扩展 / 开发与验证

想为 Alp 工具箱制作自己的可选扩展，请先阅读 [自制扩展与插件开发教程](docs/plugin-dev-guide.md)，并基于 [templates/extension-template/](templates/extension-template/README.md) 模板起步。

提交或修改本仓库任何文件后，请运行自检脚本校验清单、SHA-256、文档链接与安全规范：

```bash
python scripts/verify_repo.py
```

返回主仓库：[starsinking07/alp-toolbox](https://github.com/starsinking07/alp-toolbox)
