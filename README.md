# Alp 扩展中心

Alp 工具箱是黑鲨风神 Pro（BRB02）和黑鲨风神（BRB03）的 Windows 桌面伴侣。日常散热控制由主程序提供，想加功能时再安装扩展。[Alp 工具箱](https://github.com/starsinking07/alp-toolbox)

## 性能浮窗

玩游戏时，在小窗里看帧率、CPU / GPU 温度和散热器转速。也可以只显示硬件读数。

**[下载性能浮窗 v1](https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/performance-overlay/dist/Alp-Performance-Overlay-setup-v1.exe)** · Windows x64 · 约 278 KiB

适用于提供「设置 → 扩展」的 Alp 0.2.2 Beta v8 Preview。推荐在桌面或无边框窗口化游戏中使用。[显示项与常见问题](plugins/performance-overlay/README.md)

<details>
<summary>查看安装包 SHA-256</summary>

6e3e6a771661e03b2be152366b444c678626bf55a55c9defa5e9b42757f7c6e3

[完整校验清单](https://raw.githubusercontent.com/starsinking07/alp-toolbox-plugins/main/plugins/performance-overlay/dist/SHA256SUMS.txt)

</details>

## 安装、启用和卸载

1. 下载并校验扩展安装包，双击完成安装。
2. 从托盘右键退出 Alp 工具箱，再重新打开。
3. 在「设置 → 扩展」开启性能浮窗，选择想看的读数。

想移除时，先从托盘退出 Alp，再到 Windows 的「已安装的应用」卸载 **Alp 性能浮窗扩展**。重新打开工具箱即可看到更新后的安装状态。

## 游戏帧率从哪里来

PresentMon 读取 Windows ETW 的呈现事件，采帧对游戏进程零注入。采集器随扩展独立安装，工具箱在启用前对照内置 SHA-256 核验官方采集器。

## 为 Alp 做一个扩展

从独立安装和卸载开始，接入 Alp 的扩展卡片，再提交清单与校验结果。[开发指南](docs/plugin-dev-guide.md) · [起步模板](templates/extension-template/README.md)
