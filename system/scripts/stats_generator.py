#!/usr/bin/env python3
"""
统计报表生成器
功能：
1. 生成学习统计报表
2. 分析复习进度
3. 可视化学习趋势
"""

import os
import re
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter, defaultdict
import argparse

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


def parse_frontmatter(content: str) -> Dict:
    """解析文档的frontmatter"""
    pattern = r'^---\s*\n(.*?)\n---\s*\n'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        frontmatter_str = match.group(1)
        try:
            return yaml.safe_load(frontmatter_str) or {}
        except yaml.YAMLError:
            return {}
    return {}


def scan_all_notes(notes_dir: Path) -> List[Dict]:
    """扫描所有笔记"""
    notes = []
    
    for md_file in notes_dir.rglob("*.md"):
        if md_file.name.startswith('.'):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter = parse_frontmatter(content)
        
        # 从路径提取主题
        parts = md_file.relative_to(notes_dir).parts
        topic = parts[0] if parts else 'other'
        
        note_info = {
            'filepath': md_file,
            'relative_path': md_file.relative_to(ROOT_DIR),
            'title': md_file.stem,
            'topic': topic,
            **frontmatter
        }
        notes.append(note_info)
    
    return notes


def analyze_review_status(notes: List[Dict]) -> Dict:
    """分析复习状态"""
    today = datetime.now().date()
    
    status = {
        'total': len(notes),
        'with_metadata': 0,
        'never_reviewed': 0,
        'overdue': 0,
        'today': 0,
        'this_week': 0,
        'well_maintained': 0
    }
    
    for note in notes:
        # 检查是否有元数据
        if note.get('review_count') is not None:
            status['with_metadata'] += 1
            
            review_count = note.get('review_count', 0)
            next_review = note.get('next_review')
            
            if review_count == 0:
                status['never_reviewed'] += 1
            elif next_review:
                if isinstance(next_review, str):
                    next_review = datetime.strptime(next_review, '%Y-%m-%d').date()
                
                diff_days = (next_review - today).days
                
                if diff_days < 0:
                    status['overdue'] += 1
                elif diff_days == 0:
                    status['today'] += 1
                elif diff_days <= 7:
                    status['this_week'] += 1
                else:
                    status['well_maintained'] += 1
    
    return status


def analyze_by_topic(notes: List[Dict]) -> Dict[str, Dict]:
    """按主题分析"""
    by_topic = defaultdict(lambda: {
        'count': 0,
        'total_reviews': 0,
        'avg_mastery': 0.0,
        'notes': []
    })
    
    for note in notes:
        topic = note.get('topic', 'other')
        by_topic[topic]['count'] += 1
        by_topic[topic]['total_reviews'] += note.get('review_count', 0)
        by_topic[topic]['notes'].append(note)
    
    # 计算平均掌握度
    for topic, data in by_topic.items():
        if data['notes']:
            avg_mastery = sum(n.get('mastery_level', 0.0) for n in data['notes']) / len(data['notes'])
            data['avg_mastery'] = avg_mastery
    
    return dict(by_topic)


def analyze_learning_trend(notes: List[Dict], days: int = 30) -> Dict:
    """分析学习趋势"""
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    
    # 按日期统计创建和复习
    daily_created = Counter()
    daily_reviewed = Counter()
    
    for note in notes:
        # 创建日期
        created = note.get('created')
        if created:
            if isinstance(created, str):
                created = datetime.strptime(created, '%Y-%m-%d').date()
            if start_date <= created <= today:
                daily_created[created] += 1
        
        # 最后复习日期
        last_reviewed = note.get('last_reviewed')
        if last_reviewed:
            if isinstance(last_reviewed, str):
                last_reviewed = datetime.strptime(last_reviewed, '%Y-%m-%d').date()
            if start_date <= last_reviewed <= today:
                daily_reviewed[last_reviewed] += 1
    
    return {
        'daily_created': dict(daily_created),
        'daily_reviewed': dict(daily_reviewed),
        'period_days': days
    }


