# 性能浮窗

在桌面或无边框窗口化游戏中查看帧率、CPU / GPU 温度、负载与功耗、内存和显存占用，以及黑鲨风神 Pro（BRB02）或黑鲨风神（BRB03）的散热器转速。FPS 诊断还可显示 1% 低帧和采集进程。

## 下载和校验

**[下载 Windows 安装包](https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/performance-overlay/dist/Alp-Performance-Overlay-setup-v1.exe)** · 扩展 1.0.0 · 284,665 字节

需要 Windows x64 和提供「设置 → 扩展」的 Alp 0.2.2 Beta v8 Preview。[Alp 工具箱项目](https://github.com/starsinking07/alp-toolbox)

在下载目录打开 PowerShell，计算安装包的 SHA-256。

```powershell
$file = 'Alp-Performance-Overlay-setup-v1.exe'
(Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash
```

安装包 SHA-256

6e3e6a771661e03b2be152366b444c678626bf55a55c9defa5e9b42757f7c6e3

[SHA-256 校验清单](dist/SHA256SUMS.txt)

## 开启浮窗

1. 校验安装包后双击运行，按 Windows 提示授权安装。
2. 从系统托盘右键「退出 Alp 工具箱」，再重新打开。扩展页的「重新检测」可以确认安装状态，重新启动后才会加载浮窗。
3. 在「设置 → 扩展」开启性能浮窗。展开设置可调整显示项、布局、透明度和位置。启用全局快捷键后，可用 `Ctrl+Alt+F3` 开关浮窗。

只想看温度和转速时，可以取消 FPS 显示和仅在游戏中显示的选项。两项都关闭时无需启动采帧程序。游戏帧率由独立运行的 PresentMon 读取 Windows ETW 呈现事件，对游戏进程零注入。

如果独占全屏盖住了浮窗，可切换为无边框窗口。帧率显示为 `--` 时，展开扩展卡片查看采集诊断和权限提示。

## 单独卸载

优先从托盘退出工具箱，再在 Windows「设置 → 应用 → 已安装的应用」或「应用和功能」中卸载 **Alp 性能浮窗扩展**。也可以先关闭浮窗，再用扩展卡片上的「卸载」按钮。遇到文件占用时，从托盘退出后重试。重新打开工具箱后，扩展状态会更新，显示项和布局偏好仍保存在 Alp 内。

<details>
<summary>安装位置、载荷核验及许可</summary>

扩展安装在 `Program Files\Alp Toolbox Extensions\Performance Overlay\v1`。工具箱识别的是该目录中的 `PresentMon.exe`，以宿主内置的 SHA-256 为准。

PresentMon.exe SHA-256

226847b84157a168dc0cddd6cfe7cef2c04128b2dd333205c37b141af8e0bf4f

[PresentMon 许可证](licenses/PresentMon-LICENSE.txt) · [版权与通知](licenses/PresentMon-NOTICE.txt) · [官方安装器脚本](installer/Alp-performance-overlay.nsi)

</details>

[返回 Alp 扩展中心](../../README.md)
