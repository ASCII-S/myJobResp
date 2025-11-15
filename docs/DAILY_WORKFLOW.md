# 📅 每日知识库工作流程

## 概览

完整的知识库管理工作流程，包含学习、复习、同步和提交。

## 🌅 每日开始

### 1. 查看reviewsToday清单

```bash
# 生成reviewsToday清单
./system/scripts/kb.sh today
```

这会生成 `reviewsToday.md`，包含：
- 🔴 **已过期**：需要优先复习的笔记
- ⭐ **reviewsToday**：今天应该复习的笔记
- 📅 **本周计划**：本周内需要复习的笔记

### 2. 复习笔记

打开 `reviewsToday.md`，逐个复习笔记：

```markdown
## 🔴 已过期（优先复习）

- [ ] [CUDA Bank冲突](notes/cuda/Bank冲突.md)
  - 已复习: 2次 | 难度: medium

- [ ] [MoE模型基础](notes/MoE/MoE模型基础.md)
  - 已复习: 1次 | 难度: hard
```

**复习方式选择**：

#### 方式1：在清单中打勾（推荐！）
```markdown
- [x] [CUDA Bank冲突](notes/cuda/Bank冲突.md)  ✅ 改为 [x]
```

#### 方式2：手动修改复习次数
打开笔记文件，手动增加 `review_count`：
```yaml
---
review_count: 2  # 改为 3
difficulty: medium
---
```

## 📝 学习新内容

### 创建新笔记

```bash
# 从模板创建新笔记
./system/scripts/kb.sh new notes/新主题/新笔记.md

# 或创建种子笔记（碎片知识）
./system/scripts/kb.sh seed
```

### 编写笔记

笔记会自动包含元数据模板：
```yaml
---
title: 新笔记
created: 2024-10-19
tags: []
category: 
difficulty: medium
status: active
---
```

## 🌙 每日结束（关键！）

### 运行每日结束脚本

```bash
./system/end.sh
```

**自动执行的步骤**：

#### 1️⃣ 同步复习清单
- 读取 `reviewsToday.md` 中打勾的笔记（`- [x]`）
- 自动更新这些笔记的元数据：
  - `review_count + 1`
  - `last_reviewed = 今天`
  - 重新计算 `next_review`
  - 更新 `mastery_level`

#### 2️⃣ 修复元数据不一致 ⭐新增
- 检测手动修改 `review_count` 的笔记
- 自动更新这些笔记的时间戳：
  - `last_reviewed = 今天`
  - 基于 `review_count` 重新计算 `next_review`
  - 更新 `mastery_level`

#### 3️⃣ 初始化新笔记元数据
- 为新建的笔记添加完整的元数据
- 设置初始的 `next_review` 时间

#### 4️⃣ Git 提交和推送
- 自动提交所有笔记相关文件
- 推送到远程仓库

### 输出示例

```bash
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌙 每日结束 - 同步、修复、初始化、提交
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  🔄 同步复习清单中已勾选的笔记...
📋 发现 3 个已勾选的笔记

✅ 已标记为复习: CUDA Bank冲突.md
   复习次数: 2 → 3
   下次复习: 2024-10-26
   掌握程度: 50%

✅ 已标记为复习: MoE模型基础.md
   复习次数: 1 → 2
   下次复习: 2024-10-22
   掌握程度: 36%

✅ 成功更新: 3 个笔记

ℹ️  🔧 检查并修复元数据不一致（基于复习次数更新时间戳）...
🔍 扫描笔记文件...
📚 找到 150 篇笔记

⚠️  发现 2 篇笔记的元数据不一致

📄 Transformer注意力机制
   路径: notes/Transformer/注意力机制.md
   ⚠️  复习次数为 4，但缺少上次复习时间
   当前: review_count=4, last_reviewed=N/A, next_review=N/A
   ✅ 已修复

📊 总结:
  ✅ 已修复: 2 篇

ℹ️  ✨ 初始化/更新新建笔记的元数据...
✅ 成功初始化: 5 篇笔记

ℹ️  🐙 添加笔记相关文件到Git...
✅ 已添加 2 个路径

ℹ️  📝 准备提交...
✅ Git 提交并推送成功！

🎉 每日结束流程已完成！
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 📊 完整流程图

```
每日开始
  ↓
生成复习清单 (kb.sh today)
  ↓
复习笔记
  ├─ 方式1: 在清单中打勾 [x]
  └─ 方式2: 手动修改 review_count
  ↓
学习新内容 (可选)
  ├─ 创建新笔记
  └─ 编写内容
  ↓
