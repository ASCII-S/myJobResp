#!/bin/bash
# 每日结束脚本
# 功能：
# 1. 同步更新复习元数据
# 2. 初始化新建问题文档
# 3. Git提交并推送

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌙 每日结束 - 同步更新并提交${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 步骤1: 同步更新复习元数据
echo -e "${BLUE}[1/4]${NC} 同步更新复习元数据..."
echo
./scripts/kb.sh sync
echo

# 步骤2: 初始化新建问题文档
echo -e "${BLUE}[2/4]${NC} 检查并初始化新建问题文档..."
echo
./scripts/kb.sh add-meta
echo

# 步骤3: Git add
echo -e "${BLUE}[3/4]${NC} 添加文件到Git..."
git add notes/ 面试大纲/
echo -e "${GREEN}✅ 文件已添加${NC}"
echo

# 步骤4: Git commit and push
echo -e "${BLUE}[4/4]${NC} 提交并推送..."

# 检查是否有改动
if git diff --cached --quiet; then
    echo -e "${YELLOW}ℹ️  没有需要提交的改动${NC}"
else
    # 生成提交信息
    DATE=$(date +"%Y-%m-%d")
    TIME=$(date +"%H:%M")
    
    # 统计改动
    MODIFIED=$(git diff --cached --numstat | wc -l)
    
    COMMIT_MSG="docs: 📚 每日学习更新 ${DATE} ${TIME}

- 更新了 ${MODIFIED} 个笔记文件
- 同步复习进度
- 初始化新笔记元数据

[自动提交]"
    
    git commit -m "$COMMIT_MSG"
    echo -e "${GREEN}✅ 已提交${NC}"
    echo
    
    # 推送到远程
    echo -e "${YELLOW}推送到远程仓库...${NC}"
    if git push; then
        echo -e "${GREEN}✅ 推送成功！${NC}"
    else
        echo -e "${RED}❌ 推送失败，请检查网络连接或手动推送${NC}"
        exit 1
    fi
fi

echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 今日学习已完成并同步！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo
echo -e "📊 查看今日统计: ${YELLOW}./scripts/kb.sh stats${NC}"
echo -e "📈 查看知识图谱: ${YELLOW}./scripts/kb.sh graph${NC}"
echo

