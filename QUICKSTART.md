# 快速开始指南

## 🎯 目标

将你的面试知识库部署到GitHub Pages，实现随时随地通过网页（包括手机）访问。

## ⚡ 快速部署（3步完成）

### 1️⃣ 初始化并提交到本地Git

```bash
cd /mnt/d/Document/Obsidian/MIS/2025summer/Jobs
git init
git add .
git commit -m "Initial commit: 面试准备知识库"
```

### 2️⃣ 在GitHub创建仓库并推送

```bash
# 1. 访问 https://github.com/new 创建新仓库
#    - 仓库名：interview-knowledge-base（或你喜欢的名字）
#    - 可见性：Public（公开）
#    - 不要勾选任何初始化选项

# 2. 关联并推送（替换成你的用户名和仓库名）
git remote add origin https://github.com/你的用户名/interview-knowledge-base.git
git branch -M main
git push -u origin main
```

### 3️⃣ 启用GitHub Pages

```bash
# 在GitHub仓库页面：
# Settings → Pages → Source → 选择 "main" 分支 → Save
```

## ✅ 完成！

等待3-5分钟后，访问：
```
https://你的用户名.github.io/仓库名/
```

## 📱 在手机上使用

1. **用手机浏览器打开上面的网址**
2. **添加到主屏幕**（可以像APP一样使用）
   - iOS: 分享按钮 → 添加到主屏幕
   - Android: 菜单 → 添加到主屏幕

## 🔄 如何更新内容

修改文档后：
```bash
git add .
git commit -m "更新内容"
git push
```

GitHub会自动重新部署（约3-5分钟生效）。

## 📚 更多详细说明

查看完整的部署指南：[DEPLOY.md](DEPLOY.md)

## 🎨 已配置的功能

✅ 响应式设计（自动适配手机、平板、电脑）  
✅ 全文搜索  
✅ 侧边栏导航  
✅ 代码高亮和一键复制  
✅ 图片点击放大  
✅ 字数统计和阅读时间  
✅ 上下篇导航  
✅ Markdown链接自动跳转  

## 💡 提示

- 所有Markdown文档的相对链接都能正常工作
- 搜索功能支持中英文
- 移动端已优化，滑动和点击都很流畅
- 可以离线添加到主屏幕使用（PWA特性）

---

**遇到问题？** 查看 [DEPLOY.md](DEPLOY.md) 的常见问题部分