def analyze_tags(notes: List[Dict]) -> List[Tuple[str, int]]:
    """分析标签使用"""
    tag_counter = Counter()
    
    for note in notes:
        tags = note.get('tags', [])
        for tag in tags:
            tag_counter[tag] += 1
    
    return tag_counter.most_common(20)


def generate_ascii_bar_chart(data: List[Tuple[str, int]], max_width: int = 30) -> str:
    """生成ASCII柱状图"""
    if not data:
        return ""
    
    max_value = max(count for _, count in data)
    chart = ""
    
    for label, count in data:
        bar_length = int((count / max_value) * max_width)
        bar = '█' * bar_length
        chart += f"{label:20s} {bar} {count}\n"
    
    return chart


def generate_report(notes: List[Dict], config: Dict) -> str:
    """生成统计报表"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 基础统计
    review_status = analyze_review_status(notes)
    by_topic = analyze_by_topic(notes)
    trend = analyze_learning_trend(notes, days=30)
    top_tags = analyze_tags(notes)
    
    # 总复习次数
    total_reviews = sum(n.get('review_count', 0) for n in notes)
    avg_mastery = sum(n.get('mastery_level', 0.0) for n in notes) / max(len(notes), 1)
    
    md = f"""# 📊 知识库统计报表

**生成时间**: {today}

---

## 📈 总体概况

| 指标 | 数值 |
|------|------|
| 📚 总笔记数 | {review_status['total']} |
| ✅ 已添加元数据 | {review_status['with_metadata']} ({review_status['with_metadata']/max(review_status['total'],1)*100:.1f}%) |
| 🔄 总复习次数 | {total_reviews} |
| 🎯 平均掌握度 | {avg_mastery:.1%} |
| 📖 平均每篇复习 | {total_reviews/max(review_status['total'],1):.1f}次 |

---

## 🔔 复习状态

| 状态 | 数量 | 占比 |
|------|------|------|
| 🆕 从未复习 | {review_status['never_reviewed']} | {review_status['never_reviewed']/max(review_status['with_metadata'],1)*100:.1f}% |
| 🔴 已过期 | {review_status['overdue']} | {review_status['overdue']/max(review_status['with_metadata'],1)*100:.1f}% |
| ⭐ 今日应复习 | {review_status['today']} | {review_status['today']/max(review_status['with_metadata'],1)*100:.1f}% |
| 📅 本周计划 | {review_status['this_week']} | {review_status['this_week']/max(review_status['with_metadata'],1)*100:.1f}% |
| ✅ 维护良好 | {review_status['well_maintained']} | {review_status['well_maintained']/max(review_status['with_metadata'],1)*100:.1f}% |

