# Example Template Generation Requests

## Example 1: Low Followers, High Revenue

**Observation**:
```
低粉丝但高收入的产品
```

**Guidance**:
```
寻找产品驱动而非IP驱动的案例，证明产品力能直接变现
```

**Command**:
```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "低粉丝但高收入的产品" \
  --guidance "寻找产品驱动而非IP驱动的案例" \
  --count 2
```

## Example 2: Weekend Launchable Projects

**Observation**:
```
可以在周末快速启动的项目
```

**Guidance**:
```
低门槛、MVP清晰、技术复杂度低的产品，适合快速验证想法
```

**Command**:
```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "可以在周末快速启动的项目" \
  --guidance "低门槛、MVP清晰、技术复杂度低" \
  --count 3
```

## Example 3: Vertical Niche Success

**Observation**:
```
服务小众垂直市场但成功的产品
```

**Guidance**:
```
精准定位特定人群，市场虽小但付费意愿强
```

**Command**:
```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "服务小众垂直市场但成功的产品" \
  --guidance "精准定位特定人群，市场虽小但付费意愿强" \
  --count 2
```

## Example 4: No-AI Profitable

**Observation**:
```
不依赖AI技术但盈利的产品
```

**Guidance**:
```
传统技术解决真实问题，证明AI不是必需品
```

**Command**:
```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "不依赖AI技术但盈利的产品" \
  --guidance "传统技术解决真实问题" \
  --count 2
```

## Example 5: Pricing Innovation

**Observation**:
```
通过创新定价模式成功的产品
```

**Guidance**:
```
一次性买断、按用量付费等非标准订阅模式
```

**Command**:
```bash
backend\venv\Scripts\python.exe backend/skills/ai-template-generator/scripts/generate_template.py \
  --observation "通过创新定价模式成功的产品" \
  --guidance "一次性买断、按用量付费等非标准订阅模式" \
  --count 2
```

## Tips for Better Results

1. **Be specific in observations**: "低粉丝高收入" > "成功的产品"
2. **Provide clear guidance**: Explain what pattern you're looking for
3. **Consider user personas**: Who would benefit from this template?
4. **Think about insights**: What non-obvious takeaway should users get?
5. **Check data availability**: Ensure filters can be applied to existing data
