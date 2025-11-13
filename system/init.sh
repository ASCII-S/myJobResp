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

load_git_config() {
    python3 - <<'PY'
import shlex
from pathlib import Path

import yaml

config_path = Path("system/config/git_config.yaml")
if not config_path.exists():
    print("git_config_present=0")
else:
    try:
        data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    except Exception as exc:
        print("git_config_present=1")
        print(f"git_config_error={shlex.quote(str(exc))}")
    else:
        git_data = data.get("git") or {}

        def emit(key: str, value):
            if isinstance(value, bool):
                value = int(value)
            elif value is None:
                value = ""
            print(f"{key}={shlex.quote(str(value))}")

        print("git_config_present=1")
        emit("git_enabled", git_data.get("enabled", True))
        emit("git_initialize_repository", git_data.get("initialize_repository", True))
        emit("git_default_branch", git_data.get("default_branch", "main"))

        user = git_data.get("user") or {}
        emit("git_user_name", user.get("name", ""))
        emit("git_user_email", user.get("email", ""))

        remote = git_data.get("remote") or {}
        emit("git_remote_enabled", remote.get("enabled", False))
        emit("git_remote_name", remote.get("name", "origin"))
        emit("git_remote_url", remote.get("url", ""))

        commit = git_data.get("commit") or {}
        emit("git_commit_message_template", commit.get("message_template", ""))
PY
}

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
mkdir -p notes/outline_template
mkdir -p outlines
mkdir -p docs
mkdir -p reviewsArchived

success "目录创建完成"
echo

# 4. 配置文件
info "4️⃣ 检查配置文件..."

kb_config_path="system/config/kb_config.yaml"
git_config_path="system/config/git_config.yaml"

if [ -f "$kb_config_path" ]; then
    info "已检测到配置文件: $kb_config_path"
else
    warning "未找到必需的配置文件: $kb_config_path"
fi

if [ -f "$git_config_path" ]; then
    info "已检测到 Git 配置文件: $git_config_path"
else
    warning "未找到 Git 配置文件: $git_config_path"
fi

echo

# 5. 创建示例资料
info "5️⃣ 创建示例资料..."

if [ -f "system/templates/note_template.md" ]; then
    if [ ! -f "notes/outline_template/示例笔记.md" ]; then
        cp system/templates/note_template.md notes/outline_template/示例笔记.md
        success "已创建示例笔记: notes/outline_template/示例笔记.md"
    else
        info "示例笔记已存在，跳过"
    fi
fi

if [ -f "system/templates/outline_template.md" ]; then
    if [ ! -f "outlines/示例大纲.md" ]; then
        cp system/templates/outline_template.md outlines/示例大纲.md
        success "已创建示例大纲: outlines/示例大纲.md"
    else
        info "示例大纲已存在，跳过"
    fi
fi

echo

# 6. Git配置
info "6️⃣ Git配置..."

git_config_env=$(load_git_config)
eval "$git_config_env"

if [ "${git_config_present:-0}" -eq 0 ]; then
    warning "未找到 system/config/git_config.yaml，请先完善配置后重新运行初始化"
elif [ -n "${git_config_error:-}" ]; then
    error "解析 config/git_config.yaml 失败: ${git_config_error}"
    exit 1
elif [ "${git_enabled:-1}" -eq 0 ]; then
    info "Git 自动配置已在 config/git_config.yaml 中禁用，跳过"
else
    if [ ! -d ".git" ]; then
        if [ "${git_initialize_repository:-1}" -eq 1 ]; then
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
# reviewsToday.md

# 复习归档
reviewsArchived/

# 系统文件
.DS_Store
Thumbs.db
GITIGNORE
            fi

            success "Git仓库已初始化"
        else
            warning "config/git_config.yaml 中未启用自动初始化，请手动执行 git init"
        fi
    else
        info "Git 仓库已存在，将继续应用配置"
    fi

    if [ -d ".git" ]; then
        if [ -n "${git_user_name:-}" ]; then
            git config user.name "${git_user_name}"
            info "已设置 Git 用户名: ${git_user_name}"
        fi

        if [ -n "${git_user_email:-}" ]; then
            git config user.email "${git_user_email}"
            info "已设置 Git 邮箱: ${git_user_email}"
        fi

        if [ -n "${git_default_branch:-}" ]; then
            current_branch=$(git symbolic-ref --short HEAD 2>/dev/null || echo "")
            if [ -n "$current_branch" ] && [ "$current_branch" != "${git_default_branch}" ]; then
                git branch -m "${git_default_branch}" >/dev/null 2>&1 || true
                info "已重命名当前分支为: ${git_default_branch}"
            fi
        fi

        if [ "${git_remote_enabled:-0}" -eq 1 ] && [ -n "${git_remote_url:-}" ]; then
            if git remote get-url "${git_remote_name}" >/dev/null 2>&1; then
                git remote set-url "${git_remote_name}" "${git_remote_url}"
                info "已更新远程仓库 ${git_remote_name}"
            else
                git remote add "${git_remote_name}" "${git_remote_url}"
                info "已添加远程仓库 ${git_remote_name}"
            fi
        fi

        if [ -n "${git_commit_message_template:-}" ]; then
            info "默认提交信息模板: ${git_commit_message_template}"
        fi

        success "Git 自动配置完成"
    else
        warning "未检测到 Git 仓库，跳过剩余配置"
    fi
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
echo "  ./kb today         # 生成reviewsToday"
echo "  ./kb sync          # 同步复习进度"
echo "  ./kb stats         # 查看统计"
echo

success "祝您学习愉快！📚"
echo

