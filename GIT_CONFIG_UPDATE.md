# 🔧 Git提交配置改进

## 📅 更新日期
2025-10-19

## ✨ 改进内容

### 问题
之前 `system/end.sh` 中硬编码了要提交的目录：
```bash
git add notes/
git add 面试大纲/
git add outlines/
# ... 等等
```

### 解决方案
现在从配置文件 `kb_config.yaml` 动态读取路径！

## ⚙️ 配置方式

### 1. 在 `kb_config.yaml` 中配置路径

#### 方式一：使用 `paths` 配置（推荐）

```yaml
# config/kb_config.yaml
paths:
  notes_dir: "notes"           # 笔记目录
  outlines_dir: "面试大纲"      # 大纲目录
```

这些目录会自动被添加到Git提交中。

#### 方式二：使用 `git_auto_commit.include_paths` 配置（额外）

```yaml
# config/kb_config.yaml
git_auto_commit:
  enabled: true
  commit_message_template: "chore: 更新复习记录 - {date}"
  
  # 额外包含的路径
  include_paths:
    - "notes/"
    - "面试大纲/"
    - "outlines/"
    - "今日复习.md"
    - "今日复习归档/"
    - "config/kb_config.yaml"
```

### 2. 自动合并

脚本会：
1. 从 `paths` 读取 `notes_dir` 和 `outlines_dir`
2. 从 `git_auto_commit.include_paths` 读取额外路径
3. 自动去重
4. 只添加实际存在的目录

## 📊 工作流程

```bash
./end.sh
```

内部流程：
```
1. 同步复习进度
   ↓
2. 初始化新笔记元数据
   ↓
3. 从配置文件读取路径
   ↓
4. 只添加配置的目录到Git
   ↓
5. 检查是否有改动
   ↓
6. 提交并推送（如有改动）
```

## ✅ 优点

### 1. 灵活配置
- ✅ 不同用户可以有不同的目录结构
- ✅ 通过配置文件控制，不需要修改脚本

### 2. 避免误提交
- ✅ 只提交配置的笔记相关目录
- ✅ 不会提交系统文件、临时文件等
- ✅ 保持Git历史干净

### 3. 易于自定义
- ✅ 修改配置文件即可
- ✅ 支持多个目录
- ✅ 支持添加/删除路径

## 🎯 使用示例

### 示例1：标准配置

```yaml
# config/kb_config.yaml
paths:
  notes_dir: "notes"
  outlines_dir: "面试大纲"

git_auto_commit:
  include_paths:
    - "今日复习.md"
    - "今日复习归档/"
```

提交时会包含：
- `notes/`
- `面试大纲/`
- `今日复习.md`
- `今日复习归档/`

### 示例2：自定义目录

如果您重命名了目录：

```yaml
# config/kb_config.yaml
paths:
  notes_dir: "my-notes"        # 自定义笔记目录
  outlines_dir: "outlines"     # 英文大纲目录

git_auto_commit:
  include_paths:
    - "daily-review.md"        # 自定义复习文件名
    - "archive/"               # 自定义归档目录
```

### 示例3：添加更多目录

```yaml
# config/kb_config.yaml
git_auto_commit:
  include_paths:
    - "notes/"
    - "面试大纲/"
    - "docs/"                  # 添加文档目录
    - "projects/"              # 添加项目目录
    - "resources/"             # 添加资源目录
```

## 🔍 查看添加了哪些路径

脚本会输出：
```
✅ 已添加 7 个路径
```

您可以在提交前检查：
```bash
git status
```

## 🛡️ 容错处理

如果配置文件读取失败，脚本会：
1. 输出警告信息
2. 回退到默认路径（`notes/` 和 `面试大纲/`）
3. 继续执行，不会中断

## 📝 注意事项

### 1. 路径格式
- 使用相对路径（相对于项目根目录）
- 目录路径建议以 `/` 结尾
- 文件路径直接写文件名

### 2. 路径必须存在
- 只有实际存在的路径才会被添加
- 不存在的路径会被自动跳过

### 3. 配置优先级
- 用户配置 `config/kb_config.yaml` 优先
- 如果不存在，使用模板配置 `system/config/kb_config.yaml`

## 🎉 测试结果

```bash
./end.sh

# 输出：
✅ 已添加 7 个路径
📝 准备提交...
Daily knowledge base update: 2025-10-19
✅ Git 提交并推送成功！
```

## 💡 最佳实践

### 推荐配置

在 `config/kb_config.yaml` 中保持简洁：

```yaml
# 只配置必要的路径
paths:
  notes_dir: "notes"
  outlines_dir: "面试大纲"

git_auto_commit:
  enabled: true
  include_paths:
    - "今日复习.md"
    - "今日复习归档/"
    - "config/kb_config.yaml"  # 提交配置变更
```

### 不推荐提交的内容

以下目录/文件不应该添加到 `include_paths`：
- ❌ `system/` - 系统脚本目录
- ❌ `.git/` - Git目录
- ❌ `__pycache__/` - Python缓存
- ❌ `*.tmp` - 临时文件
- ❌ `.DS_Store` - 系统文件

（这些已经在 `.gitignore` 中忽略）

---

**改进完成！** 🎉

现在 Git 提交完全由配置文件控制，灵活且安全！

