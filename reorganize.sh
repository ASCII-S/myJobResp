#!/bin/bash
# 知识库模板化重组脚本

set -e

echo "📚 开始重组知识库结构..."
echo "⚠️  建议先备份或在Git中提交当前状态！"
echo

read -p "是否继续？(y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 已取消"
    exit 1
fi

# 1. 创建system目录结构
echo "1️⃣ 创建system目录..."
mkdir -p system/scripts
mkdir -p system/config
mkdir -p system/templates
mkdir -p system/docs

# 2. 移动脚本
echo "2️⃣ 移动脚本文件..."
if [ -d "scripts" ]; then
    mv scripts/* system/scripts/ 2>/dev/null || true
    rmdir scripts 2>/dev/null || true
fi

# 3. 移动配置
echo "3️⃣ 移动配置文件..."
if [ -d "config" ]; then
    cp -r config/* system/config/  # 复制作为模板
fi

# 4. 移动模板
echo "4️⃣ 移动模板文件..."
if [ -d "templates" ]; then
    mv templates/* system/templates/ 2>/dev/null || true
    rmdir templates 2>/dev/null || true
fi

# 5. 移动系统脚本
echo "5️⃣ 移动系统脚本..."
[ -f "start.sh" ] && mv start.sh system/
[ -f "end.sh" ] && mv end.sh system/
[ -f "requirements.txt" ] && mv requirements.txt system/

# 6. 移动文档
echo "6️⃣ 移动文档..."
[ -f "README_WORKFLOW.md" ] && mv README_WORKFLOW.md system/docs/
[ -f "TEMPLATE_PLAN.md" ] && mv TEMPLATE_PLAN.md system/docs/

# 7. 重命名用户目录（可选）
echo "7️⃣ 重命名用户目录..."
if [ -d "面试大纲" ]; then
    read -p "是否将'面试大纲'重命名为'outlines'？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mv "面试大纲" outlines
        echo "✅ 已重命名为 outlines"
    fi
fi

# 8. 创建示例目录
echo "8️⃣ 创建示例目录..."
mkdir -p examples

# 9. 创建新的启动脚本（在根目录）
echo "9️⃣ 创建启动脚本..."
cat > start.sh << 'EOF'
#!/bin/bash
# 启动脚本（调用system中的实际脚本）
./system/start.sh "$@"
EOF
chmod +x start.sh

cat > end.sh << 'EOF'
#!/bin/bash
# 结束脚本（调用system中的实际脚本）
./system/end.sh "$@"
EOF
chmod +x end.sh

# 10. 创建kb快捷命令
echo "🔟 创建快捷命令..."
cat > kb << 'EOF'
#!/bin/bash
# 知识库管理快捷命令
./system/scripts/kb.sh "$@"
EOF
chmod +x kb

echo
echo "✅ 重组完成！"
echo
echo "📂 新的目录结构："
echo "  system/          # 脚本系统"
echo "  notes/           # 您的笔记"
echo "  outlines/        # 您的大纲"
echo "  config/          # 您的配置"
echo "  examples/        # 示例内容"
echo
echo "⚠️  下一步："
echo "  1. 检查system/scripts中的路径引用"
echo "  2. 测试: ./start.sh"
echo "  3. 如有问题，可以用git恢复"
echo

