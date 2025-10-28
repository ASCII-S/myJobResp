#!/usr/bin/env python3
"""
知识库游戏化管理器
功能：
1. 管理主题经验值和等级
2. 维护连击系统
3. 生成游戏化展示内容
"""

import os
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse

# 项目根目录（脚本在 system/scripts/ 中）
ROOT_DIR = Path(__file__).parent.parent.parent
NOTES_DIR = ROOT_DIR / "notes"
OUTLINES_DIR = ROOT_DIR / "面试大纲"

# 配置文件
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


# ============ 主题数据管理 ============

def load_topics_data(config: Dict) -> Dict:
    """加载主题数据"""
    data_dir = ROOT_DIR / config['gamification']['data_dir']
    data_file = data_dir / "topics.yaml"
    
    if not data_file.exists():
        return {}
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def save_topics_data(data: Dict, config: Dict):
    """保存主题数据"""
    data_dir = ROOT_DIR / config['gamification']['data_dir']
    data_dir.mkdir(parents=True, exist_ok=True)
    
    data_file = data_dir / "topics.yaml"
    with open(data_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def extract_topic_from_note(filepath: Path, notes_dir: Path) -> str:
    """从笔记文件路径提取主题名"""
    try:
        relative_path = filepath.relative_to(notes_dir)
        topic = relative_path.parts[0]
        return topic
    except (ValueError, IndexError):
        return "unknown"


def get_outline_path(topic: str, outlines_dir: Path) -> Optional[Path]:
    """根据主题名查找对应的大纲文件"""
    outline_path = outlines_dir / f"{topic}.md"
    if outline_path.exists():
        return outline_path
    return None


def calculate_level(xp: int, levels_config: List[Dict]) -> int:
    """根据XP计算等级索引"""
    level_idx = 0
    for idx, level in enumerate(levels_config):
        if xp >= level['required_xp']:
            level_idx = idx
        else:
            break
    return level_idx


def scan_topic_notes(topic: str, notes_dir: Path, config: Dict) -> Tuple[int, int]:
    """统计主题下的笔记总数和已掌握数"""
    topic_dir = notes_dir / topic
    if not topic_dir.exists():
        return 0, 0
    
    total = 0
    mastered = 0
    threshold = config['gamification']['mastery_threshold']
    
    for md_file in topic_dir.rglob("*.md"):
        if md_file.name.startswith('.') or md_file.name.startswith('_'):
            continue
        
        total += 1
        
        # 读取frontmatter检查掌握度
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            frontmatter, _ = parse_frontmatter(content)
            if frontmatter.get('mastery_level', 0) >= threshold:
                mastered += 1
        except Exception:
            continue
    
    return total, mastered


def update_topic_xp(topic: str, xp_gain: int, date: str, config: Dict):
    """更新主题经验值"""
    topics_data = load_topics_data(config)
    
    # 如果主题不存在，初始化它
    if topic not in topics_data:
        notes_dir = ROOT_DIR / config['paths']['notes_dir']
        outlines_dir = ROOT_DIR / config['paths']['outlines_dir']
        
        total, mastered = scan_topic_notes(topic, notes_dir, config)
        
        outline_path = get_outline_path(topic, outlines_dir)
        display_name = outline_path.stem if outline_path else topic
        
        topics_data[topic] = {
            'display_name': display_name,
            'current_xp': 0,
            'current_level': 0,
            'total_notes': total,
            'mastered_notes': mastered,
            'xp_history': {}
        }
    
    # 更新XP
    topics_data[topic]['current_xp'] = topics_data[topic].get('current_xp', 0) + xp_gain
    
    # 更新等级
    levels = config['gamification']['default_levels']
    topics_data[topic]['current_level'] = calculate_level(
        topics_data[topic]['current_xp'], 
        levels
    )
    
    # 记录历史
    if 'xp_history' not in topics_data[topic]:
        topics_data[topic]['xp_history'] = {}
    
    if date in topics_data[topic]['xp_history']:
        topics_data[topic]['xp_history'][date] += xp_gain
    else:
        topics_data[topic]['xp_history'][date] = xp_gain
    
    # 保存数据
    save_topics_data(topics_data, config)


def refresh_topic_stats(config: Dict):
    """刷新所有主题的笔记统计数据"""
    topics_data = load_topics_data(config)
    notes_dir = ROOT_DIR / config['paths']['notes_dir']
    
    for topic in topics_data:
        total, mastered = scan_topic_notes(topic, notes_dir, config)
        topics_data[topic]['total_notes'] = total
        topics_data[topic]['mastered_notes'] = mastered
    
    save_topics_data(topics_data, config)


# ============ 连击系统 ============

def load_streak_data(config: Dict) -> Dict:
    """加载连击数据"""
    data_dir = ROOT_DIR / config['gamification']['data_dir']
    data_file = data_dir / "streak.yaml"
    
    if not data_file.exists():
        return {
            'total_days': 0,
            'last_review_date': None,
            'history': []
        }
    
    with open(data_file, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {
            'total_days': 0,
            'last_review_date': None,
            'history': []
        }


def save_streak_data(data: Dict, config: Dict):
    """保存连击数据"""
    data_dir = ROOT_DIR / config['gamification']['data_dir']
    data_dir.mkdir(parents=True, exist_ok=True)
    
    data_file = data_dir / "streak.yaml"
    with open(data_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, allow_unicode=True, sort_keys=False)


def update_streak(date: str, config: Dict) -> int:
    """更新连击记录，返回总天数"""
    streak_data = load_streak_data(config)
    
    # 如果今天已经记录过，直接返回
    if date in streak_data['history']:
        return streak_data['total_days']
    
    # 添加今天
    streak_data['history'].append(date)
    streak_data['history'] = sorted(list(set(streak_data['history'])))  # 去重并排序
    streak_data['total_days'] = len(streak_data['history'])
    streak_data['last_review_date'] = date
    
    save_streak_data(streak_data, config)
    
    return streak_data['total_days']


def get_streak_emoji(days: int) -> str:
    """根据连击天数返回表情"""
    if days >= 30:
        return "🔥🔥🔥"
    elif days >= 7:
        return "🔥🔥"
    elif days >= 3:
        return "🔥"
    else:
        return "✨"


# ============ 展示格式化 ============

def generate_progress_bar(current: int, total: int, length: int = 10) -> str:
    """生成进度条"""
    if total == 0:
        filled = 0
    else:
        filled = int(current / total * length)
    
    bar = "█" * filled + "░" * (length - filled)
    return bar


def format_gamification_section(config: Dict) -> str:
    """格式化游戏化展示内容"""
    # 加载数据
    topics_data = load_topics_data(config)
    streak_data = load_streak_data(config)
    levels = config['gamification']['default_levels']
    
    md = "## 🎮 学习进展\n\n"
    
    # 连击系统
    if config['gamification']['streak']['enable']:
        streak_days = streak_data['total_days']
        emoji = get_streak_emoji(streak_days) if config['gamification']['streak']['show_icon'] else ""
        md += f"### 🔥 连击系统\n"
        md += f"连续学习：**{streak_days}天** {emoji}\n\n"
    
    # 主题掌握度
    md += "### 📊 主题掌握度\n\n"
    
    if not topics_data:
        md += "_暂无主题数据，请先运行: `python system/scripts/gamification.py init`_\n"
    else:
        md += "| 主题 | 等级 | 经验值 | 掌握情况 |\n"
        md += "|------|------|--------|----------|\n"
        
        # 按XP排序显示
        sorted_topics = sorted(
            topics_data.items(), 
            key=lambda x: x[1].get('current_xp', 0), 
            reverse=True
        )
        
        for topic, data in sorted_topics:
            display_name = data.get('display_name', topic)
            current_xp = data.get('current_xp', 0)
            level_idx = data.get('current_level', 0)
            total_notes = data.get('total_notes', 0)
            mastered_notes = data.get('mastered_notes', 0)
            
            # 获取等级信息
            if level_idx < len(levels):
                level_name = levels[level_idx]['name']
                level_icon = levels[level_idx]['icon']
            else:
                level_name = "未知"
                level_icon = "❓"
            
            # 计算下一等级所需XP
            if level_idx + 1 < len(levels):
                next_xp = levels[level_idx + 1]['required_xp']
            else:
                next_xp = current_xp  # 已满级
            
            # 生成XP进度条
            xp_bar = generate_progress_bar(current_xp, next_xp, 10)
            xp_text = f"{xp_bar} {current_xp}/{next_xp} XP"
            
            # 计算掌握百分比
            if total_notes > 0:
                mastery_pct = int(mastered_notes / total_notes * 100)
            else:
                mastery_pct = 0
            
            mastery_text = f"{mastered_notes}/{total_notes} ({mastery_pct}%)"
            
            md += f"| 🌟 {display_name} | {level_name} {level_icon} | {xp_text} | {mastery_text} |\n"
        
        md += "\n💡 **提示**: 复习笔记可获得经验值！首次掌握（80%+）额外获得50XP\n"
    
    return md


# ============ 命令行接口 ============

def init_gamification_data(config: Dict):
    """初始化所有主题的游戏化数据"""
    print("🔍 扫描笔记和大纲...")
    
    notes_dir = ROOT_DIR / config['paths']['notes_dir']
    outlines_dir = ROOT_DIR / config['paths']['outlines_dir']
    
    # 获取所有主题（从笔记目录的第一级子目录）
    topics = [d.name for d in notes_dir.iterdir() if d.is_dir() and not d.name.startswith('.') and not d.name.startswith('_')]
    
    topics_data = {}
    
    for topic in topics:
        print(f"\n📚 处理主题: {topic}")
        
        # 扫描该主题下的笔记
        total, mastered = scan_topic_notes(topic, notes_dir, config)
        
        # 查找对应的大纲文件获取display_name
        outline_path = get_outline_path(topic, outlines_dir)
        if outline_path:
            display_name = outline_path.stem
        else:
            display_name = topic
        
        topics_data[topic] = {
            'display_name': display_name,
            'current_xp': 0,
            'current_level': 0,
            'total_notes': total,
            'mastered_notes': mastered,
            'xp_history': {}
        }
        
        print(f"  总笔记: {total}, 已掌握: {mastered}")
    
    # 保存数据
    save_topics_data(topics_data, config)
    
    # 初始化连击数据
    streak_data = {
        'total_days': 0,
        'last_review_date': None,
        'history': []
    }
    save_streak_data(streak_data, config)
    
    print(f"\n✅ 初始化完成！共 {len(topics_data)} 个主题")


def show_stats(config: Dict):
    """显示游戏化统计"""
    topics_data = load_topics_data(config)
    streak_data = load_streak_data(config)
    levels = config['gamification']['default_levels']
    
    print("\n" + "="*50)
    print("📊 知识库游戏化统计")
    print("="*50)
    
    # 连击信息
    print(f"\n🔥 连击系统")
    print(f"   总天数: {streak_data['total_days']}天")
    print(f"   最后学习: {streak_data.get('last_review_date', 'N/A')}")
    
    # 主题统计
    print(f"\n📚 主题统计 (共{len(topics_data)}个)")
    
    if not topics_data:
        print("   暂无数据")
    else:
        # 按XP排序
        sorted_topics = sorted(
            topics_data.items(), 
            key=lambda x: x[1].get('current_xp', 0), 
            reverse=True
        )
        
        for topic, data in sorted_topics:
            display_name = data.get('display_name', topic)
            current_xp = data.get('current_xp', 0)
            level_idx = data.get('current_level', 0)
            total_notes = data.get('total_notes', 0)
            mastered_notes = data.get('mastered_notes', 0)
            
            level_name = levels[level_idx]['name'] if level_idx < len(levels) else "未知"
            level_icon = levels[level_idx]['icon'] if level_idx < len(levels) else "❓"
            
            mastery_pct = int(mastered_notes / total_notes * 100) if total_notes > 0 else 0
            
            print(f"\n   {level_icon} {display_name}")
            print(f"      等级: {level_name} ({current_xp} XP)")
            print(f"      掌握: {mastered_notes}/{total_notes} ({mastery_pct}%)")
    
    print("\n" + "="*50 + "\n")


def show_streak_history(config: Dict):
    """显示连击历史"""
    streak_data = load_streak_data(config)
    
    print("\n" + "="*50)
    print("🔥 连击历史")
    print("="*50)
    
    print(f"\n总天数: {streak_data['total_days']}天")
    print(f"最后学习: {streak_data.get('last_review_date', 'N/A')}")
    
    if streak_data['history']:
        print(f"\n学习日期记录 (最近10天):")
        recent = streak_data['history'][-10:]
        for date in recent:
            print(f"  - {date}")
    else:
        print("\n暂无记录")
    
    print("\n" + "="*50 + "\n")


def set_topic_xp(topic: str, xp: int, config: Dict):
    """手动设置主题XP"""
    topics_data = load_topics_data(config)
    
    if topic not in topics_data:
        print(f"❌ 主题 '{topic}' 不存在")
        print(f"可用主题: {', '.join(topics_data.keys())}")
        return
    
    topics_data[topic]['current_xp'] = xp
    
    # 重新计算等级
    levels = config['gamification']['default_levels']
    topics_data[topic]['current_level'] = calculate_level(xp, levels)
    
    save_topics_data(topics_data, config)
    
    level_idx = topics_data[topic]['current_level']
    level_name = levels[level_idx]['name'] if level_idx < len(levels) else "未知"
    
    print(f"✅ 已设置 {topic} 的XP为 {xp}")
    print(f"   当前等级: {level_name}")


def refresh_stats(config: Dict):
    """刷新所有主题的统计数据"""
    print("🔄 刷新主题统计数据...")
    refresh_topic_stats(config)
    print("✅ 刷新完成")


def main():
    parser = argparse.ArgumentParser(description='知识库游戏化管理器')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # stats 命令
    parser_stats = subparsers.add_parser('stats', help='查看游戏化统计')
    
    # init 命令
    parser_init = subparsers.add_parser('init', help='初始化游戏化数据')
    
    # set-xp 命令
    parser_setxp = subparsers.add_parser('set-xp', help='手动设置主题XP')
    parser_setxp.add_argument('topic', type=str, help='主题名')
    parser_setxp.add_argument('xp', type=int, help='经验值')
    
    # streak 命令
    parser_streak = subparsers.add_parser('streak', help='查看连击历史')
    
    # refresh 命令
    parser_refresh = subparsers.add_parser('refresh', help='刷新主题统计数据')
    
    args = parser.parse_args()
    
    config = load_config()
    
    if args.command == 'init':
        init_gamification_data(config)
    elif args.command == 'stats':
        show_stats(config)
    elif args.command == 'set-xp':
        set_topic_xp(args.topic, args.xp, config)
    elif args.command == 'streak':
        show_streak_history(config)
    elif args.command == 'refresh':
        refresh_stats(config)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

