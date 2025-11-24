# PR Review Bot 使用指南

## 概述

本项目已配置了自动化的 PR Review 机器人，当有新的 Pull Request 创建或更新时，会自动进行代码质量检查。

## 功能特性

PR Review 机器人会自动检查以下内容：

### 1. Python 代码检查

- **flake8**: 代码风格检查（PEP 8）
  - 最大行长度：120 字符
  - 忽略 E203, W503 错误（与 black 格式化工具兼容）

- **pylint**: 代码质量检查
  - 检查代码复杂度
  - 检查潜在的 bug
  - 检查代码规范

- **black**: 代码格式检查
  - 检查代码是否符合 black 格式化标准
  - 行长度：120 字符

### 2. YAML 文件验证

- **yamllint**: YAML 文件格式检查
  - 检查 YAML 语法
  - 检查缩进和格式
  - 最大行长度：200 字符

- **Python YAML 解析**: 验证 YAML 文件是否可以正确解析

### 3. Shell 脚本检查

- **shellcheck**: Shell 脚本静态分析（如果已安装）
  - 检查 shell 脚本的潜在问题
  - 提供最佳实践建议

### 4. 安全检查

- 检测硬编码的密码、API 密钥等敏感信息
- 提醒潜在的安全问题

## 工作流程

1. 当 PR 被创建、更新或标记为 ready for review 时，GitHub Actions 会自动触发
2. 机器人会检查所有变更的文件（`.py`, `.yaml`, `.yml`, `.sh`）
3. 检查结果会以评论的形式发布到 PR 中
4. 如果发现问题，会在 GitHub Actions 中显示警告，但不会阻止 PR 合并

## 本地运行检查

在提交 PR 之前，你可以在本地运行这些检查：

### 安装开发依赖

```bash
pip install -r requirements-dev.txt
```

### 运行代码检查

```bash
# flake8 检查
flake8 . --max-line-length=120 --extend-ignore=E203,W503

# pylint 检查
pylint *.py modules/ utils/ i18n/ --max-line-length=120

# black 格式检查
black --check --line-length=120 .

# 自动格式化代码（如果需要）
black --line-length=120 .

# YAML 检查
yamllint -d .yamllint.yml *.yaml
```

### Shell 脚本检查（可选）

```bash
# macOS
brew install shellcheck

# Ubuntu/Debian
sudo apt-get install shellcheck

# 运行检查
shellcheck *.sh
```

## 配置文件说明

### `.flake8`

flake8 配置文件，定义了代码风格检查规则。

### `.pylintrc`

pylint 配置文件，定义了代码质量检查规则。

### `.yamllint.yml`

yamllint 配置文件，定义了 YAML 文件检查规则。

## 常见问题

### Q: 检查失败会阻止 PR 合并吗？

A: 不会。检查结果会以警告的形式显示，但不会阻止 PR 合并。不过，建议修复所有问题后再合并。

### Q: 如何忽略某些检查？

A: 
- 对于 Python 代码，可以使用 `# noqa` 或 `# pylint: disable=xxx` 注释
- 对于 YAML 文件，可以在 `.yamllint.yml` 中配置忽略规则

### Q: 如何更新检查规则？

A: 修改对应的配置文件（`.flake8`, `.pylintrc`, `.yamllint.yml`），然后提交到仓库。

### Q: 机器人会在所有 PR 上运行吗？

A: 是的，但不会在 draft PR 上运行。只有当 PR 标记为 ready for review 时才会运行。

## 自定义配置

如果需要修改检查规则，可以编辑以下文件：

- `.github/workflows/pr-review.yml`: GitHub Actions workflow 配置
- `.flake8`: flake8 配置
- `.pylintrc`: pylint 配置
- `.yamllint.yml`: yamllint 配置

## 贡献

如果你有改进建议，欢迎提交 PR！

