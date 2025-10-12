# 快速开始指南

## 🚀 快速部署到GitHub Pages

### 步骤1: 初始化Git仓库

```bash
cd /mnt/d/Document/Obsidian/MIS/2025summer/Jobs
git init
git add .
git commit -m "Initial commit: 面试大纲文档"
```

### 步骤2: 创建GitHub仓库

1. 访问 [GitHub](https://github.com) 并登录
2. 点击右上角 `+` → `New repository`
3. 填写仓库名称，例如：`interview-docs`
4. 选择 `Public` 或 `Private`
5. **不要**勾选任何初始化选项
6. 点击 `Create repository`

### 步骤3: 推送代码

```bash
# 替换下面的 YOUR_USERNAME 和 REPO_NAME
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

### 步骤4: 启用GitHub Pages

1. 进入你的GitHub仓库页面
2. 点击 `Settings` → `Pages`
3. Source 选择 `main` 分支
4. 目录选择 `/ (root)`
5. 点击 `Save`

### 步骤5: 访问你的网站

等待1-3分钟后，访问：
```
https://YOUR_USERNAME.github.io/REPO_NAME/
```

## 📱 本地预览

在部署之前，你可以在本地预览效果：

```bash
# 方法1: 使用提供的脚本
./preview.sh

# 方法2: 使用Python
python3 -m http.server 3000

# 方法3: 使用Node.js
npx http-server -p 3000
```

然后访问：`http://localhost:3000`

## 📝 更新文档

当你修改文档后：

```bash
git add .
git commit -m "更新内容"
git push
```

## 📂 项目文件说明

- `index.html` - Docsify配置，网站入口
- `_sidebar.md` - 侧边栏导航配置
- `README.md` - 首页内容
- `.nojekyll` - 禁用Jekyll处理
- `.gitignore` - Git忽略文件（排除简历等敏感信息）
- `面试大纲/` - 所有面试大纲文档
- `notes/` - 详细笔记（被面试大纲引用）

## ⚠️ 注意事项

1. **隐私保护**：`.gitignore`已配置忽略`简历/`目录，避免个人信息泄露
2. **公开/私密**：如果仓库是Private，GitHub Pages需要GitHub Pro账号
3. **链接测试**：部署后测试所有文档链接是否正常工作
4. **移动端**：在手机上测试显示效果

## 🔧 自定义配置

### 修改主题颜色

编辑 `index.html`，找到：

```css
:root {
  --theme-color: #42b983;  /* 修改这里的颜色 */
}
```

### 修改侧边栏

编辑 `_sidebar.md`，添加或删除导航链接

### 修改首页

编辑 `README.md`，自定义首页内容

## 📚 更多信息

详细部署指南请参考：[DEPLOY.md](DEPLOY.md)

---

祝你面试顺利！💪

