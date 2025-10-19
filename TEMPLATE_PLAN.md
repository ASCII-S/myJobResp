# 知识库模板化方案

## 🎯 目标

将当前项目的脚本系统提取为通用模板，方便其他人快速创建自己的个人知识库。

## 📂 推荐的项目结构

### 方案一：单仓库分离（推荐）

在当前项目中通过清晰的目录结构分离：

```
knowledge-base/
├── 📁 system/                    # 模板系统（可共享）
│   ├── scripts/                 # 所有Python脚本
│   │   ├── review_manager.py
│   │   ├── add_metadata.py
│   │   ├── auto_link.py
│   │   ├── knowledge_graph.py
│   │   ├── stats_generator.py
│   │   └── kb.sh
│   ├── config/                  # 配置模板
│   │   └── kb_config.yaml
│   ├── templates/               # 笔记模板
│   │   └── note_template.md
│   ├── docs/                    # 系统文档
│   │   ├── README.md           # 快速开始
│   │   ├── INSTALLATION.md     # 安装指南
│   │   ├── USER_GUIDE.md       # 使用手册
│   │   └── CUSTOMIZATION.md    # 自定义指南
│   ├── .github/                 # CI/CD配置
│   │   └── workflows/
│   ├── init.sh                  # 初始化脚本
│   ├── start.sh                 # 每日开始
│   ├── end.sh                   # 每日结束
│   └── requirements.txt
│
├── 📁 notes/                     # 用户笔记（个人内容）
│   ├── topic1/
│   ├── topic2/
│   └── ...
│
├── 📁 outlines/                  # 用户大纲（个人内容）
│   ├── outline1.md
│   ├── outline2.md
│   └── ...
│
├── 📁 examples/                  # 示例笔记（供参考）
│   ├── example_note.md
│   └── example_outline.md
│
├── .gitignore
├── README.md                     # 项目说明
└── 今日复习.md                  # 自动生成
```

**优点**：
- ✅ 一个仓库包含所有内容
- ✅ 系统和内容清晰分离
- ✅ 用户可以选择性地更新系统部分
- ✅ 适合个人使用

### 方案二：双仓库分离（高级）

创建两个独立的仓库：

#### 1. 模板仓库（公开）

```
knowledge-base-template/
├── scripts/                     # 所有脚本
├── config/                      # 配置模板
├── templates/                   # 笔记模板
├── docs/                        # 完整文档
├── examples/                    # 示例笔记
├── .github/                     # CI/CD
├── init.sh                      # 初始化脚本
├── start.sh
├── end.sh
├── requirements.txt
└── README.md                    # 如何使用这个模板
```

#### 2. 个人知识库（私有）

```
my-knowledge-base/
├── system/                      # git submodule → 模板仓库
├── notes/                       # 个人笔记
├── outlines/                    # 个人大纲
├── config/                      # 个人配置（覆盖模板）
└── README.md
```

**优点**：
- ✅ 模板可独立维护和更新
- ✅ 多个知识库可共享同一模板
- ✅ 模板可公开，知识库保持私有
- ✅ 适合开源分享

## 🛠️ 实现步骤

### 第一阶段：重组当前项目（方案一）

1. **创建 `system/` 目录**
   ```bash
   mkdir -p system/scripts system/config system/templates system/docs
   ```

2. **移动系统文件**
   ```bash
   # 移动脚本
   mv scripts/* system/scripts/
   
   # 移动配置
   mv config/* system/config/
   
   # 移动模板
   mv templates/* system/templates/
   
   # 移动工具脚本
   mv start.sh end.sh system/
   
   # 移动系统文档
   mv README_WORKFLOW.md system/docs/
   mv requirements.txt system/
   ```

3. **调整路径引用**
   - 更新所有脚本中的相对路径
   - 更新 `start.sh` 和 `end.sh` 中的路径

4. **重命名用户内容**
   ```bash
   # 重命名为更清晰的名称
   mv 面试大纲 outlines
   mv notes notes  # 保持不变
   ```

5. **创建示例目录**
   ```bash
   mkdir -p examples
   # 复制一些示例笔记
   ```

### 第二阶段：创建初始化脚本

创建 `system/init.sh` 让新用户快速开始：

```bash
#!/bin/bash
# 知识库初始化脚本

echo "📚 欢迎使用知识库管理系统！"
echo

# 1. 检查依赖
echo "1️⃣ 检查依赖..."
python3 --version || { echo "❌ 需要 Python 3"; exit 1; }
git --version || { echo "❌ 需要 Git"; exit 1; }

# 2. 安装Python依赖
echo "2️⃣ 安装Python依赖..."
pip install -r system/requirements.txt

# 3. 创建必要目录
echo "3️⃣ 创建目录结构..."
mkdir -p notes outlines docs 今日复习归档

# 4. 复制配置文件（如果不存在）
echo "4️⃣ 设置配置..."
if [ ! -f "config/kb_config.yaml" ]; then
    mkdir -p config
    cp system/config/kb_config.yaml config/kb_config.yaml
    echo "✅ 已创建配置文件，请根据需要修改"
fi

# 5. 创建示例笔记
echo "5️⃣ 创建示例笔记..."
if [ ! -f "notes/示例笔记.md" ]; then
    cp system/templates/note_template.md notes/示例笔记.md
fi

# 6. 配置git（可选）
echo "6️⃣ 配置Git..."
if [ ! -d ".git" ]; then
    read -p "是否初始化Git仓库？(y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        cp system/.gitignore.template .gitignore
        echo "✅ Git仓库已初始化"
    fi
fi

echo
echo "🎉 初始化完成！"
echo
echo "📖 下一步："
echo "  1. 编辑配置: config/kb_config.yaml"
echo "  2. 创建笔记: 使用 system/templates/note_template.md 作为模板"
echo "  3. 开始使用: ./system/start.sh"
echo
echo "📚 查看文档: system/docs/README.md"
```

