# GitHub Pages 部署指南

本文档说明如何将此文档库部署到GitHub Pages。

## 前置准备

1. 拥有GitHub账号
2. 本地安装Git
3. 已完成的文档内容（面试大纲和notes文件夹）

## 部署步骤

### 1. 初始化Git仓库（如果还未初始化）

```bash
cd /mnt/d/Document/Obsidian/MIS/2025summer/Jobs
git init
```

### 2. 创建.gitignore文件（可选）

创建`.gitignore`文件，排除不需要上传的文件：

```bash
# 在项目根目录创建.gitignore
cat > .gitignore << EOF
# 系统文件
.DS_Store
Thumbs.db

# 简历相关（如果不想公开）
简历/

# 临时文件
*.tmp
*.log
EOF
```

### 3. 添加文件到Git

```bash
# 添加所有必要的文件
git add .nojekyll
git add index.html
git add _sidebar.md
git add README.md
git add 面试大纲/
git add notes/

# 提交
git commit -m "Initial commit: 添加面试大纲文档"
```

### 4. 在GitHub上创建仓库

1. 登录GitHub
2. 点击右上角 `+` 号，选择 `New repository`
3. 仓库名称建议：`interview-preparation` 或 `job-interview-docs`
4. 选择 `Public`（如果想公开）或 `Private`（如果想保密）
5. **不要**勾选 `Add a README file`（因为我们已经有了）
6. 点击 `Create repository`

### 5. 连接远程仓库并推送

```bash
# 添加远程仓库（替换YOUR_USERNAME和REPO_NAME为你的实际值）
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

### 6. 启用GitHub Pages

1. 进入GitHub仓库页面
2. 点击 `Settings`（设置）
3. 在左侧菜单找到 `Pages`
4. 在 `Source` 下拉菜单中选择 `main` 分支
5. 目录选择 `/ (root)`
6. 点击 `Save`

### 7. 等待部署完成

- GitHub会自动部署，通常需要1-3分钟
- 部署完成后，会显示网站地址：`https://YOUR_USERNAME.github.io/REPO_NAME/`
- 点击链接访问你的文档网站！

## 更新文档

当你修改了文档内容后，执行以下命令更新：

```bash
# 添加修改的文件
git add .

# 提交修改
git commit -m "更新文档内容"

# 推送到GitHub
git push
```

GitHub Pages会自动重新部署，1-3分钟后就能看到更新。

## 自定义域名（可选）

如果你有自己的域名：

1. 在仓库根目录创建 `CNAME` 文件
2. 文件内容写入你的域名，如：`docs.yourdomain.com`
3. 在你的域名DNS设置中添加CNAME记录指向 `YOUR_USERNAME.github.io`

## 故障排除

### 网站显示404
- 检查GitHub Pages是否已启用
- 确认分支和目录选择正确
- 等待3-5分钟让部署完成

### 样式或链接不正常
- 检查`.nojekyll`文件是否存在
- 确认所有文件路径使用相对路径
- 检查文件名是否正确（区分大小写）

### 文档内容不更新
- 清除浏览器缓存
- 等待几分钟让GitHub Pages重新部署
- 检查git push是否成功

## 本地预览

如果想在本地预览效果：

```bash
# 安装简单的HTTP服务器（如果还没有）
# Python 3
python3 -m http.server 3000

# 或者使用Node.js的http-server
# npm install -g http-server
# http-server -p 3000
```

然后在浏览器访问：`http://localhost:3000`

## 项目结构

```
Jobs/
├── .nojekyll              # 告诉GitHub Pages不使用Jekyll
├── index.html             # Docsify配置和入口
├── README.md              # 首页内容
├── _sidebar.md            # 侧边栏导航
├── DEPLOY.md              # 本部署说明
├── 面试大纲/               # 面试大纲文档
│   ├── C++.md
│   ├── cuda.md
│   └── ...
└── notes/                 # 详细笔记（链接目标）
    ├── C++/
    ├── cuda/
    └── ...
```

## 注意事项

1. **不要上传敏感信息**：简历、证件等个人信息建议不要上传到公开仓库
2. **文件名规范**：避免使用中文文件名在URL中可能出现编码问题
3. **链接相对路径**：确保文档间的链接使用相对路径
4. **移动端测试**：部署后在手机上测试显示效果

## 许可证

如果是公开仓库，建议添加LICENSE文件说明使用许可。

---

祝部署顺利！🎉

