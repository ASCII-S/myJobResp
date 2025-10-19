# 🎓 终身学习知识库 - 工作流总结

## 🌟 系统特点

- ✅ **极简操作**：只需2个核心命令
- ✅ **自动归档**：历史复习清单自动保存
- ✅ **批量更新**：一次命令更新所有笔记
- ✅ **智能算法**：间隔重复 + 掌握度评估
- ✅ **易于维护**：完全自动化的元数据管理

---

## ⚡ 快速开始（3步）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化现有笔记

```bash
./scripts/kb.sh add-meta
```

### 3. 开始每日复习

```bash
./scripts/kb.sh today
```

---

## 📋 日常工作流（推荐使用一键脚本）

### 🌅 每天早上（1分钟）

**一键脚本（推荐）**：
```bash
./start.sh
```

或手动运行：
```bash
./scripts/kb.sh today
```

这会：
1. 自动归档昨天的复习清单到 `今日复习归档/年/月/`
2. 生成新的 `📅今日复习.md`
3. 显示需要复习的笔记统计

### 📖 全天复习（碎片时间）

在 `📅今日复习.md` 中边复习边打勾：

```markdown
- [x] [Bank冲突的概念](notes/cuda/Bank冲突.md)  ✓
- [x] [虚函数实现](notes/C++/虚函数.md)  ✓
- [ ] [Transformer架构](notes/Transformer/架构.md)
```

### 🌙 每天晚上（2分钟）

**一键脚本（推荐）**：
```bash
./end.sh
```

自动完成：
- ✅ 同步更新所有打勾笔记的元数据
- ✅ 初始化新建问题文档的元数据
- ✅ Git add + commit + push

或手动运行：
```bash
./scripts/kb.sh sync
./scripts/kb.sh add-meta
git add notes/ 面试大纲/
git commit -m "更新学习进度"
git push
```

---

## 🆕 添加新笔记时

### 1. 创建笔记文件

```bash
# 创建大纲
vim 面试大纲/新主题.md

# 创建原子问题
mkdir notes/新主题
vim notes/新主题/问题1.md
vim notes/新主题/问题2.md
```

### 2. 初始化元数据

```bash
./scripts/kb.sh add-meta
```

---

## 📂 目录结构

```
/home/ikun/Learn/Jobs/
├── 📅今日复习.md              # 当前复习清单
├── 今日复习归档/              # 历史清单归档
│   └── 2025/10/
│       ├── 2025-10-19.md
│       └── 2025-10-20.md
├── notes/                     # 原子问题笔记
│   ├── cuda/
│   ├── C++/
│   └── ...
├── 面试大纲/                  # 主题大纲
│   ├── cuda.md
│   └── ...
└── scripts/                   # 自动化脚本
    └── kb.sh                 # 快捷命令
```

---

## 🎯 两个核心脚本（一键操作）

| 命令         | 时机     | 作用                                                       |
| ------------ | -------- | ---------------------------------------------------------- |
| `./start.sh` | 每天早上 | 生成复习清单 + 自动归档 + **智能排序（易→难）** + TopK限制 |
| `./end.sh`   | 每天晚上 | 同步元数据 + 初始化新笔记 + Git提交推送                    |

### ✨ 新功能：智能排序与TopK限制

复习清单现在会：
- ✅ **智能排序**：将容易复习的放在前面（从易到难）
- ✅ **TopK限制**：默认显示前20篇，避免压力过大
- ✅ **显示详情**：标签数、难度、复习次数等
- ✅ **优先级指标**：难度小 > 复习次数多 > 创建时间新 > 标签多

📖 **详细说明**: 查看 [`SMART_REVIEW_SORT.md`](SMART_REVIEW_SORT.md)

**就这么简单！** ✨

### 或使用单独命令

| 命令                       | 作用         |
| -------------------------- | ------------ |
| `./scripts/kb.sh today`    | 生成复习清单 |
| `./scripts/kb.sh sync`     | 同步元数据   |
| `./scripts/kb.sh add-meta` | 初始化新笔记 |

---

## 📚 详细文档

- **快速上手**：
  - [`DAILY_SCRIPTS.md`](DAILY_SCRIPTS.md) - **每日脚本使用说明（推荐阅读）**
  - [`SIMPLE_WORKFLOW.md`](SIMPLE_WORKFLOW.md) - 简化工作流详解
  - [`scripts/QUICKSTART.md`](scripts/QUICKSTART.md) - 5分钟快速开始

- **功能说明**：
  - [`WORKFLOW_CHECK.md`](WORKFLOW_CHECK.md) - 功能检查报告
  - [`WORKFLOW_EXAMPLE.md`](WORKFLOW_EXAMPLE.md) - 详细使用示例
  - [`KNOWLEDGE_BASE_GUIDE.md`](KNOWLEDGE_BASE_GUIDE.md) - 完整功能指南

- **技术文档**：
  - [`scripts/README.md`](scripts/README.md) - 所有命令详解
  - [`AUTOMATION_SYSTEM.md`](AUTOMATION_SYSTEM.md) - 系统架构
  - [`config/kb_config.yaml`](config/kb_config.yaml) - 配置选项

- **其他**：
  - [`PATH_UPDATE.md`](PATH_UPDATE.md) - 路径变更说明
  - [`BUGFIX.md`](BUGFIX.md) - Bug修复记录
  - [`NEW_FEATURE.md`](NEW_FEATURE.md) - 新功能说明

---

## 🔧 可选命令

虽然日常只需2个命令，但这些在特定场景也很有用：

```bash
./scripts/kb.sh stats        # 查看统计
./scripts/kb.sh graph        # 生成知识图谱
./scripts/kb.sh report       # 生成报表
./scripts/kb.sh link <file>  # 生成相关链接
./scripts/kb.sh help         # 查看所有命令
```

---

## ✨ 核心优势

### 1. 自动归档 📦
每次生成新清单时，自动归档旧的到 `今日复习归档/年/月/日期.md`

### 2. 批量更新 ⚡
一次命令更新所有打勾的笔记，无需逐个操作

### 3. 智能算法 🧠
- 间隔重复算法（Spaced Repetition）
- 自动计算下次复习时间
- 自动评估掌握程度

### 4. 完全自动 🤖
所有元数据自动管理，无需手动编辑

### 5. 极度简单 👍
只需记住2个命令，符合自然工作流

---

## 🎓 使用建议

### 每天固定时间
- 早上8点：`./scripts/kb.sh today`
- 晚上9点：`./scripts/kb.sh sync`

### 及时打勾
复习完立即打勾，避免遗漏

### 周末回顾
- 查看统计报表
- 生成知识图谱
- 调整学习重点

---

## 🚀 开始使用

```bash
# 1. 初始化现有笔记
./scripts/kb.sh add-meta

# 2. 每天早上
./start.sh

# 3. 全天复习，在 📅今日复习.md 中打勾

# 4. 每天晚上
./end.sh
```

**祝您学习愉快！** 🎉

---

## 📞 帮助

- 查看所有命令：`./scripts/kb.sh help`
- 阅读详细文档：查看上述文档列表
- 配置选项：编辑 `config/kb_config.yaml`

**Happy Learning! 📚**

