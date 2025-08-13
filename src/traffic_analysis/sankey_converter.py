"""
桑基图数据转换器

专门用于将交通数据转换为各种桑基图可视化工具所需的格式
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
import json


class SankeyConverter:
    """桑基图数据转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.nodes = []
        self.links = []
        self.node_mapping = {}
        
    def create_node_mapping(self, data: List[Dict]) -> Dict[str, int]:
        """
        创建节点映射表
        
        Args:
            data: 桑基图数据列表
            
        Returns:
            节点名称到索引的映射字典
        """
        unique_nodes = set()
        
        for item in data:
            unique_nodes.add(item['source'])
            unique_nodes.add(item['target'])
        
        self.node_mapping = {node: idx for idx, node in enumerate(sorted(unique_nodes))}
        return self.node_mapping
    
    def convert_to_plotly_format(self, data: List[Dict]) -> Dict:
        """
        转换为Plotly桑基图格式
        
        Args:
            data: 桑基图数据列表
            
        Returns:
            Plotly格式的桑基图数据
        """
        # 创建节点映射
        node_mapping = self.create_node_mapping(data)
        
        # 准备节点数据
        nodes = {
            'label': list(node_mapping.keys()),
            'color': self._generate_node_colors(len(node_mapping))
        }
        
        # 准备链接数据
        links = {
            'source': [node_mapping[item['source']] for item in data],
            'target': [node_mapping[item['target']] for item in data],
            'value': [item['value'] for item in data],
            'color': self._generate_link_colors(len(data))
        }
        
        return {
            'type': 'sankey',
            'node': nodes,
            'link': links
        }
    
    def convert_to_d3_format(self, data: List[Dict]) -> Dict:
        """
        转换为D3.js桑基图格式
        
        Args:
            data: 桑基图数据列表
            
        Returns:
            D3格式的桑基图数据
        """
        # 创建节点映射
        node_mapping = self.create_node_mapping(data)
        
        # 准备节点数据
        nodes = [{'name': name, 'id': idx} for name, idx in node_mapping.items()]
        
        # 准备链接数据
        links = []
        for item in data:
            links.append({
                'source': node_mapping[item['source']],
                'target': node_mapping[item['target']],
                'value': item['value']
            })
        
        return {
            'nodes': nodes,
            'links': links
        }
    
    def convert_to_echarts_format(self, data: List[Dict]) -> Dict:
        """
        转换为ECharts桑基图格式
        
        Args:
            data: 桑基图数据列表
            
        Returns:
            ECharts格式的桑基图数据
        """
        # 创建节点映射
        node_mapping = self.create_node_mapping(data)
        
        # 准备节点数据
        nodes = [{'name': name} for name in node_mapping.keys()]
        
        # 准备链接数据
        links = []
        for item in data:
            links.append({
                'source': item['source'],
                'target': item['target'],
                'value': item['value']
            })
        
        return {
            'type': 'sankey',
            'data': nodes,
            'links': links,
            'layout': 'none',
            'focusNodeAdjacency': 'allEdges',
            'itemStyle': {
                'borderWidth': 1,
                'borderColor': '#aaa'
            },
            'lineStyle': {
                'color': 'source',
                'curveness': 0.5
            }
        }
    
    def create_hierarchical_sankey(self, data: List[Dict], 
                                  hierarchy_levels: List[str]) -> List[Dict]:
        """
        创建分层桑基图数据
        
        Args:
            data: 原始桑基图数据
            hierarchy_levels: 层级列表
            
        Returns:
            分层桑基图数据
        """
        hierarchical_data = []
        
        # 按层级重新组织数据
        for level_idx in range(len(hierarchy_levels) - 1):
            current_level = hierarchy_levels[level_idx]
            next_level = hierarchy_levels[level_idx + 1]
            
            # 这里可以根据实际需求实现层级逻辑
            # 示例：按区域->道路->交叉口的层级
            for item in data:
                hierarchical_item = {
                    'source': f"{current_level}_{item['source']}",
                    'target': f"{next_level}_{item['target']}",
                    'value': item['value']
                }
                hierarchical_data.append(hierarchical_item)
        
        return hierarchical_data
    
    def filter_by_threshold(self, data: List[Dict], 
                           min_value: int = 0, 
                           top_n: Optional[int] = None) -> List[Dict]:
        """
        按阈值过滤桑基图数据
        
        Args:
            data: 桑基图数据列表
            min_value: 最小值阈值
            top_n: 保留前N个最大值
            
        Returns:
            过滤后的数据
        """
        # 按最小值过滤
        filtered_data = [item for item in data if item['value'] >= min_value]
        
        # 按前N个过滤
        if top_n is not None:
            filtered_data = sorted(filtered_data, 
                                 key=lambda x: x['value'], 
                                 reverse=True)[:top_n]
        
        return filtered_data
    
    def add_flow_direction_info(self, data: List[Dict]) -> List[Dict]:
        """
        添加流向信息
        
        Args:
            data: 桑基图数据列表
            
        Returns:
            包含流向信息的数据
        """
        enhanced_data = []
        
        for item in data:
            enhanced_item = item.copy()
            
            # 添加流向描述
            enhanced_item['flow_description'] = f"从{item['source']}到{item['target']}"
            
            # 添加流量等级
            if item['value'] > 1000:
                enhanced_item['flow_level'] = '高'
            elif item['value'] > 500:
                enhanced_item['flow_level'] = '中'
            else:
                enhanced_item['flow_level'] = '低'
            
            enhanced_data.append(enhanced_item)
        
        return enhanced_data
    
    def _generate_node_colors(self, count: int) -> List[str]:
        """生成节点颜色"""
        colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        # 如果节点数量超过预定义颜色，则循环使用
        return [colors[i % len(colors)] for i in range(count)]
    
    def _generate_link_colors(self, count: int) -> List[str]:
        """生成链接颜色（半透明）"""
        base_colors = [
            'rgba(31, 119, 180, 0.4)', 'rgba(255, 127, 14, 0.4)', 
            'rgba(44, 160, 44, 0.4)', 'rgba(214, 39, 40, 0.4)',
            'rgba(148, 103, 189, 0.4)', 'rgba(140, 86, 75, 0.4)',
            'rgba(227, 119, 194, 0.4)', 'rgba(127, 127, 127, 0.4)',
            'rgba(188, 189, 34, 0.4)', 'rgba(23, 190, 207, 0.4)'
        ]
        
        return [base_colors[i % len(base_colors)] for i in range(count)]
    
    def generate_sankey_config(self, title: str = "交通流量桑基图",
                              width: int = 800, 
                              height: int = 600) -> Dict:
        """
        生成桑基图配置
        
        Args:
            title: 图表标题
            width: 图表宽度
            height: 图表高度
            
        Returns:
            图表配置字典
        """
        return {
            'title': title,
            'width': width,
            'height': height,
            'margin': {'top': 50, 'right': 50, 'bottom': 50, 'left': 50},
            'nodeWidth': 15,
            'nodePadding': 10,
            'iterations': 32,
            'format': '.0f',
            'unit': '车次'
        }
    
    def export_multiple_formats(self, data: List[Dict], 
                               base_filename: str = 'traffic_sankey') -> Dict[str, str]:
        """
        导出多种格式的桑基图数据
        
        Args:
            data: 桑基图数据列表
            base_filename: 基础文件名
            
        Returns:
            导出文件路径字典
        """
        exported_files = {}
        
        # Plotly格式
        plotly_data = self.convert_to_plotly_format(data)
        plotly_file = f"{base_filename}_plotly.json"
        with open(plotly_file, 'w', encoding='utf-8') as f:
            json.dump(plotly_data, f, ensure_ascii=False, indent=2)
        exported_files['plotly'] = plotly_file
        
        # D3格式
        d3_data = self.convert_to_d3_format(data)
        d3_file = f"{base_filename}_d3.json"
        with open(d3_file, 'w', encoding='utf-8') as f:
            json.dump(d3_data, f, ensure_ascii=False, indent=2)
        exported_files['d3'] = d3_file
        
        # ECharts格式
        echarts_data = self.convert_to_echarts_format(data)
        echarts_file = f"{base_filename}_echarts.json"
        with open(echarts_file, 'w', encoding='utf-8') as f:
            json.dump(echarts_data, f, ensure_ascii=False, indent=2)
        exported_files['echarts'] = echarts_file
        
        return exported_files


