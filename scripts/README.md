# 📚 知识库自动化脚本使用指南

## 🎯 功能概览

本知识库提供了一套完整的自动化管理系统，帮助你：

- ✅ 自动生成每日复习清单
- ✅ 追踪学习进度和掌握程度
- ✅ 发现知识点之间的关联
- ✅ 可视化知识图谱
- ✅ 生成学习统计报表

---

## 📦 环境准备

### 安装Python依赖

```bash
pip install pyyaml jieba
```

### 配置说明

配置文件位于 `config/kb_config.yaml`，可以自定义：
- 复习间隔策略
- 自动链接阈值
- 统计报表选项
- 等等

---

## 🔧 核心脚本

### 1. 复习管理器 (`review_manager.py`)

#### 生成今日复习清单

```bash
python scripts/review_manager.py today
```

输出：`📅今日复习.md`

#### 同步复习清单（推荐方式 ⭐）

```bash
# 在复习清单中打勾后，批量同步
python scripts/review_manager.py sync
```

**工作流**：
1. 生成复习清单：`python scripts/review_manager.py today`
2. 在 `📅今日复习.md` 中，将复习完的笔记打勾（`- [x]`）
3. 运行同步命令：`python scripts/review_manager.py sync`

这会自动更新所有打勾笔记的元数据：
- `last_reviewed`: 更新为今天
- `review_count`: 自动 +1
- `next_review`: 根据间隔算法计算
- `mastery_level`: 根据复习频率计算

#### 标记单个文档为已复习

```bash
# 复习完某个笔记后
python scripts/review_manager.py mark-done "notes/cuda/Bank冲突的概念.md"
```

效果同上，但只处理单个文件。

#### 设置文档难度

```bash
python scripts/review_manager.py set-difficulty "notes/cuda/Bank冲突.md" hard
```

难度影响复习间隔：
- `easy`: 间隔较长（适合已掌握的内容）
- `medium`: 标准间隔（默认）
- `hard`: 间隔较短（需要频繁复习）

#### 查看统计信息

```bash
python scripts/review_manager.py stats
```

---

### 2. 自动链接生成器 (`auto_link.py`)

#### 为单个文档生成相关笔记

```bash
python scripts/auto_link.py update "notes/cuda/Bank冲突的概念.md"
```

自动：
- 基于关键词和标签找到相关文档
- 在文档底部更新"相关笔记"区块

#### 更新所有文档的相关笔记

```bash
python scripts/auto_link.py update-all
```

⚠️ 注意：这可能需要较长时间

#### 生成跨主题索引

```bash
python scripts/auto_link.py index
```

输出：`面试大纲/_知识点索引.md`

列出在多个主题中都出现的知识点，帮助建立跨领域连接。

---

### 3. 知识图谱生成器 (`knowledge_graph.py`)

#### 生成所有格式

```bash
python scripts/knowledge_graph.py --all
```

输出：
- `docs/knowledge_graph.html` - 交互式可视化图谱
- `面试大纲/_知识图谱.md` - 文本版索引

#### 只生成HTML可视化

```bash
python scripts/knowledge_graph.py --html
```

#### 只生成文本索引

```bash
python scripts/knowledge_graph.py --text
```

---

### 4. 统计报表生成器 (`stats_generator.py`)

#### 生成统计报表

```bash
python scripts/stats_generator.py
```

输出：`面试大纲/_统计报表.md`

报表包含：
- 总体学习统计
- 复习状态分析
- 主题分布情况
- 掌握度排行
- 学习趋势分析
- 个性化建议

---

## 📋 日常工作流

### 每天早上（5分钟）

```bash
# 1. 生成今日复习清单
python scripts/review_manager.py today

# 2. 打开清单
open "📅今日复习.md"
```

### 复习完笔记后

**推荐方式（批量）**：
```bash
# 在复习清单中打勾，然后同步
python scripts/review_manager.py sync
```

**单个标记**：
```bash
python scripts/review_manager.py mark-done "notes/路径/笔记.md"
```

### 创建新笔记时

1. 使用模板：`templates/note_template.md`
2. 填写内容
3. 运行自动链接（可选）：

