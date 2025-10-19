#!/bin/bash
# 知识库管理快捷命令

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印彩色信息
info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# 显示帮助信息
show_help() {
    cat << EOF
📚 知识库管理工具

用法: ./scripts/kb.sh <命令> [参数]

📋 常用命令:

  today                    生成今日复习清单
  sync                     同步复习清单中已勾选的笔记（推荐！）
  done <file>              标记单个笔记为已复习
  stats                    查看统计信息
  
  graph                    生成知识图谱（所有格式）
  index                    生成跨主题索引
  report                   生成统计报表
  
  link <file>              为笔记生成相关链接
  link-all                 为所有笔记生成相关链接
  
  add-meta                 为现有笔记添加元数据
  fix-meta                 修复不完整的元数据
  
  new <name>               从模板创建新笔记
  
  update-all               运行所有更新（清单+图谱+索引+报表）

🔧 高级命令:

  difficulty <file> <level>    设置笔记难度 (easy/medium/hard)
  
示例:

  ./scripts/kb.sh today
  ./scripts/kb.sh sync             # 推荐工作流！
  ./scripts/kb.sh done notes/cuda/Bank冲突.md
  ./scripts/kb.sh new notes/新主题/新笔记.md
  ./scripts/kb.sh update-all

💡 推荐工作流:
  1. 运行 today 生成复习清单
  2. 在 今日复习.md 中打勾标记已复习的笔记 (- [x])
  3. 运行 sync 批量更新所有打勾的笔记

EOF
}

# 主命令处理
case "${1:-}" in
    today)
        info "生成今日复习清单..."
        python scripts/review_manager.py today
        success "复习清单已生成: 今日复习.md"
        info "💡 提示: 复习完后在清单中打勾，然后运行 './scripts/kb.sh sync'"
        ;;
    
    sync)
        info "同步复习清单中已勾选的笔记..."
        python scripts/review_manager.py sync
        ;;
    
    done)
        if [ -z "$2" ]; then
            error "请指定文件路径"
            echo "用法: ./scripts/kb.sh done <文件路径>"
            exit 1
        fi
        python scripts/review_manager.py mark-done "$2"
        ;;
    
    stats)
        python scripts/review_manager.py stats
        ;;
    
    graph)
        info "生成知识图谱..."
        python scripts/knowledge_graph.py --all
        success "知识图谱已生成"
        info "  - HTML: docs/knowledge_graph.html"
        info "  - Markdown: 面试大纲/_知识图谱.md"
        ;;
    
    index)
        info "生成跨主题索引..."
        python scripts/auto_link.py index
        success "跨主题索引已生成: 面试大纲/_知识点索引.md"
        ;;
    
    report)
        info "生成统计报表..."
        python scripts/stats_generator.py
        success "统计报表已生成: 面试大纲/_统计报表.md"
        ;;
    
    link)
        if [ -z "$2" ]; then
            error "请指定文件路径"
            echo "用法: ./scripts/kb.sh link <文件路径>"
            exit 1
        fi
        info "为笔记生成相关链接..."
        python scripts/auto_link.py update "$2"
        ;;
    
    link-all)
        warning "这可能需要较长时间..."
        read -p "确认要为所有笔记生成相关链接吗？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python scripts/auto_link.py update-all
        else
            info "已取消"
        fi
        ;;
    
    add-meta)
        info "扫描需要添加元数据的笔记..."
        python scripts/add_metadata.py add --dry-run
        echo
        read -p "确认添加元数据吗？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python scripts/add_metadata.py add
        else
            info "已取消"
        fi
        ;;
    
    fix-meta)
        info "修复不完整的元数据..."
        python scripts/add_metadata.py fix
        ;;
    
    difficulty)
        if [ -z "$2" ] || [ -z "$3" ]; then
            error "请指定文件路径和难度等级"
            echo "用法: ./scripts/kb.sh difficulty <文件路径> <easy|medium|hard>"
            exit 1
        fi
        python scripts/review_manager.py set-difficulty "$2" "$3"
        ;;
    
    new)
        if [ -z "$2" ]; then
            error "请指定新笔记的路径"
            echo "用法: ./scripts/kb.sh new notes/主题/笔记名.md"
            exit 1
        fi
        
        NOTE_PATH="$2"
        NOTE_DIR="$(dirname "$NOTE_PATH")"
        NOTE_NAME="$(basename "$NOTE_PATH" .md)"
        
        # 创建目录
        mkdir -p "$NOTE_DIR"
        
        # 从模板创建
        if [ -f "templates/note_template.md" ]; then
            TODAY=$(date +%Y-%m-%d)
            TOMORROW=$(date -d tomorrow +%Y-%m-%d 2>/dev/null || date -v+1d +%Y-%m-%d 2>/dev/null || echo "$TODAY")
            
            sed -e "s/{{DATE}}/$TODAY/g" \
                -e "s/{{DATE_PLUS_1}}/$TOMORROW/g" \
                -e "s/{{TITLE}}/$NOTE_NAME/g" \
                templates/note_template.md > "$NOTE_PATH"
            
            success "新笔记已创建: $NOTE_PATH"
            info "请编辑笔记内容"
        else
            error "模板文件不存在: templates/note_template.md"
            exit 1
        fi
        ;;
    
    update-all)
        info "开始全面更新..."
        echo
        
        info "[1/4] 生成复习清单..."
        python scripts/review_manager.py today
        success "完成"
        echo
        
        info "[2/4] 生成知识图谱..."
        python scripts/knowledge_graph.py --all
        success "完成"
        echo
        
        info "[3/4] 生成跨主题索引..."
        python scripts/auto_link.py index
        success "完成"
        echo
        
        info "[4/4] 生成统计报表..."
        python scripts/stats_generator.py
        success "完成"
        echo
        
        success "全部更新完成！"
        info "生成的文件:"
        info "  - 今日复习.md"
        info "  - 面试大纲/_知识图谱.md"
        info "  - 面试大纲/_知识点索引.md"
        info "  - 面试大纲/_统计报表.md"
        info "  - docs/knowledge_graph.html"
        ;;
    
    help|--help|-h)
        show_help
        ;;
    
    *)
        if [ -z "$1" ]; then
            error "请指定命令"
        else
            error "未知命令: $1"
        fi
        echo
        echo "运行 './scripts/kb.sh help' 查看帮助"
        exit 1
        ;;
esac

