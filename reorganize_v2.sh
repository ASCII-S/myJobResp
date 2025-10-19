#!/bin/bash
# 知识库模板化重组脚本 v2
# 方案一：单仓库分离

set -e

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
echo -e "${GREEN}📚 知识库模板化重组 - 方案一（单仓库分离）${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

warning "建议先提交或备份当前状态！"
echo "将要执行的操作："
echo "  1. 创建 system/ 目录结构"
echo "  2. 移动系统文件到 system/"
echo "  3. 保留 config/ 作为用户配置"
echo "  4. 重命名 面试大纲/ 为 outlines/"
echo "  5. 创建启动脚本和快捷命令"
echo

read -p "是否继续？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    error "已取消"
    exit 1
fi

echo

# ==================== 步骤1：创建system目录 ====================
info "1️⃣ 创建system目录结构..."
mkdir -p system/scripts
mkdir -p system/config
mkdir -p system/templates
mkdir -p system/docs
mkdir -p system/.github/workflows
success "目录创建完成"
echo

# ==================== 步骤2：移动脚本 ====================
info "2️⃣ 移动脚本文件..."
if [ -d "scripts" ]; then
    mv scripts/*.py system/scripts/ 2>/dev/null || true
    mv scripts/*.sh system/scripts/ 2>/dev/null || true
    mv scripts/*.md system/docs/ 2>/dev/null || true
    rmdir scripts 2>/dev/null || true
    success "脚本文件已移动"
else
    warning "scripts目录不存在"
fi
echo

# ==================== 步骤3：移动配置模板 ====================
info "3️⃣ 复制配置模板..."
if [ -d "config" ]; then
    # 复制到system作为模板
    cp -r config/* system/config/ 2>/dev/null || true
    success "配置模板已创建"
    info "保留 config/ 作为您的个人配置"
else
    warning "config目录不存在"
fi
echo

# ==================== 步骤4：移动模板 ====================
info "4️⃣ 移动模板文件..."
if [ -d "templates" ]; then
    mv templates/* system/templates/ 2>/dev/null || true
    rmdir templates 2>/dev/null || true
    success "模板文件已移动"
else
    warning "templates目录不存在"
fi
echo

# ==================== 步骤5：移动系统脚本 ====================
info "5️⃣ 移动系统脚本..."
[ -f "start.sh" ] && mv start.sh system/start_original.sh
[ -f "end.sh" ] && mv end.sh system/end_original.sh
[ -f "requirements.txt" ] && mv requirements.txt system/
success "系统脚本已移动"
echo

# ==================== 步骤6：移动文档 ====================
info "6️⃣ 移动文档到system/docs/..."
[ -f "README_WORKFLOW.md" ] && mv README_WORKFLOW.md system/docs/
[ -f "TEMPLATE_PLAN.md" ] && mv TEMPLATE_PLAN.md system/docs/
[ -f "TEMPLATE_README.md" ] && mv TEMPLATE_README.md system/docs/TEMPLATE_README.md
[ -f "system_init_template.sh" ] && mv system_init_template.sh system/init.sh && chmod +x system/init.sh
success "文档已移动"
echo

# ==================== 步骤7：移动GitHub Actions ====================
info "7️⃣ 移动GitHub Actions..."
if [ -d ".github/workflows" ]; then
    mv .github/workflows/* system/.github/workflows/ 2>/dev/null || true
    success "GitHub Actions已移动"
fi
echo

# ==================== 步骤8：重命名用户目录 ====================
info "8️⃣ 重命名用户目录..."
if [ -d "面试大纲" ] && [ ! -d "outlines" ]; then
    read -p "将 '面试大纲' 重命名为 'outlines'？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv "面试大纲" outlines
        success "已重命名为 outlines"
    fi
fi
echo

# ==================== 步骤9：创建示例目录 ====================
info "9️⃣ 创建目录结构..."
mkdir -p examples
mkdir -p docs
success "目录结构创建完成"
echo

# ==================== 步骤10：创建新的system脚本 ====================
info "🔟 创建system内部脚本..."

# system/start.sh
cat > system/start.sh << 'EOF'
#!/bin/bash
# 每日开始脚本（system内部版本）

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}📅 每日开始 - 生成复习清单${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 生成今日复习清单
python system/scripts/review_manager.py today

echo
echo -e "${GREEN}✅ 今日复习清单已生成！${NC}"
echo -e "${YELLOW}📖 请打开 今日复习.md 开始复习${NC}"
echo
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
EOF
chmod +x system/start.sh

# system/end.sh
cat > system/end.sh << 'EOF'
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
EOF
chmod +x system/end.sh

success "System脚本创建完成"
echo

# ==================== 步骤11：创建根目录启动脚本 ====================
info "1️⃣1️⃣ 创建根目录启动脚本..."

cat > start.sh << 'EOF'
#!/bin/bash
# 启动脚本（调用system中的实际脚本）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
./system/start.sh "$@"
EOF
chmod +x start.sh

cat > end.sh << 'EOF'
#!/bin/bash
# 结束脚本（调用system中的实际脚本）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
./system/end.sh "$@"
EOF
chmod +x end.sh

success "根目录脚本创建完成"
echo

# ==================== 步骤12：创建kb快捷命令 ====================
info "1️⃣2️⃣ 创建kb快捷命令..."

cat > kb << 'EOF'
#!/bin/bash
# 知识库管理快捷命令
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
./system/scripts/kb.sh "$@"
EOF
chmod +x kb

success "快捷命令创建完成"
echo

# ==================== 步骤13：更新.gitignore ====================
info "1️⃣3️⃣ 更新.gitignore..."

if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*.so
.Python
env/
venv/

# 编辑器
.vscode/
.idea/
*.swp
.DS_Store

# 临时文件
*.tmp
*.bak
.cache/

# 每日复习（可选忽略）
# 今日复习.md

# 复习归档
今日复习归档/

# 日志
*.log

# 系统文件
Thumbs.db
.Trashes

# 个人内容（示例，根据需要调整）
# 简历/
GITIGNORE
    success ".gitignore已创建"
else
    info ".gitignore已存在，请手动检查"
fi
echo

# ==================== 完成 ====================
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 重组完成！${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

info "📂 新的目录结构："
tree -L 2 -I '__pycache__|*.pyc|.git' . 2>/dev/null || {
    echo "  system/          # 脚本系统（可共享）"
    echo "    ├── scripts/   # Python脚本"
    echo "    ├── config/    # 配置模板"
    echo "    ├── templates/ # 笔记模板"
    echo "    ├── docs/      # 文档"
    echo "    ├── start.sh   # 每日开始"
    echo "    └── end.sh     # 每日结束"
    echo "  notes/           # 您的笔记"
    echo "  outlines/        # 您的大纲"
    echo "  config/          # 您的配置"
    echo "  examples/        # 示例"
    echo "  start.sh         # 快捷启动"
    echo "  end.sh           # 快捷结束"
    echo "  kb               # 快捷命令"
}
echo

warning "⚠️  重要：下一步操作"
echo "  1. 检查 system/scripts/ 中的路径引用"
echo "  2. 测试功能: ./start.sh"
echo "  3. 如有问题: git restore ."
echo

info "💡 测试命令："
echo "  ./start.sh         # 生成复习清单"
echo "  ./kb today         # 同上"
echo "  ./kb sync          # 同步进度"
echo "  ./kb stats         # 查看统计"
echo

success "开始使用您的模板化知识库吧！ 🚀"
echo

