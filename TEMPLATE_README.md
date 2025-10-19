# 📚 知识库管理系统

> 一个智能的个人知识库管理系统，支持间隔重复、自动复习、知识图谱可视化

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

## ✨ 特性

- 🧠 **智能复习系统**: 基于间隔重复算法，自动计算最佳复习时间
- 📊 **智能排序**: 将容易复习的内容放在前面，从易到难，避免心态失衡
- 🎯 **TopK限制**: 避免一次显示过多内容，默认20篇，可配置
- 🔗 **自动关联**: 发现笔记之间的关联，自动推荐相关内容
- 📈 **知识图谱**: 可视化知识网络，了解学习全貌
- 📝 **元数据管理**: 自动追踪复习次数、掌握度、难度等
- 🚀 **简单易用**: 每天两个命令，轻松管理知识库

## 🚀 快速开始

### 前置要求

- Python 3.7+
- Git（推荐）

### 安装

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/knowledge-base-template.git my-knowledge-base
cd my-knowledge-base

# 2. 运行初始化
chmod +x system_init_template.sh
./system_init_template.sh

# 3. 完成！开始使用
./start.sh
```

## 💡 使用方法

### 每日工作流

```bash
# ☀️ 早上：生成今日复习清单
./start.sh

# 📖 复习：打开 今日复习.md，边复习边打勾 [x]

# 🌙 晚上：同步进度并提交
./end.sh
```

### 常用命令

```bash
./kb today              # 生成今日复习清单
./kb sync               # 同步复习进度
./kb mark-done <file>   # 标记单个笔记为已复习
./kb set-difficulty <file> <easy/medium/hard>
./kb stats              # 查看学习统计
./kb graph              # 生成知识图谱
./kb link               # 自动发现关联
```

## 📂 项目结构

```
my-knowledge-base/
├── system/                  # 系统脚本（模板部分）
│   ├── scripts/            # Python脚本
│   ├── config/             # 默认配置
│   ├── templates/          # 笔记模板
│   ├── docs/               # 文档
│   ├── start.sh            # 每日开始
│   └── end.sh              # 每日结束
│
├── notes/                   # 您的笔记
│   ├── topic1/
│   └── topic2/
│
├── outlines/                # 您的大纲
│   ├── outline1.md
│   └── outline2.md
│
├── config/                  # 您的配置（覆盖默认）
│   └── kb_config.yaml
│
├── examples/                # 示例笔记
│
├── start.sh                 # 快捷启动（调用system/）
├── end.sh                   # 快捷结束（调用system/）
└── kb                       # 快捷命令
```

## ⚙️ 配置

编辑 `config/kb_config.yaml` 自定义设置：

```yaml
# 每日复习数量限制
daily_review:
  max_today: 20              # 今日最多显示20篇
  max_overdue: 10            # 过期最多显示10篇
  
  # 排序权重（调整优先级）
  sort_weights:
    difficulty_easy: 3.0     # 难度权重（越大越优先）
    review_count: 2.0        # 复习次数权重
    created_new: 1.0         # 创建时间权重
    tags_count: 0.5          # 标签数量权重

# 复习间隔（天数）
review_intervals:
  easy: [1, 3, 7, 15, 30, 60, 120]
  medium: [1, 2, 5, 10, 21, 45, 90]
  hard: [1, 1, 3, 7, 14, 30, 60]
```

## 📝 创建笔记

使用模板创建新笔记：

```bash
cp system/templates/note_template.md notes/新主题/新笔记.md
```

笔记格式（YAML frontmatter）：

```markdown
---
created: 2025-10-19
difficulty: medium
tags:
  - 主题标签
  - 相关标签
---

# 笔记标题

## 内容

...
```

## 📊 智能排序功能

复习清单会自动按优先级排序，将**容易复习的放在前面**：

1. **难度小的优先** (权重3.0) - easy > medium > hard
2. **复习次数多的优先** (权重2.0) - 熟悉的内容
3. **创建时间新的优先** (权重1.0) - 记忆清晰
4. **标签多的优先** (权重0.5) - 关联性强

**效果**：从易到难，建立信心，避免心态失衡 ✨

## 📚 文档

- [安装指南](system/docs/INSTALLATION.md)
- [使用手册](system/docs/USER_GUIDE.md)
- [自定义指南](system/docs/CUSTOMIZATION.md)
- [开发文档](system/docs/DEVELOPMENT.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

[MIT License](LICENSE)

## 💬 反馈与支持

- 问题反馈：[GitHub Issues](https://github.com/your-username/knowledge-base-template/issues)
- 讨论交流：[GitHub Discussions](https://github.com/your-username/knowledge-base-template/discussions)

## 🌟 致谢

感谢所有贡献者和使用者！

---

**开始构建您的终身学习知识库吧！** 🚀

