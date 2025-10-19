# ⚡ 快速开始 - 5分钟上手知识库自动化

## 第一步：安装依赖 (1分钟)

```bash
pip install -r requirements.txt
```

## 第二步：为现有笔记添加元数据 (2分钟)

```bash
# 预览将要处理的文件
./scripts/kb.sh add-meta

# 确认后会自动添加
```

## 第三步：生成今日复习清单 (1分钟)

```bash
./scripts/kb.sh today
```

查看生成的 `今日复习.md`

## 第四步：开始复习！

### 💡 推荐方式（批量打勾）

1. 在 `今日复习.md` 中，将复习完的笔记打勾：
   ```markdown
   - [x] [Bank冲突的概念](notes/cuda/Bank冲突.md)  ✓ 已复习
   ```

2. 复习完成后，运行同步命令：
   ```bash
   ./scripts/kb.sh sync
   ```

这会自动更新所有打勾笔记的元数据！

### 其他方式（单个标记）

```bash
./scripts/kb.sh done notes/cuda/某个笔记.md
```

---

## 🎉 完成！

你已经成功设置好知识库自动化系统。

### 接下来每天只需：

1. 早上运行：`./scripts/kb.sh today`
2. 打开 `今日复习.md`，边复习边打勾
3. 复习完成后：`./scripts/kb.sh sync`

**就这么简单！** ✨

### 每周一次（可选）：

```bash
# 一键生成所有报表
./scripts/kb.sh update-all
```

---

## 📚 更多功能

- 查看所有命令：`./scripts/kb.sh help`
- 详细文档：`scripts/README.md`
- 完整指南：`KNOWLEDGE_BASE_GUIDE.md`

**开始你的学习之旅吧！🚀**

