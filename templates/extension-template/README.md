# 自制扩展起步模板 (`extension-template`)

将本目录完整复制为 `plugins/<your-extension-slug>/`，即可作为独立扩展的初始骨架：

1. 修改 `plugin.json` 中的 `id`、`name`、`description`、`installerName`、`installDir` 与 `downloadUrl`；
2. 参考 `installer/extension-template.nsi` 修改安装目录名、注册表卸载项与打包文件清单，编译生成安装包放入 `dist/`；
3. 计算安装包与核心载荷的小写 64 位 SHA-256，更新 `dist/SHA256SUMS.txt`、`plugin.json` 与仓库根目录 [catalog.json](../../catalog.json)；
4. 若需要向主仓库贡献「设置 → 扩展」卡片接入代码，可对照 [host-snippet/card_example.py](host-snippet/card_example.py) 使用宿主内置的 `ExtensionCard` 与 `make_extension_subcard()`；
5. 提交前在仓库根目录运行 `python scripts/verify_repo.py` 确认零报错。

完整开发说明详见 [自制扩展与插件开发教程](../../docs/plugin-dev-guide.md)。
