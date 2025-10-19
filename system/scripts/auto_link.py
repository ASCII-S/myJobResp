#!/usr/bin/env python3
"""
自动链接生成器
功能：
1. 基于内容相似度自动发现相关文档
2. 基于标签匹配推荐相关笔记
3. 自动更新文档底部的"相关笔记"区块
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse
from collections import Counter
import jieba
import yaml

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent  # 脚本在 system/scripts/ 中
NOTES_DIR = ROOT_DIR / "notes"

# 配置文件（优先用户配置，后备模板配置）
USER_CONFIG = ROOT_DIR / "config" / "kb_config.yaml"
TEMPLATE_CONFIG = ROOT_DIR / "system" / "config" / "kb_config.yaml"
CONFIG_FILE = USER_CONFIG if USER_CONFIG.exists() else TEMPLATE_CONFIG


def load_config() -> Dict:
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def parse_frontmatter(content: str) -> Tuple[Dict, str]:
    """解析文档的frontmatter和正文"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_str)
            return frontmatter or {}, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """提取文本关键词"""
    # 移除Markdown语法
    text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    text = re.sub(r'#+ ', '', text)
    text = re.sub(r'\[.*?\]\(.*?\)', '', text)
    
    # 分词
    words = jieba.cut(text)
    
    # 过滤停用词和短词
    stopwords = {'的', '了', '是', '在', '和', '与', '或', '有', '为', '等', '如', '如何', '什么', '怎么'}
    filtered_words = [w for w in words if len(w) > 1 and w not in stopwords]
    
    # 统计词频
    word_freq = Counter(filtered_words)
    
    return [word for word, _ in word_freq.most_common(top_n)]


def calculate_similarity(doc1: Dict, doc2: Dict, config: Dict) -> float:
    """计算两个文档的相似度（0-1）"""
    keyword_weight = config['auto_linking']['keyword_weight']
    tag_weight = config['auto_linking']['tag_weight']
    
    # 标签相似度
    tags1 = set(doc1.get('tags', []))
    tags2 = set(doc2.get('tags', []))
    
    if tags1 and tags2:
        tag_similarity = len(tags1 & tags2) / len(tags1 | tags2)
    else:
        tag_similarity = 0
    
    # 关键词相似度
    keywords1 = set(doc1.get('keywords', []))
    keywords2 = set(doc2.get('keywords', []))
    
    if keywords1 and keywords2:
        keyword_similarity = len(keywords1 & keywords2) / len(keywords1 | keywords2)
    else:
        keyword_similarity = 0
    
    # 加权平均
    similarity = keyword_weight * keyword_similarity + tag_weight * tag_similarity
    
    return similarity


def find_related_notes(target_file: Path, all_notes: List[Dict], config: Dict) -> List[Tuple[Dict, float]]:
    """找到与目标文档相关的笔记"""
    # 读取目标文档
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = parse_frontmatter(content)
    
    # 提取关键词
    keywords = extract_keywords(body)
    
    target_doc = {
        'filepath': target_file,
        'tags': frontmatter.get('tags', []),
        'keywords': keywords
    }
    
    # 计算相似度
    similarities = []
    for note in all_notes:
        # 跳过自己
        if note['filepath'] == target_file:
            continue
        
        similarity = calculate_similarity(target_doc, note, config)
        
        if similarity >= config['auto_linking']['similarity_threshold']:
            similarities.append((note, similarity))
    
    # 按相似度排序
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    # 返回前N个
    max_suggestions = config['auto_linking']['max_suggestions']
    return similarities[:max_suggestions]


