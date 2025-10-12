# 项目结构说明

## 📁 文件结构

```
Jobs/
├── index.html              # Docsify 主配置文件和网站入口
├── _sidebar.md             # 侧边栏导航配置
├── README.md               # 首页内容
├── .nojekyll               # 告诉 GitHub Pages 不使用 Jekyll
├── .gitignore              # Git 忽略配置（排除简历等敏感信息）
├── preview.sh              # 本地预览脚本
├── QUICKSTART.md           # 快速开始指南
├── DEPLOY.md               # 详细部署指南
├── PROJECT_STRUCTURE.md    # 本文件
│
├── 面试大纲/                # 主要文档目录
│   ├── 精通C++.md
│   ├── cuda.md
│   ├── gemm-opt.md
│   ├── pytorch.md
│   ├── 机器学习.md
│   ├── 深度学习.md
│   ├── 熟悉GPU架构.md
│   ├── 熟悉主流大模型推理框架的使用和开发.md
│   ├── 熟悉主流推理框架vllm与sglang.md
│   ├── 熟悉分布式通信.md
│   ├── 熟悉大模型推理核心技术.md
│   ├── 熟悉大模型部署.md
│   ├── 熟悉常用的加速器.md
│   ├── 熟悉常见的大模型.md
│   ├── 熟悉操作系统原理.md
│   ├── 精通Transformer.md
│   ├── 精通vllm,有相关推理框架开发经验.md
│   ├── 精通大模型压缩技术.md
│   ├── 精通数据结构.md
│   └── AI大模型训练推理及优化.md
│
├── notes/                  # 详细笔记（被面试大纲引用）
│   ├── C++/
│   ├── cuda/
│   ├── DS/
│   ├── Transformer/
│   ├── gemm-opt/
│   ├── pytorch/
│   ├── vllm/
│   ├── 分布式通信/
│   ├── 操作系统/
│   ├── 深度学习/
│   └── 精通大模型压缩技术/
│
└── 简历/                   # 个人简历（已被 .gitignore 排除）
```

## 🔧 核心文件说明

### index.html
- **作用**: Docsify 的主配置文件和网站入口
- **功能**:
  - 配置网站标题、主题
  - 启用侧边栏、搜索、代码高亮等插件
  - 配置相对路径支持（`relativePath: true`）
  - 移动端优化样式

### _sidebar.md
- **作用**: 侧边栏导航配置
- **特点**:
  - 按主题分类组织文档
  - 只显示"面试大纲"中的文档
  - 支持折叠/展开
  - 移动端友好

### README.md
- **作用**: 网站首页内容
- **内容**:
  - 项目介绍
  - 文档分类说明
  - 使用指南

### .nojekyll
- **作用**: 告诉 GitHub Pages 不使用 Jekyll 处理文件
- **重要性**: 必须存在，否则以下划线开头的文件（如 `_sidebar.md`）会被 Jekyll 忽略

### .gitignore
- **作用**: 配置 Git 忽略的文件和目录
- **排除内容**:
  - `简历/` 目录（避免个人信息泄露）
  - 系统文件（`.DS_Store`、`Thumbs.db`）
  - IDE 配置文件
  - 临时文件

## 🎨 技术栈

### Docsify
- **版本**: 4.x
- **特点**:
  - 无需构建，直接渲染 Markdown
  - 支持相对链接
  - 丰富的插件生态
  - 移动端友好

### 插件列表
1. **搜索插件** - 全文搜索功能
2. **代码高亮** - 支持 C++、Python、CUDA 等多种语言
3. **复制代码** - 一键复制代码块
4. **分页导航** - 上一篇/下一篇导航
5. **图片缩放** - 点击图片放大查看
6. **Emoji支持** - 表情符号渲染

## 📝 文档链接规则

### 相对链接格式
面试大纲中的文档链接到 notes 使用相对路径：

```markdown
[链接文本](../notes/目录名/文件名.md)
```

**示例**:
```markdown
[C++程序从源代码到可执行文件的完整过程](../notes/C++/C++程序从源代码到可执行文件的完整过程.md)
```

### Docsify 处理
- Docsify 会自动处理相对路径
- 配置 `relativePath: true` 确保链接正确解析
- 支持 Markdown、HTML 等格式的文档

## 🚀 部署流程

1. **初始化 Git 仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

2. **推送到 GitHub**
   ```bash
   git remote add origin <仓库地址>
   git push -u origin main
   ```

3. **启用 GitHub Pages**
   - Settings → Pages
   - Source: main 分支
   - 目录: / (root)

4. **访问网站**
   ```
   https://<username>.github.io/<repo-name>/
   ```

## 🔒 隐私保护

### 已排除的内容
- `简历/` 目录 - 包含个人简历、证件等敏感信息
- `.vscode/`、`.idea/` - IDE 配置文件
- 系统临时文件

### 建议
- 如果需要公开仓库，确保不包含任何敏感信息
- 如果需要保密，可以使用 GitHub 私有仓库（需要 Pro 账号才能使用 GitHub Pages）

## 📱 移动端优化

### 响应式设计
- 侧边栏自适应宽度
- 字体大小针对移动端优化
- 代码块横向滚动
- 触摸友好的交互

### 测试设备
建议在以下设备测试：
- iPhone / Android 手机
- iPad / Android 平板
- 不同尺寸的桌面浏览器

## 🔍 搜索功能

### 特点
- 全文搜索
- 中文分词支持
- 搜索结果高亮
- 快速跳转

### 使用
- 点击页面右上角搜索框
- 输入关键词
- 选择搜索结果跳转

## 🎯 下一步

1. **本地预览**: 运行 `./preview.sh` 查看效果
2. **部署到 GitHub Pages**: 参考 `QUICKSTART.md`
3. **自定义样式**: 修改 `index.html` 中的 CSS
4. **添加更多内容**: 在 `面试大纲/` 和 `notes/` 中添加文档

---

Happy Coding! 💻
