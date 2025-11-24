# 开发工作流程 (Development Workflow)

## 分支策略

**重要：所有开发工作都在 `dev` 分支进行**

- `main` 分支：稳定版本，只接受来自 `dev` 分支的合并
- `dev` 分支：开发分支，所有新功能和修复都在此分支开发

### 分支切换

```bash
# 切换到 dev 分支
git checkout dev

# 如果 dev 分支不存在，创建并切换
git checkout -b dev

# 从 main 分支创建 dev 分支（首次创建）
git checkout -b dev main
```

## Git 提交规范

### 基本原则

**每次功能修改后都要提交到 Git**

这是一个重要的开发习惯，有助于：
- 保持代码历史清晰
- 便于回滚和问题追踪
- 提高团队协作效率
- 确保代码变更可追溯

### 提交时机

在以下情况下应该提交：

1. ✅ **完成一个功能模块** - 功能实现完成后立即提交
2. ✅ **修复一个 Bug** - Bug 修复后立即提交
3. ✅ **重构代码** - 代码重构完成后提交
4. ✅ **添加新文件** - 新增文件后提交
5. ✅ **更新文档** - 文档更新后提交
6. ✅ **配置变更** - 配置文件修改后提交

### 提交信息格式

使用约定式提交（Conventional Commits）格式：

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### Type 类型

- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具链相关
- `config`: 配置变更

#### 示例

```bash
# 新功能
git commit -m "feat: 添加 Helm Chart 版本选择功能"

# Bug 修复
git commit -m "fix: 修复 Helm 命令构建问题"

# 文档更新
git commit -m "docs: 更新 README 使用说明"

# 代码重构
git commit -m "refactor: 提取配置常量为全局变量"

# 配置变更
git commit -m "config: 更新 .gitignore 规则"
```

### 提交前检查清单

提交前确保：

- [ ] 代码通过语法检查
- [ ] 没有引入明显的 Bug
- [ ] 相关文档已更新（如需要）
- [ ] 提交信息清晰明确
- [ ] 只提交相关的变更（避免一次性提交过多不相关的修改）

### 工作流程示例

#### 场景 1: 添加新功能

```bash
# 1. 创建功能分支（如需要）
git checkout -b feat/new-feature

# 2. 编写代码
# ... 编写代码 ...

# 3. 检查状态
git status

# 4. 添加文件
git add .

# 5. 提交
git commit -m "feat: 添加新功能描述"

# 6. 推送到远程（如需要）
git push origin feat/new-feature
```

#### 场景 2: 修复 Bug

```bash
# 1. 修复 Bug
# ... 修复代码 ...

# 2. 测试验证
# ... 测试 ...

# 3. 提交
git add .
git commit -m "fix: 修复 Helm 命令构建问题"
```

#### 场景 3: 重构代码

```bash
# 1. 重构代码
# ... 重构 ...

# 2. 验证功能正常
# ... 测试 ...

# 3. 提交
git add .
git commit -m "refactor: 提取配置常量为全局变量，提高可维护性"
```

### 提交频率建议

- **小功能/修复**: 完成后立即提交
- **大功能**: 可以分阶段提交，每个阶段完成后提交一次
- **文档更新**: 可以批量提交，但建议及时提交

### 避免的做法

❌ **不要**：
- 累积大量修改后一次性提交
- 提交不相关的多个功能
- 提交包含调试代码或注释掉的代码
- 提交包含敏感信息（密码、密钥等）

✅ **应该**：
- 每个功能完成后立即提交
- 保持提交信息清晰
- 确保提交的代码可以正常工作
- 遵循提交规范

### 工具辅助

可以使用 Git hooks 来自动检查：

```bash
# .git/hooks/pre-commit
#!/bin/bash
# 运行语法检查
python3 -m py_compile $(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')
```

### 总结

**核心原则：每次功能修改后都要提交到 Git**

这有助于：
- 保持代码历史清晰
- 便于问题追踪和回滚
- 提高开发效率
- 确保代码变更可追溯

