#!/usr/bin/env python3
"""
知识库复习管理器
功能：
1. 生成今日复习清单
2. 标记文档为已复习
3. 自动更新元数据（复习次数、下次复习时间等）
4. 统计复习进度
"""

import os
import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import argparse

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
NOTES_DIR = ROOT_DIR / "notes"
OUTLINES_DIR = ROOT_DIR / "面试大纲"
CONFIG_FILE = ROOT_DIR / "config" / "kb_config.yaml"


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


def update_frontmatter(filepath: Path, updates: Dict) -> None:
    """更新文档的frontmatter"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, body = parse_frontmatter(content)
    
    # 更新字段
    for key, value in updates.items():
        frontmatter[key] = value
    
    # 重新构建文档
    frontmatter_str = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False)
    new_content = f"---\n{frontmatter_str}---\n{body}"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)


def calculate_next_review(review_count: int, difficulty: str, config: Dict) -> str:
    """计算下次复习日期"""
    intervals = config['review_intervals'].get(difficulty, config['review_intervals']['medium'])
    
    # 如果复习次数超过配置的间隔数，使用最后一个间隔
    index = min(review_count, len(intervals) - 1)
    days = intervals[index]
    
    next_date = datetime.now() + timedelta(days=days)
    return next_date.strftime('%Y-%m-%d')


def calculate_mastery_level(review_count: int, days_since_created: int) -> float:
    """计算掌握程度（0-1）"""
    # 简单算法：基于复习次数和时间跨度
    if days_since_created == 0:
        return 0.0
    
    # 复习密度
    density = review_count / max(days_since_created, 1)
    # 复习次数因子
    count_factor = min(review_count / 10, 1.0)
    
    mastery = min((density * 30 + count_factor) / 2, 1.0)
    return round(mastery, 2)


def scan_notes(notes_dir: Path) -> List[Dict]:
    """扫描所有笔记文件"""
    notes = []
    
    for md_file in notes_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
            
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, _ = parse_frontmatter(content)
        
        if frontmatter:
            note_info = {
                'filepath': md_file,
                'relative_path': md_file.relative_to(ROOT_DIR),
                'title': md_file.stem,
                **frontmatter
            }
            notes.append(note_info)
    
    return notes


def calculate_review_priority(note: Dict, today: datetime.date, config: Dict) -> float:
    """
    计算笔记的复习优先级分数（越高越优先）
    
    排序策略：将容易复习的放在前面，避免心态失衡
    - 创建时间新的（容易记住）
    - 复习次数多的（说明重要且熟悉）
    - 难度小的（easy优先）
    - tags数多的（关联性强，容易回忆）
    """
    weights = config.get('daily_review', {}).get('sort_weights', {
        'created_new': 1.0,
        'review_count': 2.0,
        'difficulty_easy': 3.0,
        'tags_count': 0.5
    })
    
    score = 0.0
    
    # 1. 创建时间新的（天数越少分数越高）
    created = note.get('created')
    if created:
        if isinstance(created, str):
            created_date = datetime.strptime(created, '%Y-%m-%d').date()
        elif isinstance(created, datetime):
            created_date = created.date()
        else:
            created_date = created
        
        days_since_created = (today - created_date).days
        # 归一化：30天内的笔记得分递减
        created_score = max(0, (30 - days_since_created) / 30)
        score += created_score * weights['created_new']
    
    # 2. 复习次数多的（次数越多分数越高）
    review_count = note.get('review_count', 0)
    # 归一化：10次以内线性增长，超过10次固定为1
    count_score = min(review_count / 10, 1.0)
    score += count_score * weights['review_count']
    
    # 3. 难度小的（easy > medium > hard）
    difficulty = note.get('difficulty', 'medium')
    difficulty_map = {'easy': 1.0, 'medium': 0.5, 'hard': 0.0}
    difficulty_score = difficulty_map.get(difficulty, 0.5)
    score += difficulty_score * weights['difficulty_easy']
    
    # 4. tags数量多的（关联性强）
    tags = note.get('tags', [])
    tags_count = len(tags) if isinstance(tags, list) else 0
    # 归一化：5个tags以内线性增长
    tags_score = min(tags_count / 5, 1.0)
    score += tags_score * weights['tags_count']
    
    return score


def generate_review_list(notes: List[Dict], config: Dict) -> Dict[str, List[Dict]]:
    """生成复习清单，按优先级分类并排序"""
    today = datetime.now().date()
    
    review_list = {
        'overdue': [],      # 已过期
        'today': [],        # 今日应复习
        'this_week': [],    # 本周应复习
        'upcoming': []      # 未来
    }
    
    for note in notes:
        next_review = note.get('next_review')
        if not next_review:
            continue
        
        if isinstance(next_review, str):
            next_review = datetime.strptime(next_review, '%Y-%m-%d').date()
        
        diff_days = (next_review - today).days
        
        # 分类：只有next_review <= today的才会出现在今日/过期中
        if diff_days < 0:
            review_list['overdue'].append(note)
        elif diff_days == 0:
            review_list['today'].append(note)
        elif diff_days <= 7:
            review_list['this_week'].append(note)
        else:
            review_list['upcoming'].append(note)
    
    # 智能排序：将容易复习的放在前面
    # 使用优先级分数排序（分数越高越靠前）
    for category in ['overdue', 'today', 'this_week']:
        review_list[category].sort(
            key=lambda x: calculate_review_priority(x, today, config),
            reverse=True  # 分数高的在前
        )
    
    # TopK限制：避免一次复习过多
    daily_config = config.get('daily_review', {})
    max_overdue = daily_config.get('max_overdue', 0)
    max_today = daily_config.get('max_today', 0)
    max_this_week = daily_config.get('max_this_week', 0)
    
    # 记录原始总数
    review_list['total_overdue'] = len(review_list['overdue'])
    review_list['total_today'] = len(review_list['today'])
    review_list['total_this_week'] = len(review_list['this_week'])
    
    # 应用TopK限制
    if max_overdue > 0 and len(review_list['overdue']) > max_overdue:
        review_list['overdue'] = review_list['overdue'][:max_overdue]
    if max_today > 0 and len(review_list['today']) > max_today:
        review_list['today'] = review_list['today'][:max_today]
    if max_this_week > 0 and len(review_list['this_week']) > max_this_week:
        review_list['this_week'] = review_list['this_week'][:max_this_week]
    
    return review_list


def generate_review_markdown(review_list: Dict[str, List[Dict]], config: Dict) -> str:
    """生成复习清单的Markdown文档"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 获取总数（在TopK之前）
    total_overdue = review_list.get('total_overdue', len(review_list['overdue']))
    total_today = review_list.get('total_today', len(review_list['today']))
    total_this_week = review_list.get('total_this_week', len(review_list['this_week']))
    
    # 获取TopK配置
    daily_config = config.get('daily_review', {})
    max_overdue = daily_config.get('max_overdue', 0)
    max_today = daily_config.get('max_today', 0)
    max_this_week = daily_config.get('max_this_week', 0)
    
    md = f"""# 📅 复习清单

**生成时间**: {today}

## 统计概览

- 🔴 **已过期**: {len(review_list['overdue'])} 篇"""
    
    if max_overdue > 0 and total_overdue > len(review_list['overdue']):
        md += f" (共{total_overdue}篇，显示前{max_overdue}篇)"
    
    md += f"\n- ⭐ **今日复习**: {len(review_list['today'])} 篇"
    
    if max_today > 0 and total_today > len(review_list['today']):
        md += f" (共{total_today}篇，显示前{max_today}篇)"
    
    md += f"\n- 📅 **本周计划**: {len(review_list['this_week'])} 篇"
    
    if max_this_week > 0 and total_this_week > len(review_list['this_week']):
        md += f" (共{total_this_week}篇，显示前{max_this_week}篇)"
    
    md += f"\n- 📆 **未来安排**: {len(review_list['upcoming'])} 篇\n\n"
    
    md += """💡 **排序策略**: 按优先级智能排序（容易复习的在前）
- ✅ 创建时间新的（容易记住）
- ✅ 复习次数多的（重要且熟悉）
- ✅ 难度小的（easy优先）
- ✅ 标签多的（关联性强）

---

"""
    
    # 已过期
    if review_list['overdue']:
        md += "## 🔴 已过期（优先复习）\n\n"
        md += "_按智能排序，从易到难，建议从上往下复习_\n\n"
        
        for i, note in enumerate(review_list['overdue'], 1):
            next_review = note.get('next_review', 'N/A')
            review_count = note.get('review_count', 0)
            difficulty = note.get('difficulty', 'medium')
            mastery = note.get('mastery_level', 0.0)
            tags_count = len(note.get('tags', []))
            
            # 显示序号
            md += f"**{i}.** "
            md += f"- [ ] [{note['title']}]({note['relative_path']})\n"
            md += f"  - 应于: {next_review} | 已复习: {review_count}次 | 难度: {difficulty} | 掌握度: {mastery:.0%} | 标签: {tags_count}个\n"
        md += "\n"
    
    # 今日复习
    if review_list['today']:
        md += "## ⭐ 今日复习\n\n"
        md += "_按智能排序，从易到难_\n\n"
        
        for i, note in enumerate(review_list['today'], 1):
            review_count = note.get('review_count', 0)
            difficulty = note.get('difficulty', 'medium')
            mastery = note.get('mastery_level', 0.0)
            tags_count = len(note.get('tags', []))
            
            md += f"**{i}.** "
            md += f"- [ ] [{note['title']}]({note['relative_path']})\n"
            md += f"  - 已复习: {review_count}次 | 难度: {difficulty} | 掌握度: {mastery:.0%} | 标签: {tags_count}个\n"
        md += "\n"
    
    # 本周计划
    if review_list['this_week']:
        md += "## 📅 本周计划\n\n"
        md += "_按智能排序_\n\n"
        
        for i, note in enumerate(review_list['this_week'], 1):
            next_review = note.get('next_review', 'N/A')
            review_count = note.get('review_count', 0)
            difficulty = note.get('difficulty', 'medium')
            
            md += f"**{i}.** "
            md += f"- [ ] [{note['title']}]({note['relative_path']}) - {next_review}\n"
            md += f"  - 已复习: {review_count}次 | 难度: {difficulty}\n"
        md += "\n"
    
    # 使用说明
    md += """---

## 📖 使用说明

### 💡 推荐方式：在清单中打勾，然后同步

1. **复习笔记时，直接在本文档中打勾**：
   - 将 `- [ ]` 改为 `- [x]`
   
2. **复习完成后，运行同步命令**：
```bash
python scripts/review_manager.py sync
# 或使用快捷命令: ./scripts/kb.sh sync
```

这会自动更新所有打勾笔记的元数据！

### 其他方式

#### 标记单个文档
```bash
python scripts/review_manager.py mark-done "notes/cuda/Bank冲突的概念.md"
```

#### 调整难度
```bash
python scripts/review_manager.py set-difficulty "notes/cuda/Bank冲突.md" hard
```

#### 重新生成清单
```bash
python scripts/review_manager.py today
```
"""
    
    return md


