"""
城市交通流量数据分析模块

这个包提供了完整的城市交通流量数据处理和桑基图可视化功能。

主要组件:
- TrafficDataProcessor: 交通数据处理器
- SankeyConverter: 桑基图数据转换器

使用示例:
    from traffic_analysis import TrafficDataProcessor, SankeyConverter
    
    processor = TrafficDataProcessor()
    converter = SankeyConverter()
    
    # 处理数据
    results = processor.process_traffic_data()
    
    # 转换为桑基图格式
    sankey_data = converter.convert_to_plotly_format(results['sankey_data'])
"""

from .data_processor import TrafficDataProcessor
from .sankey_converter import SankeyConverter

__version__ = "1.0.0"
__author__ = "Traffic Analysis Team"
__email__ = "traffic@example.com"

__all__ = [
    'TrafficDataProcessor',
    'SankeyConverter'
]

# 模块级别的便捷函数
def quick_analysis(num_records=1000, top_n=15):
    """
    快速交通数据分析
    
    Args:
        num_records: 生成的数据记录数
        top_n: 保留的前N条流量最大的路线
        
    Returns:
        分析结果字典
    """
    processor = TrafficDataProcessor()
    converter = SankeyConverter()
    
    # 处理数据
    results = processor.process_traffic_data()
    
    # 过滤和转换数据
    filtered_data = converter.filter_by_threshold(
        results['sankey_data'], 
        min_value=100, 
        top_n=top_n
    )
    
    # 转换为多种格式
    plotly_data = converter.convert_to_plotly_format(filtered_data)
    
    return {
        'statistics': results['statistics'],
        'sankey_data': filtered_data,
        'plotly_data': plotly_data,
        'processor': processor,
        'converter': converter
    }


def create_sample_visualization(output_file='traffic_sankey.html'):
    """
    创建示例可视化文件
    
    Args:
        output_file: 输出HTML文件名
        
    Returns:
        生成的文件路径
    """
    import json
    
    # 快速分析
    results = quick_analysis()
    
    # HTML模板
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>城市交通流量桑基图</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .stats { background: #f0f0f0; padding: 15px; margin: 20px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>城市交通流量桑基图</h1>
        <div class="stats">
            <h3>数据统计:</h3>
            <p>总流量: {total_flow:,} 车次 | 平均速度: {avg_speed:.1f} km/h | 独特路线: {unique_routes}</p>
        </div>
        <div id="sankey-chart" style="width:100%;height:600px;"></div>
        <script>
            var data = [{sankey_data}];
            var layout = {{
                title: "城市交通流量分析",
                font: {{ size: 12 }},
                margin: {{ t: 50, r: 50, b: 50, l: 50 }}
            }};
            Plotly.newPlot('sankey-chart', data, layout);
        </script>
    </div>
</body>
</html>
    """
    
    # 生成HTML内容
    stats = results['statistics']
    html_content = html_template.format(
        total_flow=stats['total_flow'],
        avg_speed=stats['avg_speed'],
        unique_routes=stats['unique_routes'],
        sankey_data=json.dumps(results['plotly_data'])
    )
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_file