每日结束 (./system/end.sh)
  ├─ 1. 同步复习清单（处理打勾的笔记）
  ├─ 2. 修复元数据不一致（处理手动修改的笔记）⭐
  ├─ 3. 初始化新笔记元数据
  └─ 4. Git 提交和推送
  ↓
完成！✅
```

## 🎯 两种复习方式对比

### 方式1：清单打勾（推荐）

**优点**：
- ✅ 简单快捷，只需改 `[ ]` 为 `[x]`
- ✅ 集中管理，在一个文件中操作
- ✅ 支持批量处理

**步骤**：
1. 在 `reviewsToday.md` 中打勾
2. 运行 `./system/end.sh` 自动同步

### 方式2：手动修改复习次数

**优点**：
- ✅ 灵活性高，可以精确控制
- ✅ 适合临时复习（不在清单中的笔记）
- ✅ 可以直接在笔记文件中操作

**步骤**：
1. 打开笔记，手动修改 `review_count: 2` → `3`
2. 运行 `./system/end.sh` 自动修复时间戳

## 💡 常见场景

### 场景1：只复习清单中的笔记

```bash
# 早上
./system/scripts/kb.sh today          # 生成清单
vim reviewsToday.md                       # 打勾复习

# 晚上
./system/end.sh                       # 自动同步+提交
```

### 场景2：临时复习其他笔记

```bash
# 浏览笔记时发现需要复习
vim notes/其他主题/某笔记.md
# 手动将 review_count: 3 改为 4

# 晚上
./system/end.sh                       # 自动修复时间戳+提交
```

### 场景3：创建新笔记

```bash
# 创建并编写新笔记
./system/scripts/kb.sh new notes/新主题/新笔记.md
vim notes/新主题/新笔记.md

# 晚上
./system/end.sh                       # 自动初始化元数据+提交
```

### 场景4：混合使用

```bash
# 早上：生成清单
./system/scripts/kb.sh today

# 白天：
# - 在清单中打勾复习部分笔记
# - 临时复习其他笔记（手动改 review_count）
# - 创建新笔记

# 晚上：一键处理所有情况
./system/end.sh
# ✅ 自动同步打勾的笔记
# ✅ 自动修复手动修改的笔记  ⭐新增
# ✅ 自动初始化新笔记
# ✅ 自动提交推送
```

## ⚡ 快捷命令汇总

```bash
# 复习相关
./system/scripts/kb.sh today          # 生成reviewsToday清单
./system/scripts/kb.sh sync           # 同步复习清单中已打勾的笔记
./system/scripts/kb.sh done <file>    # 标记单个笔记为已复习
./system/scripts/kb.sh fix            # 手动检查并修复元数据
./system/scripts/kb.sh fix --auto     # 自动修复所有不一致
./system/scripts/kb.sh stats          # 查看统计信息

# 笔记创建
./system/scripts/kb.sh new <file>     # 创建新笔记
./system/scripts/kb.sh seed           # 创建种子笔记

# 知识图谱和索引
./system/scripts/kb.sh graph          # 生成知识图谱
./system/scripts/kb.sh index          # 生成跨主题索引
./system/scripts/kb.sh report         # 生成统计报表

# 每日结束（最重要！）
./system/end.sh                       # 一键完成所有同步和提交
```

## 🔥 最佳实践

### 1. 每日结束必跑

**每天结束前务必运行**：
```bash
./system/end.sh
```

这是最重要的步骤！它会：
- 自动处理所有元数据更新
- 避免手动遗漏
- 保持数据一致性

### 2. 灵活选择复习方式

- **正常复习流程**：使用清单打勾
- **临时复习**：手动修改 `review_count`
- **混合使用**：两种方式可以同时使用，`end.sh` 都能处理

### 3. 定期检查

```bash
# 每周运行一次，查看统计
./system/scripts/kb.sh stats

# 偶尔检查元数据一致性
./system/scripts/kb.sh fix --dry-run
```

### 4. 充分利用自动化

- ✅ 不需要手动更新时间戳
- ✅ 不需要手动计算下次复习时间
- ✅ 不需要手动提交 Git
- ✅ 只需专注于学习和复习内容

## 🎉 总结

有了 `./system/end.sh` 的自动化流程，你只需要：

1. **早上**：运行 `kb.sh today` 生成清单
2. **白天**：专注复习和学习
   - 清单中打勾 ✓
   - 或手动改复习次数
3. **晚上**：运行 `./system/end.sh` 一键搞定！

**新增的元数据自动修复功能**让你可以：
- 随时随地手动复习笔记
- 不用担心忘记更新时间戳
- 系统每天自动帮你同步元数据
- 保证复习系统始终准确运行

专注学习，其他交给自动化！🚀

