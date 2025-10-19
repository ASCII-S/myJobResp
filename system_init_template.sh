#!/bin/bash
# 知识库初始化脚本（给新用户使用）
# 这是一个模板，展示新用户如何快速开始

set -e

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
echo -e "${GREEN}📚 知识库管理系统 - 初始化${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 1. 检查依赖
info "1️⃣ 检查系统依赖..."

if ! command -v python3 &> /dev/null; then
    error "需要 Python 3.7+"
    exit 1
fi
success "Python $(python3 --version)"

if ! command -v git &> /dev/null; then
    warning "未安装 Git（可选，但推荐安装）"
else
    success "Git $(git --version)"
fi

echo

# 2. 安装Python依赖
info "2️⃣ 安装Python依赖..."

if [ -f "system/requirements.txt" ]; then
    pip install -q -r system/requirements.txt
    success "Python依赖安装完成"
else
    warning "未找到 requirements.txt"
fi

echo

# 3. 创建目录结构
info "3️⃣ 创建目录结构..."

mkdir -p notes
mkdir -p outlines
mkdir -p docs
mkdir -p 今日复习归档

success "目录创建完成"
echo

# 4. 配置文件
info "4️⃣ 设置配置文件..."

if [ ! -f "config/kb_config.yaml" ]; then
    mkdir -p config
    if [ -f "system/config/kb_config.yaml" ]; then
        cp system/config/kb_config.yaml config/kb_config.yaml
        success "已创建配置文件: config/kb_config.yaml"
        warning "请根据需要修改配置"
    fi
else
    info "配置文件已存在，跳过"
fi

echo

# 5. 创建示例笔记
info "5️⃣ 创建示例笔记..."

if [ -f "system/templates/note_template.md" ]; then
    if [ ! -f "notes/示例笔记.md" ]; then
        cp system/templates/note_template.md notes/示例笔记.md
        success "已创建示例笔记: notes/示例笔记.md"
    else
        info "示例笔记已存在，跳过"
    fi
fi

echo

# 6. Git配置
info "6️⃣ Git配置..."

if [ ! -d ".git" ]; then
    read -p "是否初始化Git仓库？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        
        # 创建.gitignore
        if [ -f "system/.gitignore.template" ]; then
            cp system/.gitignore.template .gitignore
        else
            cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*.so

# 临时文件
*.tmp
*.bak
.cache/

# 每日复习（可选忽略）
# 今日复习.md

# 复习归档
今日复习归档/

# 系统文件
.DS_Store
Thumbs.db
GITIGNORE
        fi
        
        success "Git仓库已初始化"
        info "建议添加远程仓库: git remote add origin <url>"
    fi
else
    info "Git仓库已存在，跳过"
fi

echo

# 7. 完成
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 初始化完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

info "📖 下一步操作："
echo "  1. 编辑配置: nano config/kb_config.yaml"
echo "  2. 创建笔记: 参考 notes/示例笔记.md"
echo "  3. 开始使用: ./start.sh"
echo "  4. 查看文档: cat system/docs/README.md"
echo

info "💡 常用命令:"
echo "  ./start.sh         # 每天早上，生成复习清单"
echo "  ./end.sh           # 每天晚上，同步并提交"
echo "  ./kb today         # 生成今日复习"
echo "  ./kb sync          # 同步复习进度"
echo "  ./kb stats         # 查看统计"
echo

success "祝您学习愉快！📚"
echo

