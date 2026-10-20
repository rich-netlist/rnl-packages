# RNL 公开包

[English](README.md)

RNL 标准系列及 `rnl-zh` 留在 rnl，仍由查看器内置。本仓库保存以下可选包；包文件、示例和各包 README 保留原始字节。

| 包 | 版本 | 分类 |
| --- | --- | --- |
| analog-canvas-extensions | 0.1 | 扩展 |
| eda-symbol | 0.1 | 扩展 |
| eda-style | 0.1 | 扩展 |
| pdk-sky130 | 0.1 | 工艺库 |

使用 git-filter-repo 从 rnl main 导入上述四个目录和 `scripts/pdk/` 的历史，并将包目录改为 `packages/包名/版本/`。确切来源提交及校验器版本见 `rnl-revision.txt`。各包 README 保持原样。

## 使用

清单地址：<https://rich-netlist.github.io/rnl-packages/catalog.json>。每版文件的永久地址为 `https://rich-netlist.github.io/rnl-packages/packages/包名/版本/包名.rnl`。

网页版查看器选择 **File → Include Public Package…**，文件头写：

```spice
* @RNL(type="header") { @VERSION("0.3"); @USE-PACKAGE(name="eda-symbol", version="0.1") }
```

命令行按清单 URL 下载并校验原始字节的 SHA-256，然后使用 `rnl check circuit.sp --path /下载目录/packages/eda-symbol/0.1`。`rnl render` 同样使用 `--path`；依赖包需要分别提供目录。

## 清单格式

`catalog.json` 由 `python scripts/catalog.py` 生成，不手写。顶层 `schemaVersion` 为 `1`，`packages` 数组逐一记录每个包的每个版本：

- `name`、`version` 必须与头段一致。RNL 0.3 第 16.2 节规定版本是 `major.minor`，每个 0.x 自成主版本，不使用第三段版本或 preview 后缀。
- `kind` 为 `extension` 或 `pdk`；`summary.zh`、`summary.en` 从 `metadata.json` 生成。
- `url`、`sha256` 是主包文件的永久地址和原始字节 SHA-256 小写十六进制。
- `path` 保留旧库相对路径，便于旧查看器状态和图库兼容；`description` 是原包首段简介；`source` 是 GitHub 源文件链接。
- `assets` 记录版本目录内所有文件，包括 README 和示例，每项有相对 `path`、永久 `url`、原始字节 `sha256`。

消费端必须拒绝未知格式和 hash 不符；相对 URL 以清单 URL 为基准（供离线测试使用）。最新版本按数字比较两段；固定版本按精确名字、版本及锁定 hash 选择。已发布记录及资产不可删除或修改，包括简介元数据。CI 与 PR 目标分支或 main 的前一个提交比较，防止篡改，并确认提交的清单确由文件生成。

## 发布新版本

1. 新建分支，将包复制到新的 `packages/包名/major.minor/`，只修改新版本的头段和内容，保留旧版本及其元数据。
2. 新包在 `metadata.json` 增加分类、兼容路径和中英文简介；已有包保留元数据。
3. 执行 `python scripts/catalog.py` 和 `python scripts/catalog.py --check --base origin/main`，审阅 URL、hash 和清单差异。
4. 提英文 PR。CI 用 `rnl-revision.txt` 中固定的完整提交读取所有版本、检查无错误并绘制每个符号；还运行 `sky130.py --check` 验证 PDK 示例和桩模型。
5. 审核合并后 main 工作流发布 GitHub Pages，保留全部旧版本。验证线上清单和 hash。此流程不发布 npm 或 tag。

升级校验器时，仅将 `rnl-revision.txt` 改为审阅过的完整 rnl 提交并运行 CI。校验采用固定源码、`Cargo.lock`（`cargo build --locked`）和查看器同款 WebAssembly 渲染器。仓库 Pages 设置选择 **GitHub Actions**；静态文件允许跨站访问，供 rnl 网站及嵌入查看器使用。

`packages/**` 使用 CC0-1.0；脚本、配置和根文档使用 MIT，见 `REUSE.toml` 与 `LICENSES/`。
