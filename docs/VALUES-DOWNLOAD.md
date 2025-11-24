# Values.yaml 动态下载功能

## 概述

为了确保用户始终使用最新版本的 `values.yaml` 配置文件，脚本现在支持从官方 Dify Helm Chart 仓库自动下载 `values.yaml` 文件。

## 功能特点

- ✅ **自动下载**: 如果本地不存在 `values.yaml`，自动从官方仓库下载
- ✅ **版本管理**: 支持指定特定版本的 Chart
- ✅ **缓存机制**: 下载的文件缓存在 `.cache/` 目录，避免重复下载
- ✅ **Helm 命令**: 使用 Helm 命令从官方仓库下载（Helm 为必选依赖）
- ✅ **灵活使用**: 支持使用本地文件或强制重新下载

## 使用方式

### 1. 自动下载最新版本（推荐）

```bash
python generate-values-prd.py
```

脚本会自动：
1. 检查本地是否存在 `values.yaml`
2. 如果不存在，从 Helm Chart 仓库下载最新版本
3. 将文件保存到 `.cache/values-latest.yaml`
4. 使用该文件进行配置生成

### 2. 指定版本

```bash
python generate-values-prd.py --chart-version 3.5.6
```

下载指定版本的 `values.yaml` 并保存到 `.cache/values-3.6.0.yaml`。

### 3. 使用本地文件

如果你已经手动下载了 `values.yaml`，可以使用 `--local` 参数（必须同时指定版本）：

```bash
python generate-values-prd.py --local --chart-version 3.5.6
```

### 4. 强制重新下载

如果需要获取最新版本，可以强制重新下载：

```bash
python generate-values-prd.py --force-download
```

## 下载机制

### Helm 命令（必选）

脚本需要 Helm 才能正常工作。脚本会：

1. 检查 Helm 是否已安装，如果未安装会提示安装并退出
2. 添加 Dify Helm Chart 仓库：
   ```bash
   helm repo add dify-helm https://langgenius.github.io/dify-helm
   helm repo update dify-helm
   ```

3. 使用 `helm show values` 获取 values.yaml：
   ```bash
   helm show values dify-helm/dify --version <version>
   ```

**注意**: 如果 Helm 未安装，脚本会显示安装说明并退出，不会尝试其他下载方式。

## 缓存机制

下载的 `values.yaml` 文件会缓存在 `.cache/` 目录：

```
.cache/
├── values-latest.yaml      # 最新版本
├── values-3.6.0.yaml       # 特定版本
└── values-3.5.0.yaml       # 其他版本
```

**缓存策略：**
- 如果缓存文件存在且未使用 `--force-download`，直接使用缓存
- 使用 `--force-download` 会忽略缓存，重新下载

## 版本管理

### 获取可用版本列表

如果使用 Helm，可以查看可用版本：

```bash
helm repo add dify-helm https://langgenius.github.io/dify-helm
helm repo update dify-helm
helm search repo dify-helm/dify --versions
```

### 版本格式

版本号格式通常为：`3.6.0`、`3.6.0-beta.1` 等。

## 故障排除

### 问题 1: 无法下载 values.yaml

**可能原因：**
- Helm 未安装（必选依赖）
- 网络连接问题
- Helm 配置错误

**解决方案：**
1. **安装 Helm**（必选）：https://helm.sh/docs/intro/install/
2. 检查网络连接
3. 手动下载 values.yaml 并使用 `--local --chart-version <version>` 参数

### 问题 2: 版本不存在

**可能原因：**
- 指定的版本不存在
- 版本号格式错误

**解决方案：**
1. 使用 `helm search repo dify-helm/dify --versions` 查看可用版本
2. 不指定版本，使用最新版本

### 问题 3: 缓存文件损坏

**解决方案：**
```bash
# 删除缓存目录
rm -rf .cache/

# 重新运行脚本
python generate-values-prd.py --force-download
```

## 最佳实践

1. **定期更新**: 建议定期使用 `--force-download` 获取最新版本
2. **版本锁定**: 生产环境建议指定具体版本，避免自动更新
3. **本地备份**: 重要配置建议保存本地备份
4. **版本验证**: 下载后检查版本是否符合预期

## 技术细节

### 下载流程

```
1. 检查命令行参数
   ├─ --local → 使用本地文件
   ├─ --version → 指定版本下载
   └─ 默认 → 下载最新版本

2. 检查本地文件
   ├─ 存在 → 使用本地文件
   └─ 不存在 → 继续下载流程

3. 检查缓存
   ├─ 存在且未强制下载 → 使用缓存
   └─ 不存在或强制下载 → 继续下载

4. 下载文件
   ├─ 检查 Helm 是否安装
   │  ├─ 未安装 → 显示安装说明并退出
   │  └─ 已安装 → 使用 Helm 命令下载
   │     ├─ 成功 → 保存到缓存
   │     └─ 失败 → 报错退出

5. 使用下载的文件生成配置
```

### 文件结构

```
项目根目录/
├── generate-values-prd.py    # 主脚本
├── values.yaml               # 本地文件（可选）
├── .cache/                   # 缓存目录
│   ├── values-latest.yaml
│   └── values-<version>.yaml
└── values-prd.yaml          # 生成的配置文件
```

## 相关链接

- [Dify Helm Chart 仓库](https://langgenius.github.io/dify-helm)
- [Helm 官方文档](https://helm.sh/docs/)
- [GitHub 仓库](https://github.com/langgenius/dify-helm)