def main():
    """演示桑基图转换功能"""
    print("=== 桑基图转换器演示 ===\n")
    
    # 示例数据
    sample_data = [
        {'source': '市中心广场', 'target': '商业区', 'value': 1500},
        {'source': '火车站', 'target': '市中心广场', 'value': 1200},
        {'source': '住宅区A', 'target': '商业区', 'value': 800},
        {'source': '住宅区B', 'target': '工业园区', 'value': 600},
        {'source': '大学城', 'target': '市中心广场', 'value': 900},
        {'source': '商业区', 'target': '体育中心', 'value': 400},
        {'source': '工业园区', 'target': '火车站', 'value': 700}
    ]
    
    # 初始化转换器
    converter = SankeyConverter()
    
    # 转换为不同格式
    print("转换为Plotly格式...")
    plotly_format = converter.convert_to_plotly_format(sample_data)
    print(f"节点数量: {len(plotly_format['node']['label'])}")
    print(f"链接数量: {len(plotly_format['link']['source'])}")
    
    print("\n转换为D3格式...")
    d3_format = converter.convert_to_d3_format(sample_data)
    print(f"节点数量: {len(d3_format['nodes'])}")
    print(f"链接数量: {len(d3_format['links'])}")
    
    print("\n转换为ECharts格式...")
    echarts_format = converter.convert_to_echarts_format(sample_data)
    print(f"节点数量: {len(echarts_format['data'])}")
    print(f"链接数量: {len(echarts_format['links'])}")
    
    # 过滤数据
    print("\n过滤流量大于700的数据...")
    filtered_data = converter.filter_by_threshold(sample_data, min_value=700)
    print(f"过滤后数据量: {len(filtered_data)}")
    
    # 添加流向信息
    print("\n添加流向信息...")
    enhanced_data = converter.add_flow_direction_info(sample_data)
    for item in enhanced_data[:3]:
        print(f"{item['flow_description']} - 流量等级: {item['flow_level']}")
    
    # 导出多种格式
    print("\n导出多种格式文件...")
    exported_files = converter.export_multiple_formats(sample_data)
    for format_name, filename in exported_files.items():
        print(f"{format_name}格式已导出到: {filename}")
    
    print("\n桑基图转换演示完成！")


if __name__ == "__main__":
    main()