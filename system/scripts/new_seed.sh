#!/bin/bash
# 快速创建种子笔记的辅助脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }

echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌱 创建种子笔记${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo

# 1. 选择或输入主题
echo "请选择或输入主题："
echo

# 列出现有主题
SEEDS_DIR="notes/_seeds"
if [ -d "$SEEDS_DIR" ]; then
    echo "现有主题："
    i=1
    declare -a themes
    for dir in "$SEEDS_DIR"/*/; do
        if [ -d "$dir" ]; then
            theme=$(basename "$dir")
            themes[$i]="$theme"
            echo "  $i) $theme"
            ((i++))
        fi
    done
    echo "  0) 新建主题"
    echo
fi

read -p "选择序号或直接输入新主题名: " choice

if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -gt 0 ] && [ "$choice" -lt "$i" ]; then
    THEME="${themes[$choice]}"
    info "已选择主题: $THEME"
else
    THEME="$choice"
    if [ "$THEME" = "0" ] || [ -z "$THEME" ]; then
        read -p "输入新主题名: " THEME
    fi
    info "创建新主题: $THEME"
fi

# 2. 输入笔记标题
echo
read -p "笔记标题: " TITLE

if [ -z "$TITLE" ]; then
    echo "❌ 标题不能为空"
    exit 1
fi

# 3. 创建目录和文件
TARGET_DIR="$SEEDS_DIR/$THEME"
mkdir -p "$TARGET_DIR"

FILENAME="$TARGET_DIR/${TITLE}.md"

if [ -f "$FILENAME" ]; then
    echo "⚠️  文件已存在: $FILENAME"
    read -p "是否覆盖？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 4. 创建笔记内容
cat > "$FILENAME" << EOF
---
created: $(date +%Y-%m-%d)
difficulty: medium
tags:
  - seeds
  - $THEME
  - 待体系化
status: seed
potential_theme: "$THEME"
related_seeds: []
---

# $TITLE

> 快速记录关于"$TITLE"的核心内容

## 🎯 核心要点

- 

## 📚 快速参考

### 示例


### 命令/代码
\`\`\`

\`\`\`

## 🔗 相关碎片

- 

## 💡 未来扩展

当积累了更多"$THEME"相关的种子笔记时：
- [ ] 可以考虑升级为正式主题
- [ ] 补充完整的知识体系

## 📌 备注


EOF

success "种子笔记已创建: $FILENAME"
echo
info "下一步："
echo "  1. 编辑笔记: ${FILENAME}"
echo "  2. 查看主题: ls -la $TARGET_DIR"
echo "  3. 继续积累更多种子笔记"
echo
echo "💡 提示: 当同主题积累5-10个种子笔记时，可以考虑升级为正式主题"
echo