def mark_as_reviewed(filepath: Path, config: Dict) -> None:
    """标记文档为已复习，更新元数据"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    frontmatter, _ = parse_frontmatter(content)
    
    # 获取当前值
    review_count = frontmatter.get('review_count', 0)
    difficulty = frontmatter.get('difficulty', config['default_difficulty'])
    created = frontmatter.get('created')
    
    # 计算新值
    today = datetime.now().strftime('%Y-%m-%d')
    new_review_count = review_count + 1
    next_review = calculate_next_review(new_review_count, difficulty, config)
    
    # 计算掌握程度
    if created:
        if isinstance(created, str):
            created_date = datetime.strptime(created, '%Y-%m-%d').date()
        elif isinstance(created, datetime):
            created_date = created.date()
        else:
            created_date = created
        
        today_date = datetime.now().date()
        days_since_created = (today_date - created_date).days
    else:
        days_since_created = 30  # 默认值
    
    mastery_level = calculate_mastery_level(new_review_count, days_since_created)
    
    # 更新元数据
    updates = {
        'last_reviewed': today,
        'next_review': next_review,
        'review_count': new_review_count,
        'mastery_level': mastery_level
    }
    
    update_frontmatter(filepath, updates)
    
    print(f"✅ 已标记为复习: {filepath.name}")
    print(f"   复习次数: {review_count} → {new_review_count}")
    print(f"   下次复习: {next_review}")
    print(f"   掌握程度: {mastery_level:.0%}")


def set_difficulty(filepath: Path, difficulty: str) -> None:
    """设置文档难度"""
    valid_difficulties = ['easy', 'medium', 'hard']
    if difficulty not in valid_difficulties:
        print(f"❌ 无效的难度等级。请使用: {', '.join(valid_difficulties)}")
        return
    
    update_frontmatter(filepath, {'difficulty': difficulty})
    print(f"✅ 已设置难度为: {difficulty}")


def sync_from_review_list(config: Dict) -> None:
    """从今日复习清单同步已完成的笔记"""
    review_file = ROOT_DIR / "今日复习.md"
    
    if not review_file.exists():
        print("❌ 复习清单不存在，请先运行: python scripts/review_manager.py today")
        return
    
    with open(review_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 匹配已勾选的笔记：- [x] [标题](路径)
    pattern = r'- \[x\] \[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    if not matches:
        print("ℹ️  没有发现已勾选的笔记")
        return
    
    print(f"📋 发现 {len(matches)} 个已勾选的笔记")
    print()
    
    updated = 0
    failed = 0
    
    for title, rel_path in matches:
        filepath = ROOT_DIR / rel_path
        
        if not filepath.exists():
            print(f"❌ 文件不存在: {rel_path}")
            failed += 1
            continue
        
        try:
            mark_as_reviewed(filepath, config)
            updated += 1
        except Exception as e:
            print(f"❌ 更新失败 {filepath.name}: {e}")
            failed += 1
    
    print()
    print(f"✅ 成功更新: {updated} 个笔记")
    if failed > 0:
        print(f"❌ 失败: {failed} 个笔记")
    
    # 清空已完成的checkbox（改为普通文本）
    if updated > 0:
        print()
        try:
            response = input("是否清空已完成的checkbox？(y/N) ")
            if response.lower() == 'y':
                # 将 [x] 替换为 [✓]（已完成标记）
                new_content = re.sub(r'- \[x\] ', '- [✓] ', content, flags=re.IGNORECASE)
                with open(review_file, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print("✅ 已更新复习清单")
        except (EOFError, KeyboardInterrupt):
            print("\nℹ️  已跳过清空checkbox")


def main():
    parser = argparse.ArgumentParser(description='知识库复习管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # today 命令
    parser_today = subparsers.add_parser('today', help='生成今日复习清单')
    
    # mark-done 命令
    parser_mark = subparsers.add_parser('mark-done', help='标记为已复习')
    parser_mark.add_argument('filepath', type=str, help='文件路径')
    
    # sync 命令（新增）
    parser_sync = subparsers.add_parser('sync', help='从复习清单同步已勾选的笔记')
    
    # set-difficulty 命令
    parser_diff = subparsers.add_parser('set-difficulty', help='设置难度')
    parser_diff.add_argument('filepath', type=str, help='文件路径')
    parser_diff.add_argument('difficulty', type=str, choices=['easy', 'medium', 'hard'], help='难度等级')
    
    # stats 命令
    parser_stats = subparsers.add_parser('stats', help='显示统计信息')
    
    args = parser.parse_args()
    
    config = load_config()
    
    if args.command == 'today':
        # 归档旧的复习清单
        output_file = ROOT_DIR / "今日复习.md"
        if output_file.exists():
            # 读取旧文件的创建日期
            with open(output_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 从文件中提取日期
            date_match = re.search(r'\*\*生成时间\*\*: (\d{4}-\d{2}-\d{2})', content)
            if date_match:
                old_date = date_match.group(1)
                year, month, day = old_date.split('-')
                
                # 创建归档目录
                archive_dir = ROOT_DIR / "今日复习归档" / year / month
                archive_dir.mkdir(parents=True, exist_ok=True)
                
                # 归档文件
                archive_file = archive_dir / f"{old_date}.md"
                output_file.rename(archive_file)
                print(f"📦 已归档旧复习清单: 今日复习归档/{year}/{month}/{old_date}.md")
        
        print("🔍 扫描笔记文件...")
        notes = scan_notes(NOTES_DIR)
        print(f"📚 找到 {len(notes)} 篇笔记")
        
        print("📋 生成复习清单...")
        review_list = generate_review_list(notes, config)
        
        md_content = generate_review_markdown(review_list, config)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        print(f"✅ 复习清单已生成: {output_file}")
        print(f"\n统计:")
        print(f"  🔴 已过期: {len(review_list['overdue'])}")
        print(f"  ⭐ 今日: {len(review_list['today'])}")
        print(f"  📅 本周: {len(review_list['this_week'])}")
    
    elif args.command == 'mark-done':
        filepath = ROOT_DIR / args.filepath
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            return
        
        mark_as_reviewed(filepath, config)
    
    elif args.command == 'sync':
        sync_from_review_list(config)
    
    elif args.command == 'set-difficulty':
        filepath = ROOT_DIR / args.filepath
        if not filepath.exists():
            print(f"❌ 文件不存在: {filepath}")
            return
        
        set_difficulty(filepath, args.difficulty)
    
    elif args.command == 'stats':
        print("🔍 扫描笔记文件...")
        notes = scan_notes(NOTES_DIR)
        
        total = len(notes)
        with_metadata = sum(1 for n in notes if n.get('review_count') is not None)
        total_reviews = sum(n.get('review_count', 0) for n in notes)
        avg_mastery = sum(n.get('mastery_level', 0.0) for n in notes) / max(total, 1)
        
        print(f"\n📊 知识库统计")
        print(f"  总笔记数: {total}")
        print(f"  已添加元数据: {with_metadata} ({with_metadata/max(total,1)*100:.1f}%)")
        print(f"  总复习次数: {total_reviews}")
        print(f"  平均掌握度: {avg_mastery:.1%}")
        
        # 按难度分组
        by_difficulty = {}
        for note in notes:
            diff = note.get('difficulty', 'unknown')
            by_difficulty[diff] = by_difficulty.get(diff, 0) + 1
        
        print(f"\n  难度分布:")
        for diff, count in sorted(by_difficulty.items()):
            print(f"    {diff}: {count}")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