"""
    
    # 如果有过期的笔记，添加警告
    if review_status['overdue'] > 10:
        md += f"\n⚠️ **警告**: 有 {review_status['overdue']} 篇笔记已过期，建议优先复习！\n\n"
    
    md += "---\n\n## 📚 主题分布\n\n"
    
    # 按笔记数排序
    sorted_topics = sorted(by_topic.items(), key=lambda x: x[1]['count'], reverse=True)
    
    md += "| 主题 | 笔记数 | 总复习次数 | 平均掌握度 |\n"
    md += "|------|--------|------------|------------|\n"
    
    for topic, data in sorted_topics:
        md += f"| {topic} | {data['count']} | {data['total_reviews']} | {data['avg_mastery']:.1%} |\n"
    
    md += "\n### 笔记数量分布\n\n```\n"
    topic_chart_data = [(topic, data['count']) for topic, data in sorted_topics[:10]]
    md += generate_ascii_bar_chart(topic_chart_data)
    md += "```\n\n"
    
    md += "---\n\n## 🏆 掌握度排行\n\n"
    
    # 掌握度最高的笔记
    mastered_notes = [n for n in notes if n.get('mastery_level', 0) > 0]
    mastered_notes.sort(key=lambda n: n.get('mastery_level', 0), reverse=True)
    
    md += "### Top 10 已掌握\n\n"
    for note in mastered_notes[:10]:
        mastery = note.get('mastery_level', 0)
        review_count = note.get('review_count', 0)
        md += f"- [{note['title']}]({note['relative_path']}) - {mastery:.0%} (复习{review_count}次)\n"
    
    md += "\n### Top 10 需加强\n\n"
    needs_work = [n for n in notes if n.get('review_count', 0) > 0 and n.get('mastery_level', 0) < 0.5]
    needs_work.sort(key=lambda n: n.get('mastery_level', 0))
    
    for note in needs_work[:10]:
        mastery = note.get('mastery_level', 0)
        review_count = note.get('review_count', 0)
        md += f"- [{note['title']}]({note['relative_path']}) - {mastery:.0%} (复习{review_count}次)\n"
    
    md += "\n---\n\n## 📅 近30天学习趋势\n\n"
    
    # 统计近30天的活跃度
    created_count = len(trend['daily_created'])
    reviewed_count = len(trend['daily_reviewed'])
    total_created = sum(trend['daily_created'].values())
    total_reviewed = sum(trend['daily_reviewed'].values())
    
    md += f"- 📝 新建笔记: {total_created} 篇（{created_count} 个活跃日）\n"
    md += f"- 🔄 复习笔记: {total_reviewed} 次（{reviewed_count} 个活跃日）\n"
    md += f"- 📊 日均新建: {total_created/30:.1f} 篇\n"
    md += f"- 📊 日均复习: {total_reviewed/30:.1f} 次\n"
    
    md += "\n---\n\n## 🏷️ 热门标签 Top 20\n\n"
    
    if top_tags:
        md += "```\n"
        md += generate_ascii_bar_chart(top_tags)
        md += "```\n"
    else:
        md += "暂无标签数据\n"
    
    md += "\n---\n\n## 💡 建议\n\n"
    
    # 根据数据给出建议
    suggestions = []
    
    if review_status['never_reviewed'] > review_status['with_metadata'] * 0.3:
        suggestions.append(f"- 📌 有 {review_status['never_reviewed']} 篇笔记从未复习，建议尽快进行首次复习")
    
    if review_status['overdue'] > 10:
        suggestions.append(f"- ⏰ 有 {review_status['overdue']} 篇笔记已过期，建议优先处理")
    
    if total_created < 30:
        suggestions.append("- 📝 最近30天新建笔记较少，保持持续学习的习惯")
    
    if total_reviewed < 30:
        suggestions.append("- 🔄 最近30天复习较少，建议增加复习频率")
    
    if avg_mastery < 0.3:
        suggestions.append("- 🎯 整体掌握度偏低，建议增加复习次数")
    
    # 找出薄弱主题
    weak_topics = [topic for topic, data in by_topic.items() if data['avg_mastery'] < 0.3 and data['count'] > 5]
    if weak_topics:
        suggestions.append(f"- 📚 以下主题需要加强: {', '.join(weak_topics)}")
    
    if suggestions:
        md += "\n".join(suggestions)
    else:
        md += "✅ 知识库维护良好，继续保持！\n"
    
    md += "\n\n---\n\n## 📖 如何使用\n\n"
    md += """1. **定期查看报表**：建议每周查看一次，了解学习进度
2. **关注过期笔记**：及时复习已过期的内容
3. **平衡主题学习**：注意各主题的掌握度是否均衡
4. **保持学习节奏**：参考学习趋势，保持稳定的学习习惯

### 更新报表

```bash
python scripts/stats_generator.py
```
"""
    
    return md


def main():
    parser = argparse.ArgumentParser(description='统计报表生成器')
    parser.add_argument('--days', type=int, default=30, help='分析的天数范围')
    
    args = parser.parse_args()
    config = load_config()
    
    print("🔍 扫描笔记文件...")
    notes = scan_all_notes(NOTES_DIR)
    print(f"📚 找到 {len(notes)} 篇笔记")
    
    print("📊 生成统计报表...")
    report_content = generate_report(notes, config)
    
    output_file = ROOT_DIR / "面试大纲" / "_统计报表.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"✅ 报表已生成: {output_file}")
    
    # 输出关键指标到终端
    review_status = analyze_review_status(notes)
    print(f"\n📈 关键指标:")
    print(f"  总笔记: {review_status['total']}")
    print(f"  已过期: {review_status['overdue']}")
    print(f"  今日应复习: {review_status['today']}")


if __name__ == '__main__':
    main()