```bash
python scripts/auto_link.py update "新笔记路径.md"
```

### 每周日（30分钟）

```bash
# 1. 查看统计报表
python scripts/stats_generator.py
open "面试大纲/_统计报表.md"

# 2. 生成知识图谱
python scripts/knowledge_graph.py --all
open "docs/knowledge_graph.html"

# 3. 查看跨主题索引
python scripts/auto_link.py index
```

---

## 🤖 GitHub Actions 自动化

系统配置了GitHub Actions，会自动：

### 每次push时
- 更新复习清单
- 重新生成知识图谱
- 更新跨主题索引
- 生成最新统计报表

### 每天UTC 0点（北京时间8点）
- 自动运行所有脚本
- 自动提交更新

**无需手动操作，推送代码即可！**

---

## 📊 文档元数据说明

每个笔记文档应包含以下frontmatter：

```yaml
---
created: 2025-10-19              # 创建日期
last_reviewed: 2025-10-19        # 最后复习日期（自动更新）
next_review: 2025-10-20          # 下次复习日期（自动计算）
review_count: 0                  # 复习次数（自动递增）
difficulty: medium               # 难度：easy/medium/hard
mastery_level: 0.0               # 掌握程度：0.0-1.0（自动计算）
tags: [cuda, memory, optimization]  # 标签
related_outlines: []             # 相关大纲
---
```

### 哪些字段会自动更新？

- ✅ `last_reviewed` - 每次标记为已复习
- ✅ `next_review` - 根据间隔算法计算
- ✅ `review_count` - 自动递增
- ✅ `mastery_level` - 根据复习频率计算

### 哪些字段需要手动维护？

- ⚙️ `created` - 创建时填写
- ⚙️ `difficulty` - 可以随时调整
- ⚙️ `tags` - 手动添加标签
- ⚙️ `related_outlines` - 手动添加相关大纲

---

## 🔄 批量添加元数据

如果你有很多现有笔记还没有添加元数据，可以使用：

```bash
python scripts/add_metadata.py
```

这会：
1. 扫描所有没有frontmatter的笔记
2. 自动添加基础元数据
3. 保留原有内容

---

## 🐛 常见问题

### Q: 脚本运行出错？

**A**: 检查是否安装了依赖：
```bash
pip install pyyaml jieba
```

### Q: GitHub Actions没有自动运行？

**A**: 确保：
1. 仓库设置中开启了Actions
2. 有权限提交代码（检查 GITHUB_TOKEN）

### Q: 复习间隔不合理？

**A**: 编辑 `config/kb_config.yaml` 调整间隔策略

### Q: 自动链接推荐不准确？

**A**: 调整 `config/kb_config.yaml` 中的：
- `similarity_threshold`: 相似度阈值（0-1）
- `keyword_weight`: 关键词权重
- `tag_weight`: 标签权重

### Q: 想要不同的统计周期？

**A**: 使用 `--days` 参数：
```bash
python scripts/stats_generator.py --days 60
```

---

## 📚 进阶技巧

### 1. 结合Git Hooks

创建 `.git/hooks/post-commit`：

```bash
#!/bin/bash
# 每次提交后自动生成复习清单
python scripts/review_manager.py today
```

### 2. 定时提醒

使用cron或系统任务调度：

```bash
# crontab -e
0 8 * * * cd /path/to/Jobs && python scripts/review_manager.py today
```

### 3. 集成到编辑器

在VSCode中配置Tasks：

```json
{
  "label": "标记为已复习",
  "type": "shell",
  "command": "python scripts/review_manager.py mark-done ${file}"
}
```

---

## 🎯 最佳实践

1. **保持简单**：不要过度优化，重点是持续使用
2. **定期复习**：每天花15分钟处理复习清单
3. **及时标记**：复习完立即标记，形成习惯
4. **关注趋势**：每周看一次统计报表
5. **适时调整**：根据实际情况调整难度和间隔

---

## 📝 反馈与改进

如果你有任何建议或遇到问题，欢迎：
1. 修改配置文件
2. 调整脚本参数
3. 贡献代码改进

**记住：工具是为人服务的，找到最适合自己的工作流！**

