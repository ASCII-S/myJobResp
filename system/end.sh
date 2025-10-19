#!/bin/bash
# 每日结束脚本（system内部版本）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌙 每日结束 - 同步、初始化、提交${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 1. 同步复习清单
info "🔄 同步复习清单中已勾选的笔记..."
python system/scripts/review_manager.py sync || {
    error "同步失败"
    exit 1
}
echo

# 2. 初始化新笔记元数据
info "✨ 初始化/更新新建笔记的元数据..."
python system/scripts/add_metadata.py || {
    error "初始化元数据失败"
    exit 1
}
echo

# 3. Git操作
info "🐙 Git add, commit, push..."
git add .

COMMIT_MESSAGE="Daily knowledge base update: $(date +'%Y-%m-%d')"
git commit -m "$COMMIT_MESSAGE" || {
    warning "没有新改动或commit失败，跳过推送"
    exit 0
}

git push || {
    error "Git push失败"
    exit 1
}

success "✅ Git 提交并推送成功！"
echo

success "🎉 每日结束流程已完成！"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
