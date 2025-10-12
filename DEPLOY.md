# GitHub Pages 部署指南

本文档介绍如何将面试知识库部署到GitHub Pages，使其可以通过网页访问。

## 📋 前置要求

1. 拥有GitHub账号
2. 已安装Git
3. 已在本地完成知识库的配置

## 🚀 部署步骤

### 步骤1：初始化Git仓库

如果还没有初始化Git仓库，在项目根目录执行：

```bash
# 进入项目目录
cd /mnt/d/Document/Obsidian/MIS/2025summer/Jobs

# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: 面试准备知识库"
```

### 步骤2：在GitHub上创建仓库

1. 登录GitHub
2. 点击右上角的 `+` 号，选择 `New repository`
3. 填写仓库信息：
   - **Repository name**: 例如 `interview-knowledge-base`
   - **Description**: 面试准备知识库
   - **Visibility**: 
     - **Public**: 公开（任何人都可以访问）
     - **Private**: 私有（只有你和授权的人可以访问，GitHub Pro账号可以为私有仓库启用Pages）
   - ❌ 不要勾选 "Initialize this repository with a README"
4. 点击 `Create repository`

### 步骤3：关联远程仓库并推送

```bash
# 关联远程仓库（将下面的URL替换为你自己的仓库地址）
git remote add origin https://github.com/你的用户名/interview-knowledge-base.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 步骤4：启用GitHub Pages

1. 在GitHub仓库页面，点击 `Settings`（设置）
2. 在左侧菜单中找到 `Pages`
3. 在 `Source` 部分：
   - **Branch**: 选择 `main`
   - **Folder**: 选择 `/ (root)`
4. 点击 `Save`
5. 等待几分钟，GitHub Pages会自动构建并部署

### 步骤5：访问你的知识库

部署完成后，你的知识库将可以通过以下地址访问：

```
https://你的用户名.github.io/仓库名/
```

例如：
```
https://username.github.io/interview-knowledge-base/
```

GitHub会显示实际的访问地址，在Settings > Pages页面可以看到。

## 📱 移动端访问

部署成功后，你可以：

1. **直接在手机浏览器访问上述URL**
2. **添加到主屏幕**（推荐）：
   - iOS Safari: 点击分享按钮 → "添加到主屏幕"
   - Android Chrome: 菜单 → "添加到主屏幕"

## 🔄 更新内容

当你修改了文档内容后，只需要：

```bash
# 查看修改
git status

# 添加修改的文件
git add .

# 提交
git commit -m "更新：描述你的修改"

# 推送到GitHub
git push
```

GitHub Pages会自动检测到更改并重新部署（通常需要几分钟）。

## ⚙️ 高级配置

### 自定义域名（可选）

如果你有自己的域名：

1. 在Settings > Pages中，找到 `Custom domain`
2. 输入你的域名（如 `interview.yourdomain.com`）
3. 在域名服务商处添加CNAME记录，指向 `你的用户名.github.io`

### 启用HTTPS

GitHub Pages默认支持HTTPS，建议勾选 `Enforce HTTPS` 选项。

### 修改主题颜色

编辑 `index.html`，修改这一行：

```javascript
themeColor: '#42b983',  // 改为你喜欢的颜色
```

### 添加Google Analytics（可选）

如果想统计访问量，可以在 `index.html` 中添加：

```javascript
window.$docsify = {
  // ... 其他配置
  ga: 'UA-XXXXXXXXX-X',  // 你的GA跟踪ID
}
```

然后在plugins部分添加：
```html
<script src="//cdn.jsdelivr.net/npm/docsify/lib/plugins/ga.min.js"></script>
```

## 🔒 隐私保护

`.gitignore` 文件已经配置为忽略简历等个人隐私文件。推送前请确认：

```bash
# 查看将要推送的文件
git status

# 如果看到隐私文件，立即添加到.gitignore
echo "隐私文件路径" >> .gitignore
git add .gitignore
git commit -m "更新.gitignore"
```

## ❓ 常见问题

### Q1: 404 Not Found

**原因**: GitHub Pages还在构建中，或者分支/文件夹选择错误

**解决**: 
- 等待3-5分钟
- 检查Settings > Pages中的Source配置
- 确保仓库根目录有 `index.html` 文件

### Q2: 链接跳转失败

**原因**: Markdown链接路径问题

**解决**: 
- 确保 `.nojekyll` 文件存在
- 使用相对路径
- Docsify会自动处理 `.md` 后缀

### Q3: 样式显示异常

**原因**: CDN加载失败或浏览器缓存

**解决**: 
- 清除浏览器缓存
- 尝试使用不同的CDN源
- 检查浏览器控制台的错误信息

### Q4: 私有仓库能用GitHub Pages吗？

**解答**: 
- 免费账号：只能为公开仓库启用Pages
- GitHub Pro账号：可以为私有仓库启用Pages

### Q5: 如何禁止搜索引擎收录？

在仓库根目录创建 `robots.txt`：

```
User-agent: *
Disallow: /
```

## 📊 本地预览

推送到GitHub之前，可以在本地预览：

```bash
# 方法1：Python
python3 -m http.server 3000

# 方法2：Node.js
npx http-server -p 3000

# 方法3：VS Code Live Server扩展
# 右键index.html → Open with Live Server
```

然后访问 `http://localhost:3000`

## 🎉 完成

恭喜！你的面试知识库现在已经可以在任何设备上通过网页访问了！

记得把访问链接保存到手机浏览器的书签或添加到主屏幕，方便随时查看。

---

**需要帮助？** 

- Docsify文档: https://docsify.js.org
- GitHub Pages文档: https://docs.github.com/pages

