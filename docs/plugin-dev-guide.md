# 为 Alp 制作扩展

从可独立安装、卸载的 Windows 安装包做起。扩展文件有自己的目录和校验值，宿主源码负责识别可信载荷并在「设置 → 扩展」显示卡片。[起步模板](../templates/extension-template/README.md)

## 1. 规划扩展文件

为扩展选择唯一 ID 和目录名，例如 `vendor.example-extension` 和 `plugins/example-extension/`。给使用者写明适用机型、用途、需要的 Alp 版本以及安装、重启和卸载步骤。

- 用 `plugin.json` 登记名称、版本、平台和安装器信息。[扩展清单规范](../schemas/plugin.schema.json)
- 用 `installer/` 保存 NSIS 源文件，成品及其 `SHA256SUMS.txt` 放在 `dist/`。
- 随包分发第三方程序时，保留对应的许可证和通知，并在扩展说明里标明来源。

## 2. 打包成可独立卸载的程序

复制模板，先用自己的载荷完成安装和卸载测试。现有宿主采用 64 位 Program Files 目录，例如 `Program Files\Alp Toolbox Extensions\Example Extension\v1`。NSIS 中用 `$PROGRAMFILES64` 取系统目录，用 `SetRegView 64` 将唯一的卸载键写入 `HKLM\Software\Microsoft\Windows\CurrentVersion\Uninstall`。

卸载器只处理安装器列出的文件。核心载荷被占用时，提示用户从托盘退出 Alp 后再试，并保留卸载条目。版本并排安装时，应给对应版本分配独立的目录和卸载键。[NSIS 模板](../templates/extension-template/installer/extension-template.nsi) · [性能浮窗安装器参考](../plugins/performance-overlay/installer/Alp-performance-overlay.nsi)

## 3. 核对两种 SHA-256

- `sha256` 和 `size` 记录下载的安装包 SHA-256 和字节数。将同一个安装包摘要写入 `dist/SHA256SUMS.txt`。
- `payloadSha256` 记录安装后供宿主验证的核心文件 SHA-256。性能浮窗的核心文件是 `PresentMon.exe`，宿主在源码中固定其路径和预期哈希。
- 清单中的下载链接应指向可直接下载的安装包。提交目录收录时，让 `catalog.json` 的条目与该扩展的 `plugin.json` 一致。模板里的站点、哈希和大小都是示例值。[目录示例](../examples/catalog.sample.json) · [目录清单规范](../schemas/catalog.schema.json)

对已经确认过的载荷先校验、后启动。涉及采帧时沿用独立进程与 ETW 的方式，保持对游戏进程零注入。

## 4. 接入 Alp 的扩展卡片

当前 Alp 通过宿主源码显式登记每项扩展。目录清单用于分发与校验，卡片及运行控制随宿主版本发布。开发时使用包含以下接口的 Alp 宿主源码。本文对照的宿主构建是 `20261127-v8-extensions-repo-preview`。[Alp 主项目](https://github.com/starsinking07/alp-toolbox)

1. 在宿主中实现已安装检测。可参考 `brb02/overlay_extension.py`，从 Program Files 中的固定位置核对核心载荷 SHA-256，随后把检测结果传给卡片。
2. 在 `brb02/gui/pages.py` 的 `_build_extensions_tab()` 里，把 `ExtensionCard` 加入 `ExtensionsPanel`。安装完整但未运行时传 `ready`，功能已启动时传 `running`，缺文件或校验失败时传 `absent`。让获取、卸载和运行开关调用各自的宿主回调。
3. 用 `make_extension_subcard()` 生成抽屉里的设置分区，把控件放入返回的布局，再把子卡片加入 `card.drawer_layout`。这样设置区可以沿用宿主的玻璃与实色主题。
4. 宿主确认启停结果后，更新开关和 `card.set_status()`，再调用 `panel.apply_filters()`。安装或卸载后，重启工具箱会重新读取安装状态。[卡片示例源码](../templates/extension-template/host-snippet/card_example.py)

## 5. 验证和提交

- 测试未安装、校验失败、已安装、启动、退出和独立卸载。安装或卸载完成后，从托盘退出并重开 Alp，确认卡片状态与磁盘一致。
- 检查提交的代码、文档和日志，移除本机路径、私人账户名及真实设备地址。给出可复查的安装包与核心文件摘要。
- 推送前运行离线校验。发布到 GitHub 后加 `--online` 再跑一次，核对 GitHub 分支中的文档路径、公开链接、目录清单和下载包。

```powershell
py -3.14 -B scripts/verify_repo.py
py -3.14 -B scripts/verify_repo.py --online
```

扩展仓库提交安装器、清单、许可证和验证结果。宿主检测、卡片和运行接线随配套代码提交给 Alp 主项目。

[返回 Alp 扩展中心](../README.md)
