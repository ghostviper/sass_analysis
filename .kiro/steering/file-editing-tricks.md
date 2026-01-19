# 文件编辑技巧与故障排除

## strReplace 失败的常见原因

`strReplace` 工具要求 `oldStr` 必须与文件内容**完全匹配**，包括：
- 每个空格、制表符
- 换行符
- 特殊字符编码（全角/半角标点）
- 不可见的空白字符

### 典型失败场景
1. 文件包含中文或特殊字符
2. 文件编码与预期不一致
3. 从 `readFile` 看到的内容与实际文件字节级别不一致
4. 多行字符串中的换行符差异（CRLF vs LF）

## 解决方案

### 方案1：重写整个文件（推荐用于大改动或中文内容）

```
1. fsWrite  - 创建文件，写入前 50-100 行
2. fsAppend - 追加后续内容（每次 50-100 行）
3. fsAppend - 继续追加直到完成
```

注意：`fsWrite` 内容太长时可能有问题，建议分多次 `fsAppend`。

### 方案2：诊断后重试 strReplace

用 PowerShell 查看文件实际内容：
```powershell
# 查看指定行范围
Get-Content "file.py" -Encoding UTF8 | Select-Object -Index (88..100)

# 查看文件编码
[System.IO.File]::ReadAllBytes("file.py")[0..10]
```

### 方案3：直接输出让用户手动复制

当多次尝试失败时，直接输出修改后的内容，让用户手动复制粘贴。

## 场景选择指南

| 场景 | 推荐方法 |
|------|----------|
| 小范围修改（几行纯ASCII代码） | `strReplace` |
| 涉及中文/特殊字符的修改 | `fsWrite` + `fsAppend` 重写 |
| 大范围重构（超过50行） | `fsWrite` + `fsAppend` 重写 |
| 修改反复失败时 | 直接输出内容让用户手动复制 |
| 新建文件 | `fsWrite` + `fsAppend` |

## 验证修改

修改完成后验证语法：
```powershell
# Python（使用 venv 下的 python）
# 项目 python 在 backend/venv 下，必须使用完整路径
backend\venv\Scripts\python.exe -m py_compile backend/curation/cli.py

# 或者先激活 venv
backend\venv\Scripts\activate
python -m py_compile backend/curation/cli.py

# TypeScript/JavaScript
npx tsc --noEmit path/to/file.ts
```

## 经验教训

1. 遇到 strReplace 连续失败2次以上，立即切换到重写策略
2. 中文内容的文件优先使用重写策略
3. 不要反复尝试相同的 strReplace，浪费时间
4. 大文件修改时，分段 append 比一次性写入更可靠
5. **fsWrite 和 fsAppend 必须提供 text 参数**，缺少 text 参数会导致 "aborted" 错误
6. 调用文件写入工具前，确认所有必需参数都已填写，不要遗漏
7. **Python 命令必须使用 venv**：项目的 python 在 `backend/venv` 下，运行时使用 `backend\venv\Scripts\python.exe` 而不是系统 `python`
