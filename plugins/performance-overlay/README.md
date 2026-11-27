# 性能浮窗扩展 (`alp.performance-overlay`)

- **扩展 ID**：`alp.performance-overlay`
- **版本**：`1.0.0`
- **运行形态**：`optional-installer`（按需加载 · 安装/卸载后需从托盘重启工具箱）
- **最低主程序版本**：`0.2.2-beta-v8-Preview`
- **安装包**：[Alp-Performance-Overlay-setup-v1.exe](dist/Alp-Performance-Overlay-setup-v1.exe)（`284,665` 字节）
- **安装包 SHA-256**：`6e3e6a771661e03b2be152366b444c678626bf55a55c9defa5e9b42757f7c6e3`
- **默认安装目录**：`Program Files\Alp Toolbox Extensions\Performance Overlay\v1`
- **核心载荷 `PresentMon.exe` SHA-256**：`226847b84157a168dc0cddd6cfe7cef2c04128b2dd333205c37b141af8e0bf4f`

---

## 功能简介

在桌面与无边框窗口化游戏中实时显示帧率（Intel PresentMon ETW 采帧，零进程注入）、1% Low 帧率、CPU/GPU 温度与功耗、内存/显存占用以及黑鲨散热器转速。

- 主程序拆出 `PresentMon.exe` 后，未安装扩展的精简安装不再携带帧率采集器；既有性能浮窗外观/显示项偏好仍完整保留于配置文件中。
- 安装过程中只校验受保护目录 `Program Files\Alp Toolbox Extensions\Performance Overlay\v1\PresentMon.exe` 的精确 SHA-256，不从临时目录或环境 `PATH` 误加载未签名二进制。

---

## 安装与使用

1. 下载 [Alp-Performance-Overlay-setup-v1.exe](https://github.com/starsinking07/alp-toolbox-plugins/raw/main/plugins/performance-overlay/dist/Alp-Performance-Overlay-setup-v1.exe) 并校验 SHA-256 为 `6e3e6a771661e03b2be152366b444c678626bf55a55c9defa5e9b42757f7c6e3`。
2. 以管理员权限完成安装后，**从系统托盘右键「退出 Alp 工具箱」并重新打开工具箱**（或在「设置 → 扩展」先点击「⟳ 重新检测」确认状态后重启生效）。
3. 进入 **设置 → 扩展** 打开性能浮窗总开关，可随时配置显示项、布局（线性 / 双列 / 横向紧凑）、背景透明度、位置与全局热键（默认 `Ctrl+Alt+F3`）。

## 卸载方式

- **扩展卡片内**：在「设置 → 扩展」性能浮窗卡片右上角点击「卸载」；如扩展文件正被占用，请先退出工具箱再完成卸载。
- **系统控制面板**：在 Windows「设置 → 应用 → 已安装的应用」中找到 `Alp 性能浮窗扩展` 执行卸载。

## 许可协议

本扩展随附 Intel PresentMon 开源许可与版权声明，详见 [PresentMon-LICENSE.txt](licenses/PresentMon-LICENSE.txt) 与 [PresentMon-NOTICE.txt](licenses/PresentMon-NOTICE.txt)。
