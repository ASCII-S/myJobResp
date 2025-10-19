#!/usr/bin/env python3
"""
批量添加元数据到现有笔记
功能：
1. 扫描所有没有frontmatter的笔记
2. 自动添加基础元数据
3. 保留原有内容
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict
import argparse

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
NOTES_DIR = ROOT_DIR / "notes"
CONFIG_FILE = ROOT_DIR / "config" / "kb_config.yaml"


def load_config() -> Dict:
    """加载配置文件"""
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def has_frontmatter(content: str) -> bool:
    """检查文档是否已有frontmatter"""
    pattern = r'^---\s*\n.*?\n---\s*\n'
    return bool(re.match(pattern, content, re.DOTALL))


def extract_tags_from_path(filepath: Path, notes_dir: Path) -> list:
    """从文件路径提取标签"""
    parts = filepath.relative_to(notes_dir).parts
    tags = []
    
    # 第一级目录作为主题标签
    if len(parts) >= 1:
        topic = parts[0]
        tags.append(topic)
    
    # 第二级目录作为子主题标签
    if len(parts) >= 2:
        subtopic = parts[1]
        if subtopic != filepath.stem:  # 避免重复
            tags.append(f"{topic}/{subtopic}")
    
    return tags


def add_frontmatter(filepath: Path, config: Dict, dry_run: bool = False) -> bool:
    """为文档添加frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查是否已有frontmatter
    if has_frontmatter(content):
        return False
    
    # 提取标签
    tags = extract_tags_from_path(filepath, NOTES_DIR)
    
    # 创建frontmatter
    today = datetime.now().strftime('%Y-%m-%d')
    tomorrow = datetime.now().strftime('%Y-%m-%d')  # 新笔记第一次复习设为第二天
    
    frontmatter = {
        'created': today,
        'last_reviewed': today,
        'next_review': tomorrow,
        'review_count': 0,
        'difficulty': config['default_difficulty'],
        'mastery_level': 0.0,
        'tags': tags,
        'related_outlines': []
    }
    
    # 构建新内容
    frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{frontmatter_str}---\n\n{content}"
    
    if not dry_run:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    return True


def scan_and_add_metadata(notes_dir: Path, config: Dict, dry_run: bool = False) -> Dict:
    """扫描并添加元数据"""
    stats = {
        'total': 0,
        'with_frontmatter': 0,
        'without_frontmatter': 0,
        'added': 0,
        'files': []
    }
    
    print("🔍 扫描笔记文件...")
    
    for md_file in notes_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        
        stats['total'] += 1
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if has_frontmatter(content):
            stats['with_frontmatter'] += 1
        else:
            stats['without_frontmatter'] += 1
            stats['files'].append(md_file)
    
    print(f"📚 总计: {stats['total']} 篇笔记")
    print(f"  ✅ 已有元数据: {stats['with_frontmatter']}")
    print(f"  ❌ 缺少元数据: {stats['without_frontmatter']}")
    
    if stats['without_frontmatter'] == 0:
        print("\n🎉 所有笔记都已有元数据！")
        return stats
    
    if dry_run:
        print(f"\n🔍 预览模式：将为以下 {len(stats['files'])} 个文件添加元数据：")
        for f in stats['files'][:20]:  # 只显示前20个
            print(f"  - {f.relative_to(ROOT_DIR)}")
        if len(stats['files']) > 20:
            print(f"  ... 还有 {len(stats['files']) - 20} 个文件")
        return stats
    
    print(f"\n📝 开始添加元数据...")
    for i, md_file in enumerate(stats['files'], 1):
        print(f"[{i}/{len(stats['files'])}] {md_file.name}", end='')
        
        if add_frontmatter(md_file, config, dry_run=False):
            stats['added'] += 1
            print(" ✅")
        else:
            print(" ⏭️  (已跳过)")
    
    print(f"\n✅ 完成！共添加 {stats['added']} 个文件的元数据")
    
    return stats


def update_existing_metadata(notes_dir: Path, config: Dict, field: str, value: any) -> int:
    """更新现有笔记的某个元数据字段"""
    updated = 0
    
    print(f"🔍 扫描并更新字段: {field} = {value}")
    
    for md_file in notes_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not has_frontmatter(content):
            continue
        
        # 解析frontmatter
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, content, re.DOTALL)
        
        if match:
            frontmatter_str = match.group(1)
            body = match.group(2)
            
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                
                # 更新字段
                frontmatter[field] = value
                
                # 重新构建文档
                new_frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
                new_content = f"---\n{new_frontmatter_str}---\n{body}"
                
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                updated += 1
                
            except yaml.YAMLError:
                continue
    
    print(f"✅ 已更新 {updated} 个文件")
    return updated


def main():
    parser = argparse.ArgumentParser(description='批量添加/更新元数据')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # add 命令：添加元数据
    parser_add = subparsers.add_parser('add', help='为缺少元数据的笔记添加')
    parser_add.add_argument('--dry-run', action='store_true', help='预览模式，不实际修改文件')
    
    # update 命令：更新字段
    parser_update = subparsers.add_parser('update', help='更新现有笔记的某个字段')
    parser_update.add_argument('field', type=str, help='字段名')
    parser_update.add_argument('value', type=str, help='字段值')
    
    # fix 命令：修复元数据
    parser_fix = subparsers.add_parser('fix', help='修复不完整的元数据')
    
    args = parser.parse_args()
    config = load_config()
    
    if args.command == 'add' or not args.command:
        # 默认命令
        dry_run = args.dry_run if args.command == 'add' else False
        stats = scan_and_add_metadata(NOTES_DIR, config, dry_run)
        
        if dry_run and stats['without_frontmatter'] > 0:
            print("\n💡 提示：运行以下命令以实际添加元数据：")
            print("   python scripts/add_metadata.py add")
    
    elif args.command == 'update':
        # 尝试解析值的类型
        value = args.value
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False
        elif value.isdigit():
            value = int(value)
        elif value.replace('.', '').isdigit():
            value = float(value)
        
        update_existing_metadata(NOTES_DIR, config, args.field, value)
    
    elif args.command == 'fix':
        print("🔧 修复不完整的元数据...")
        
        required_fields = {
            'created': datetime.now().strftime('%Y-%m-%d'),
            'last_reviewed': datetime.now().strftime('%Y-%m-%d'),
            'next_review': datetime.now().strftime('%Y-%m-%d'),
            'review_count': 0,
            'difficulty': 'medium',
            'mastery_level': 0.0,
            'tags': [],
            'related_outlines': []
        }
        
        fixed = 0
        for md_file in NOTES_DIR.rglob("*.md"):
            if md_file.name.startswith('.'):
                continue
            
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not has_frontmatter(content):
                continue
            
            pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
            match = re.match(pattern, content, re.DOTALL)
            
            if match:
                frontmatter_str = match.group(1)
                body = match.group(2)
                
                try:
                    frontmatter = yaml.safe_load(frontmatter_str)
                    needs_fix = False
                    
                    # 检查并补充缺失字段
                    for field, default_value in required_fields.items():
                        if field not in frontmatter:
                            frontmatter[field] = default_value
                            needs_fix = True
                    
                    if needs_fix:
                        # 重新构建文档
                        new_frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
                        new_content = f"---\n{new_frontmatter_str}---\n{body}"
                        
                        with open(md_file, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        
                        fixed += 1
                        print(f"✅ {md_file.name}")
                
                except yaml.YAMLError:
                    continue
        
        print(f"\n✅ 修复了 {fixed} 个文件的元数据")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

