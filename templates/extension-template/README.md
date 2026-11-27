# 从 Alp 扩展模板起步

这份模板包含扩展清单、NSIS 安装器和宿主卡片示例。先编译一个自己的安装包，再用已安装的载荷验证宿主接入。[完整开发指南](../../docs/plugin-dev-guide.md)

## 复制并提供载荷

在插件仓库根目录复制模板。以下以 `example-extension` 为例。

```powershell
Copy-Item templates/extension-template plugins/example-extension -Recurse
Set-Location plugins/example-extension
New-Item -ItemType Directory -Force payload, dist | Out-Null
```

将自己的 `ExampleExtension.exe` 放在复制后的 `payload/`。修改清单的名称、ID、适用版本及文件名。安装器的显示名、版本、卸载键和目录也应对应同一扩展。[清单模板](plugin.json) · [NSIS 模板](installer/extension-template.nsi)

## 生成安装包和校验文件

安装 NSIS 3 并让 `makensis` 可用。在复制后的扩展目录执行以下命令。

```powershell
makensis /INPUTCHARSET UTF8 installer/extension-template.nsi

$setup = Get-Item dist/Alp-Example-Extension-setup-v1.exe
$setupHash = (Get-FileHash $setup.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
$payloadHash = (Get-FileHash payload/ExampleExtension.exe -Algorithm SHA256).Hash.ToLowerInvariant()

$setupHash
$setup.Length
$payloadHash
"$setupHash  $($setup.Name)" | Set-Content -Encoding ascii dist/SHA256SUMS.txt
```

将三项输出依次填入 `sha256`、`size`、`payloadSha256`。按实际托管地址填写下载链接，替换 `example.invalid` 占位值。提交目录收录时，把清单条目同步到仓库根目录的 `catalog.json`。

## 验证卡片和卸载

卡片示例运行于具备扩展组件的 Alp 宿主源码中。由宿主传入已核验的安装状态、启停结果、获取与卸载回调。用「设置 → 扩展」查看状态，并验证 Windows 可以单独卸载自己的扩展。[宿主卡片示例](host-snippet/card_example.py)

回到插件仓库根目录运行 `py -3.14 -B scripts/verify_repo.py`。公开提交前，用自己的扩展名称和安装步骤替换这份模板说明。

[返回 Alp 扩展中心](../../README.md)
