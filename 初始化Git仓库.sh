#!/bin/bash
# Git 仓库初始化和推送脚本

echo "================================"
echo "GitHub Pages 部署初始化脚本"
echo "================================"
echo ""

# 检查是否已经初始化Git
if [ -d ".git" ]; then
    echo "✓ Git 仓库已存在"
else
    echo "正在初始化 Git 仓库..."
    git init
    echo "✓ Git 仓库初始化完成"
fi

echo ""
echo "添加文件到 Git..."
git add .nojekyll
git add index.html
git add _sidebar.md
git add README.md
git add DEPLOY.md
git add QUICKSTART.md
git add PROJECT_STRUCTURE.md
git add preview.sh
git add .gitignore
git add 面试大纲/
git add notes/

echo "✓ 文件添加完成"
echo ""

# 显示状态
echo "当前 Git 状态:"
git status --short

echo ""
echo "================================"
echo "下一步操作："
echo "================================"
echo ""
echo "1. 提交更改:"
echo "   git commit -m \"Initial commit: 面试大纲文档\""
echo ""
echo "2. 在 GitHub 上创建新仓库"
echo "   访问: https://github.com/new"
echo ""
echo "3. 连接远程仓库并推送:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 在 GitHub 仓库设置中启用 GitHub Pages"
echo "   Settings → Pages → Source: main 分支"
echo ""
echo "详细说明请查看 QUICKSTART.md 和 DEPLOY.md"
echo ""