### 第三阶段：完善文档

创建以下文档：

1. **`system/docs/README.md`** - 快速开始指南
2. **`system/docs/INSTALLATION.md`** - 详细安装说明
3. **`system/docs/USER_GUIDE.md`** - 使用手册
4. **`system/docs/CUSTOMIZATION.md`** - 自定义指南
5. **`system/docs/DEVELOPMENT.md`** - 开发者文档

### 第四阶段：创建模板仓库（可选）

如果要采用方案二：

1. 创建新仓库 `knowledge-base-template`
2. 将 `system/` 目录内容移到新仓库根目录
3. 完善 README 和文档
4. 发布到 GitHub
5. 在个人知识库中使用 git submodule

## 📝 使用流程（给其他用户）

### 方案一：单仓库

```bash
# 1. 克隆或下载模板
git clone https://github.com/your-name/knowledge-base-template.git my-kb
cd my-kb

# 2. 运行初始化
./system/init.sh

# 3. 自定义配置
nano config/kb_config.yaml

# 4. 开始使用
./system/start.sh
```

### 方案二：双仓库

```bash
# 1. 创建新的知识库
mkdir my-knowledge-base
cd my-knowledge-base

# 2. 添加模板作为 submodule
git init
git submodule add https://github.com/your-name/kb-template.git system

# 3. 运行初始化
./system/init.sh

# 4. 开始使用
./system/start.sh
```

## 🎨 配置分离策略

支持用户自定义配置，而不修改模板：

```
# 配置加载优先级
1. ./config/kb_config.yaml          # 用户自定义（优先）
2. ./system/config/kb_config.yaml   # 模板默认（后备）
```

修改脚本以支持配置覆盖：

```python
def load_config() -> Dict:
    """加载配置文件，支持用户自定义覆盖"""
    # 先加载模板配置
    template_config = ROOT_DIR / "system" / "config" / "kb_config.yaml"
    config = {}
    if template_config.exists():
        with open(template_config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    
    # 加载用户配置并覆盖
    user_config = ROOT_DIR / "config" / "kb_config.yaml"
    if user_config.exists():
        with open(user_config, 'r', encoding='utf-8') as f:
            user_cfg = yaml.safe_load(f)
            config.update(user_cfg)  # 深度合并
    
    return config
```

## 📋 待办清单

- [ ] 决定使用方案一还是方案二
- [ ] 重组目录结构
- [ ] 更新所有脚本中的路径引用
- [ ] 创建 `init.sh` 初始化脚本
- [ ] 编写系统文档（快速开始、安装、使用手册）
- [ ] 创建示例笔记和大纲
- [ ] 实现配置覆盖机制
- [ ] 更新 .gitignore（分离系统和用户内容）
- [ ] 测试完整流程
- [ ] （可选）发布到 GitHub

## 🚀 发布清单（如果公开分享）

- [ ] 编写清晰的 README
- [ ] 添加 LICENSE 文件（MIT/Apache 2.0）
- [ ] 创建 CHANGELOG
- [ ] 添加 GitHub Actions（自动测试）
- [ ] 创建 GitHub Pages 文档网站
- [ ] 录制使用演示视频
- [ ] 撰写博客文章介绍

## 💡 命名建议

### 项目名称
- `knowledge-base-template`
- `personal-kb-system`
- `lifelong-learning-kb`
- `smart-knowledge-base`
- `atomic-notes-system`

### GitHub 描述
"🧠 A smart knowledge base system with spaced repetition, automated reviews, and knowledge graph visualization. Perfect for lifelong learning."

### 标签
- knowledge-management
- note-taking
- spaced-repetition
- personal-knowledge-base
- zettelkasten
- second-brain
- python
- markdown

## 📊 推荐实施顺序

### 第一步：快速验证（1-2小时）
1. 创建 `system/` 目录
2. 移动核心脚本
3. 调整路径
4. 测试基本功能

### 第二步：完善结构（2-3小时）
1. 创建示例内容
2. 编写初始化脚本
3. 完善 .gitignore
4. 编写基础文档

### 第三步：发布准备（3-5小时）
1. 完善所有文档
2. 创建详细的 README
3. 添加 LICENSE
4. 测试完整流程

## 🎯 成功标准

模板化完成的标志：
- ✅ 新用户可以在5分钟内开始使用
- ✅ 不需要修改任何系统代码
- ✅ 配置清晰且有示例
- ✅ 文档完整且易懂
- ✅ 更新系统不影响用户内容

---

**建议**: 我推荐先使用**方案一（单仓库）**，因为：
1. 更容易实施和维护
2. 适合大多数个人使用场景
3. 以后可以轻松迁移到方案二

需要我帮您开始实施吗？

