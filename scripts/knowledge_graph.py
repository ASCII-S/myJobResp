 #!/usr/bin/env python3
"""
知识图谱生成器
功能：
1. 生成知识点之间的关联图
2. 输出可视化HTML（使用vis.js）
3. 生成文本版知识图谱索引
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set
import argparse
import yaml

# 项目根目录
ROOT_DIR = Path(__file__).parent.parent
NOTES_DIR = ROOT_DIR / "notes"
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


def extract_internal_links(body: str, current_file: Path) -> List[str]:
    """提取文档中的内部链接"""
    # 匹配 Markdown 链接：[text](path)
    pattern = r'\[([^\]]+)\]\(([^\)]+\.md)\)'
    matches = re.findall(pattern, body)
    
    links = []
    for text, link_path in matches:
        # 处理相对路径
        if not link_path.startswith('http'):
            # 解析相对路径
            if link_path.startswith('../'):
                target_path = (current_file.parent / link_path).resolve()
            else:
                target_path = (current_file.parent / link_path).resolve()
            
            if target_path.exists():
                links.append(str(target_path))
    
    return links


def build_graph(notes_dir: Path) -> Tuple[List[Dict], List[Dict]]:
    """构建知识图谱的节点和边"""
    nodes = []
    edges = []
    
    # 文件路径到ID的映射
    file_to_id = {}
    
    print("🔍 扫描笔记文件...")
    all_files = list(notes_dir.rglob("*.md"))
    
    # 创建节点
    for i, md_file in enumerate(all_files):
        if md_file.name.startswith('.'):
            continue
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        frontmatter, body = parse_frontmatter(content)
        
        # 从路径提取主题
        parts = md_file.relative_to(notes_dir).parts
        topic = parts[0] if parts else 'other'
        
        node = {
            'id': i,
            'label': md_file.stem,
            'title': md_file.stem,  # 悬停提示
            'filepath': str(md_file),
            'topic': topic,
            'review_count': frontmatter.get('review_count', 0),
            'mastery_level': frontmatter.get('mastery_level', 0.0),
            'tags': frontmatter.get('tags', []),
        }
        
        nodes.append(node)
        file_to_id[str(md_file)] = i
    
    print(f"📚 找到 {len(nodes)} 个节点")
    
    # 创建边（基于链接）
    print("🔗 分析链接关系...")
    for node in nodes:
        filepath = Path(node['filepath'])
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        _, body = parse_frontmatter(content)
        links = extract_internal_links(body, filepath)
        
        for target_path in links:
            if target_path in file_to_id:
                edge = {
                    'from': node['id'],
                    'to': file_to_id[target_path],
                    'weight': 1
                }
                edges.append(edge)
    
    print(f"🔗 找到 {len(edges)} 条连接")
    
    return nodes, edges


def generate_html_visualization(nodes: List[Dict], edges: List[Dict], output_file: Path) -> None:
    """生成HTML可视化文件"""
    # 为不同主题分配颜色
    topics = list(set(node['topic'] for node in nodes))
    colors = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c', '#34495e', '#e67e22']
    topic_colors = {topic: colors[i % len(colors)] for i, topic in enumerate(topics)}
    
    # 转换节点格式
    vis_nodes = []
    for node in nodes:
        # 节点大小基于复习次数和链接数
        size = 10 + node['review_count'] * 2
        
        vis_node = {
            'id': node['id'],
            'label': node['label'][:30],  # 限制显示长度
            'title': f"{node['title']}<br>复习: {node['review_count']}次<br>掌握: {node['mastery_level']:.0%}",
            'color': topic_colors.get(node['topic'], '#95a5a6'),
            'size': size,
            'topic': node['topic']
        }
        vis_nodes.append(vis_node)
    
    # HTML模板
    html_template = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>知识图谱 - 可视化</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        #mynetwork {
            width: 100%;
            height: 100vh;
            border: 1px solid lightgray;
        }
        #info {
            position: absolute;
            top: 10px;
            left: 10px;
            background: white;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
        }
        .legend {
            margin-top: 10px;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div id="info">
        <h3>📚 知识图谱</h3>
        <p>节点: <span id="nodeCount">0</span></p>
        <p>连接: <span id="edgeCount">0</span></p>
        <div class="legend">
            <h4>主题分类</h4>
            <div id="legendItems"></div>
        </div>
    </div>
    <div id="mynetwork"></div>

    <script type="text/javascript">
        // 数据
        var nodes = new vis.DataSet(""" + json.dumps(vis_nodes, ensure_ascii=False) + """);
        var edges = new vis.DataSet(""" + json.dumps(edges, ensure_ascii=False) + """);

        // 容器
        var container = document.getElementById('mynetwork');
        
        // 数据
        var data = {
            nodes: nodes,
            edges: edges
        };
        
        // 配置
        var options = {
            nodes: {
                shape: 'dot',
                font: {
                    size: 14,
                    face: 'Arial'
                },
                borderWidth: 2,
                shadow: true
            },
            edges: {
                width: 1,
                color: {color: '#848484', highlight: '#2B7CE9'},
                smooth: {
                    type: 'continuous'
                }
            },
            physics: {
                stabilization: false,
                barnesHut: {
                    gravitationalConstant: -20000,
                    springConstant: 0.001,
                    springLength: 200
                }
            },
            interaction: {
                hover: true,
                tooltipDelay: 100,
                navigationButtons: true,
                keyboard: true
            }
        };
        
        // 创建网络
        var network = new vis.Network(container, data, options);
        
        // 更新统计信息
        document.getElementById('nodeCount').textContent = nodes.length;
        document.getElementById('edgeCount').textContent = edges.length;
        
        // 生成图例
        var topics = """ + json.dumps(topic_colors, ensure_ascii=False) + """;
        var legendHTML = '';
        for (var topic in topics) {
            legendHTML += '<div class="legend-item">';
            legendHTML += '<div class="legend-color" style="background-color: ' + topics[topic] + '"></div>';
            legendHTML += '<span>' + topic + '</span>';
            legendHTML += '</div>';
        }
        document.getElementById('legendItems').innerHTML = legendHTML;
        
        // 点击节点时的处理
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var node = nodes.get(nodeId);
                console.log("点击节点:", node.label);
            }
        });
    </script>
</body>
</html>"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_template)


def generate_text_index(nodes: List[Dict], edges: List[Dict]) -> str:
    """生成文本版知识图谱"""
    # 统计每个节点的连接数
    node_connections = {node['id']: {'in': 0, 'out': 0} for node in nodes}
    for edge in edges:
        node_connections[edge['from']]['out'] += 1
        node_connections[edge['to']]['in'] += 1
    
    # 按主题分组
    by_topic = {}
    for node in nodes:
        topic = node['topic']
        if topic not in by_topic:
            by_topic[topic] = []
        by_topic[topic].append(node)
    
    # 生成Markdown
    md = f"""# 🕸️ 知识图谱索引

