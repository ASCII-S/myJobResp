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
info "🐙 添加笔记相关文件到Git..."

# 从配置文件读取要提交的路径
CONFIG_FILE="config/kb_config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    CONFIG_FILE="system/config/kb_config.yaml"
fi

# 使用Python读取配置并添加文件
python3 << 'PYTHON_SCRIPT'
import yaml
import subprocess
import sys
from pathlib import Path

config_file = "config/kb_config.yaml" if Path("config/kb_config.yaml").exists() else "system/config/kb_config.yaml"

try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 从配置中读取路径
    paths_to_add = []
    
    # 1. 从 paths 配置读取
    if 'paths' in config:
        notes_dir = config['paths'].get('notes_dir', 'notes')
        outlines_dir = config['paths'].get('outlines_dir', '面试大纲')
        paths_to_add.extend([notes_dir, outlines_dir])
    
    # 2. 从 git_auto_commit.include_paths 读取（如果配置了）
    if 'git_auto_commit' in config and 'include_paths' in config['git_auto_commit']:
        paths_to_add.extend(config['git_auto_commit']['include_paths'])
    
    # 去重
    paths_to_add = list(set(paths_to_add))
    
    # 添加到git
    for path in paths_to_add:
        if Path(path).exists():
            result = subprocess.run(['git', 'add', path], capture_output=True)
            # 静默处理，错误不影响流程
    
    print(f"✅ 已添加 {len([p for p in paths_to_add if Path(p).exists()])} 个路径")
    
except Exception as e:
    print(f"⚠️  读取配置失败: {e}", file=sys.stderr)
    # 回退到基本路径
    subprocess.run(['git', 'add', 'notes/'], capture_output=True)
    subprocess.run(['git', 'add', '面试大纲/'], capture_output=True)
    print("⚠️  使用默认路径")
PYTHON_SCRIPT

# 检查是否有改动
if git diff --cached --quiet; then
    warning "没有笔记改动，跳过提交"
    exit 0
fi

info "📝 准备提交..."

COMMIT_MESSAGE="Daily knowledge base update: $(date +'%Y-%m-%d')"
git commit -m "$COMMIT_MESSAGE" || {
    warning "Commit失败，跳过推送"
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
