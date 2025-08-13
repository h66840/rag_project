"""
城市交通流量数据分析完整示例

这个脚本演示了如何使用交通数据处理器和桑基图转换器
来分析城市交通流量数据并生成可视化图表。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processor import TrafficDataProcessor
from sankey_converter import SankeyConverter
import json


def run_complete_analysis():
    """运行完整的交通数据分析流程"""
    
    print("=" * 60)
    print("城市交通流量数据分析完整示例")
    print("=" * 60)
    
    # 步骤1: 初始化处理器
    print("\n步骤1: 初始化数据处理器和转换器")
    processor = TrafficDataProcessor()
    converter = SankeyConverter()
    
    # 步骤2: 生成和处理数据
    print("\n步骤2: 生成模拟交通数据并进行处理")
    results = processor.process_traffic_data()
    
    # 显示处理结果统计
    print("\n数据处理统计:")
    stats = results['statistics']
    print(f"  总流量: {stats['total_flow']:,} 车次")
    print(f"  平均速度: {stats['avg_speed']:.1f} km/h")
    print(f"  平均行程时间: {stats['avg_travel_time']:.1f} 分钟")
    print(f"  峰值流量: {stats['peak_flow']:,} 车次")
    print(f"  独特路线数: {stats['unique_routes']}")
    print(f"  交叉口数量: {stats['unique_intersections']}")
    
    # 步骤3: 获取桑基图数据
    print("\n步骤3: 准备桑基图数据")
    sankey_data = results['sankey_data']
    
    # 过滤数据 - 只保留流量较大的路线
    filtered_data = converter.filter_by_threshold(sankey_data, min_value=100, top_n=15)
    print(f"  原始数据: {len(sankey_data)} 条路线")
    print(f"  过滤后数据: {len(filtered_data)} 条路线")
    
    # 步骤4: 转换为不同格式
    print("\n步骤4: 转换为多种桑基图格式")
    
    # 转换为Plotly格式
    plotly_data = converter.convert_to_plotly_format(filtered_data)
    print(f"  Plotly格式 - 节点: {len(plotly_data['node']['label'])}, 链接: {len(plotly_data['link']['source'])}")
    
    # 转换为D3格式
    d3_data = converter.convert_to_d3_format(filtered_data)
    print(f"  D3格式 - 节点: {len(d3_data['nodes'])}, 链接: {len(d3_data['links'])}")
    
    # 转换为ECharts格式
    echarts_data = converter.convert_to_echarts_format(filtered_data)
    print(f"  ECharts格式 - 节点: {len(echarts_data['data'])}, 链接: {len(echarts_data['links'])}")
    
    # 步骤5: 添加增强信息
    print("\n步骤5: 添加流向分析信息")
    enhanced_data = converter.add_flow_direction_info(filtered_data)
    
    # 分析流量等级分布
    flow_levels = {}
    for item in enhanced_data:
        level = item['flow_level']
        flow_levels[level] = flow_levels.get(level, 0) + 1
    
    print("  流量等级分布:")
    for level, count in flow_levels.items():
        print(f"    {level}流量路线: {count} 条")
    
    # 步骤6: 显示主要交通流向
    print("\n步骤6: 主要交通流向分析")
    top_routes = sorted(filtered_data, key=lambda x: x['value'], reverse=True)[:10]
    
    print("  流量最大的10条路线:")
    for i, route in enumerate(top_routes, 1):
        print(f"    {i:2d}. {route['source']} → {route['target']}: {route['value']:,} 车次")
    
    # 步骤7: 导出数据文件
    print("\n步骤7: 导出数据文件")
    
    # 导出原始桑基图数据
    with open('traffic_sankey_raw.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False, indent=2)
    print("  原始桑基图数据已导出: traffic_sankey_raw.json")
    
    # 导出多种格式
    exported_files = converter.export_multiple_formats(filtered_data, 'traffic_flow')
    for format_name, filename in exported_files.items():
        print(f"  {format_name.upper()}格式已导出: {filename}")
    
    # 步骤8: 生成配置文件
    print("\n步骤8: 生成可视化配置")
    config = converter.generate_sankey_config(
        title="城市交通流量桑基图",
        width=1000,
        height=700
    )
    
    with open('sankey_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print("  可视化配置已导出: sankey_config.json")
    
    # 步骤9: 生成HTML可视化文件
    print("\n步骤9: 生成HTML可视化文件")
    generate_html_visualization(plotly_data, config)
    print("  HTML可视化文件已生成: traffic_sankey_visualization.html")
    
    print("\n" + "=" * 60)
    print("分析完成！生成的文件:")
    print("  - traffic_sankey_raw.json: 原始桑基图数据")
    print("  - traffic_flow_plotly.json: Plotly格式数据")
    print("  - traffic_flow_d3.json: D3格式数据") 
    print("  - traffic_flow_echarts.json: ECharts格式数据")
    print("  - sankey_config.json: 可视化配置")
    print("  - traffic_sankey_visualization.html: HTML可视化")
    print("=" * 60)
    
    return {
        'raw_data': filtered_data,
        'plotly_data': plotly_data,
        'd3_data': d3_data,
        'echarts_data': echarts_data,
        'config': config,
        'statistics': stats
    }


def generate_html_visualization(plotly_data, config):
    """生成HTML可视化文件"""
    
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .chart-container {{
            width: 100%;
            height: 700px;
            margin: 20px 0;
        }}
        .info {{
            background-color: #e8f4fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{title}</h1>
            <p>城市交通流量数据桑基图可视化</p>
        </div>
        
        <div class="info">
            <h3>图表说明:</h3>
            <ul>
                <li>节点代表城市中的不同区域或交通枢纽</li>
                <li>连接线的粗细表示交通流量的大小</li>
                <li>颜色用于区分不同的交通流向</li>
                <li>鼠标悬停可查看详细数据</li>
            </ul>
        </div>
        
        <div id="sankey-chart" class="chart-container"></div>
        
        <script>
            var data = [{sankey_data}];
            
            var layout = {{
                title: {{
                    text: "{title}",
                    font: {{ size: 20 }}
                }},
                width: {width},
                height: {height},
                font: {{ size: 12 }},
                margin: {{ t: 50, r: 50, b: 50, l: 50 }}
            }};
            
            var config = {{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            }};
            
            Plotly.newPlot('sankey-chart', data, layout, config);
        </script>
    </div>
</body>
</html>
    """
    
    html_content = html_template.format(
        title=config['title'],
        sankey_data=json.dumps(plotly_data),
        width=config['width'],
        height=config['height']
    )
    
    with open('traffic_sankey_visualization.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


def analyze_traffic_patterns(data):
    """分析交通模式"""
    print("\n交通模式分析:")
    
    # 分析最繁忙的起点
    source_flows = {}
    target_flows = {}
    
    for item in data:
        source = item['source']
        target = item['target']
        value = item['value']
        
        source_flows[source] = source_flows.get(source, 0) + value
        target_flows[target] = target_flows.get(target, 0) + value
    
    # 最繁忙的起点
    top_sources = sorted(source_flows.items(), key=lambda x: x[1], reverse=True)[:5]
    print("  最繁忙的起点:")
    for i, (source, flow) in enumerate(top_sources, 1):
        print(f"    {i}. {source}: {flow:,} 车次")
    
    # 最繁忙的终点
    top_targets = sorted(target_flows.items(), key=lambda x: x[1], reverse=True)[:5]
    print("  最繁忙的终点:")
    for i, (target, flow) in enumerate(top_targets, 1):
        print(f"    {i}. {target}: {flow:,} 车次")


if __name__ == "__main__":
    # 运行完整分析
    results = run_complete_analysis()
    
    # 额外的交通模式分析
    analyze_traffic_patterns(results['raw_data'])
    
    print("\n示例运行完成！请查看生成的文件。")