**总节点数**: {len(nodes)}
**总连接数**: {len(edges)}
**主题数**: {len(by_topic)}

---

## 📊 统计概览

### 连接最多的节点（Hub节点）

"""
    
    # 找出连接最多的节点
    hub_nodes = sorted(nodes, key=lambda n: node_connections[n['id']]['in'] + node_connections[n['id']]['out'], reverse=True)[:10]
    
    for node in hub_nodes:
        conn = node_connections[node['id']]
        total_conn = conn['in'] + conn['out']
        rel_path = Path(node['filepath']).relative_to(ROOT_DIR)
        md += f"- [{node['label']}]({rel_path}) - {total_conn}个连接 (入: {conn['in']}, 出: {conn['out']})\n"
    
    md += "\n---\n\n## 📚 按主题分类\n\n"
    
    for topic in sorted(by_topic.keys()):
        topic_nodes = by_topic[topic]
        md += f"### {topic} ({len(topic_nodes)}篇)\n\n"
        
        # 按复习次数排序
        topic_nodes.sort(key=lambda n: n['review_count'], reverse=True)
        
        for node in topic_nodes[:20]:  # 每个主题最多显示20个
            conn = node_connections[node['id']]
            total_conn = conn['in'] + conn['out']
            rel_path = Path(node['filepath']).relative_to(ROOT_DIR)
            mastery = node['mastery_level']
            
            md += f"- [{node['label']}]({rel_path})"
            md += f" | 复习: {node['review_count']}次"
            md += f" | 掌握: {mastery:.0%}"
            md += f" | 连接: {total_conn}\n"
        
        if len(topic_nodes) > 20:
            md += f"\n_...还有 {len(topic_nodes) - 20} 篇_\n"
        
        md += "\n"
    
    md += """---

## 📖 如何使用

1. **查看可视化图谱**：打开 `docs/knowledge_graph.html`
2. **查找Hub节点**：这些是核心概念，值得重点学习
3. **发现孤立节点**：没有连接的节点需要建立关联
4. **按主题浏览**：系统化地复习某个领域

"""
    
    return md


def main():
    parser = argparse.ArgumentParser(description='知识图谱生成器')
    parser.add_argument('--html', action='store_true', help='生成HTML可视化')
    parser.add_argument('--text', action='store_true', help='生成文本索引')
    parser.add_argument('--all', action='store_true', help='生成所有格式')
    
    args = parser.parse_args()
    
    if not any([args.html, args.text, args.all]):
        args.all = True
    
    config = load_config()
    
    # 构建图谱
    nodes, edges = build_graph(NOTES_DIR)
    
    # 生成HTML可视化
    if args.html or args.all:
        if config['knowledge_graph']['generate_html']:
            print("🌐 生成HTML可视化...")
            html_output = ROOT_DIR / "docs" / "knowledge_graph.html"
            html_output.parent.mkdir(exist_ok=True)
            generate_html_visualization(nodes, edges, html_output)
            print(f"✅ HTML已生成: {html_output}")
        else:
            print("ℹ️  HTML生成已在配置中禁用")
    
    # 生成文本索引
    if args.text or args.all:
        print("📄 生成文本索引...")
        text_content = generate_text_index(nodes, edges)
        text_output = ROOT_DIR / "面试大纲" / "_知识图谱.md"
        with open(text_output, 'w', encoding='utf-8') as f:
            f.write(text_content)
        print(f"✅ 文本索引已生成: {text_output}")
    
    print("\n✅ 知识图谱生成完成")


if __name__ == '__main__':
    main()