def update_related_notes_section(filepath: Path, related_notes: List[Tuple[Dict, float]]) -> None:
    """更新文档的"相关笔记"区块"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找"相关笔记"区块
    pattern = r'(## 相关笔记\n).*?(?=\n## |$)'
    
    # 生成新的相关笔记内容
    related_section = "## 相关笔记\n"
    related_section += "<!-- 自动生成 -->\n\n"
    
    if related_notes:
        for note, similarity in related_notes:
            rel_path = note['relative_path']
            title = note['title']
            tags = ', '.join(note.get('tags', [])[:3])
            related_section += f"- [{title}]({rel_path}) - 相似度: {similarity:.0%}"
            if tags:
                related_section += f" | 标签: {tags}"
            related_section += "\n"
    else:
        related_section += "暂无相关笔记\n"
    
    related_section += "\n"
    
    # 替换或添加相关笔记区块
    if re.search(pattern, content, re.DOTALL):
        new_content = re.sub(pattern, related_section, content, flags=re.DOTALL)
    else:
        # 如果不存在，添加到文档末尾
        if not content.endswith('\n'):
            content += '\n'
        new_content = content + '\n---\n\n' + related_section
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def scan_all_notes(notes_dir: Path) -> List[Dict]:
    """扫描所有笔记，提取元数据和关键词"""
    notes = []
    
    print("🔍 扫描笔记文件...")
    for md_file in notes_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        keywords = extract_keywords(body)
        
        note_info = {
            'filepath': md_file,
            'relative_path': md_file.relative_to(ROOT_DIR),
            'title': md_file.stem,
            'tags': frontmatter.get('tags', []),
            'keywords': keywords
        }
        notes.append(note_info)
    
    print(f"📚 找到 {len(notes)} 篇笔记")
    return notes


def generate_cross_topic_index(all_notes: List[Dict], config: Dict) -> str:
    """生成跨主题索引"""
    # 统计标签
    tag_notes = {}
    for note in all_notes:
        for tag in note.get('tags', []):
            if tag not in tag_notes:
                tag_notes[tag] = []
            tag_notes[tag].append(note)
    
    # 找出跨主题的标签（出现在多个主题的）
    cross_topic_tags = {tag: notes for tag, notes in tag_notes.items() if len(notes) >= 2}
    
    # 生成Markdown
    md = f"""# 🔗 知识点跨主题索引

**生成时间**: {Path.cwd()}

本索引列出在多个主题中都出现的知识点，帮助建立跨领域连接。

---

"""
    
    # 按标签分组
    for tag in sorted(cross_topic_tags.keys()):
        notes = cross_topic_tags[tag]
        md += f"## {tag} ({len(notes)}篇)\n\n"
        
        # 按主题分组
        by_topic = {}
        for note in notes:
            # 从路径提取主题（第一级目录）
            parts = note['relative_path'].parts
            if len(parts) >= 2 and parts[0] == 'notes':
                topic = parts[1]
            else:
                topic = '其他'
            
            if topic not in by_topic:
                by_topic[topic] = []
            by_topic[topic].append(note)
        
        md += f"**涉及主题**: {', '.join(by_topic.keys())}\n\n"
        
        for topic, topic_notes in sorted(by_topic.items()):
            md += f"### {topic}\n\n"
            for note in topic_notes:
                md += f"- [{note['title']}]({note['relative_path']})\n"
            md += "\n"
        
        md += "---\n\n"
    
    return md


def main():
    parser = argparse.ArgumentParser(description='自动链接生成器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # update 命令：更新单个文档的相关笔记
    parser_update = subparsers.add_parser('update', help='更新单个文档的相关笔记')
    parser_update.add_argument('filepath', type=str, help='文件路径')
    
    # update-all 命令：更新所有文档
    parser_update_all = subparsers.add_parser('update-all', help='更新所有文档的相关笔记')
    
    # index 命令：生成跨主题索引
    parser_index = subparsers.add_parser('index', help='生成跨主题索引')
    
    args = parser.parse_args()
    config = load_config()
    
    if args.command == 'update':
        filepath = ROOT_DIR / args.filepath
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            return
        
        print(f"📄 处理文件: {filepath.name}")
        all_notes = scan_all_notes(NOTES_DIR)
        
        print("🔗 查找相关笔记...")
        related_notes = find_related_notes(filepath, all_notes, config)
        
        if related_notes:
            print(f"✅ 找到 {len(related_notes)} 篇相关笔记")
            for note, sim in related_notes:
                print(f"   - {note['title']} (相似度: {sim:.0%})")
        else:
            print("ℹ️  未找到相关笔记")
        
        print("💾 更新文档...")
        update_related_notes_section(filepath, related_notes)
        print("✅ 完成")
    
    elif args.command == 'update-all':
        all_notes = scan_all_notes(NOTES_DIR)
        
        print(f"🔄 开始更新所有文档...")
        for i, note in enumerate(all_notes, 1):
            print(f"[{i}/{len(all_notes)}] {note['title']}")
            related_notes = find_related_notes(note['filepath'], all_notes, config)
            update_related_notes_section(note['filepath'], related_notes)
        
        print("✅ 全部完成")
    
    elif args.command == 'index':
        all_notes = scan_all_notes(NOTES_DIR)
        
        print("📊 生成跨主题索引...")
        index_content = generate_cross_topic_index(all_notes, config)
        
        output_file = ROOT_DIR / "面试大纲" / "_知识点索引.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"✅ 索引已生成: {output_file}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

