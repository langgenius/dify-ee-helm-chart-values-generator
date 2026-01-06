# CI 集成测试计划

> 待实施的 CI 集成测试增强计划

## 阶段 1: 添加非交互模式

在 `generate-values-prd.py` 添加 `--ci` 参数：

```python
parser.add_argument(
    "--ci", "--non-interactive",
    action="store_true",
    help="CI mode: use default values for all prompts"
)
```

修改 `utils/prompts.py` 中的提示函数，支持自动使用默认值。

## 阶段 2: 创建集成测试

```
tests/
├── conftest.py              # pytest 配置
├── test_integration.py      # 集成测试
└── profiles/
    └── standard.yaml        # 标准环境预设配置
```

**测试内容：**

| 测试项 | 说明 |
|--------|------|
| YAML 有效性 | 生成的文件是有效的 YAML |
| 必需字段检查 | 包含所有必需的配置项 |
| 版本特性验证 | 3.7+ 包含 triggerDomain 等 |
| 密钥生成验证 | 所有密钥已生成且长度正确 |

## 阶段 3: 更新 CI 配置

```yaml
# .github/workflows/ci.yml
integration-test:
  strategy:
    matrix:
      chart-version: ['3.6.0', '3.6.5', '3.7.0', '3.7.1', '3.7.2']
  steps:
    - name: Install Helm
      uses: azure/setup-helm@v3
    
    - name: Generate values for ${{ matrix.chart-version }}
      run: |
        python generate-values-prd.py \
          --chart-version ${{ matrix.chart-version }} \
          --ci --lang en
    
    - name: Validate generated YAML
      run: python -m pytest tests/test_integration.py
```

## 状态

- [ ] 阶段 1: 非交互模式
- [ ] 阶段 2: 集成测试
- [ ] 阶段 3: CI 配置更新

