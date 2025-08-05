# 城市交通流量数据分析模块

这个模块提供了城市交通流量数据的处理和分析功能。

## 功能模块

- `data_processor.py`: 核心数据处理脚本
- `sankey_converter.py`: 桑基图数据转换器
- `examples/`: 示例数据和脚本

## 主要功能

### 数据处理
- 交通流量数据清洗和预处理
- 多种数据源的整合和标准化
- 时间序列数据的聚合和分析

### 桑基图转换
- 将交通流量数据转换为桑基图所需的格式
- 支持多层级的交通流向分析
- 自动生成源-目标-流量的数据结构

### 可视化支持
- 生成适用于各种可视化工具的数据格式
- 支持动态数据更新和实时分析

## 使用示例

```python
from traffic_analysis.data_processor import TrafficDataProcessor
from traffic_analysis.sankey_converter import SankeyConverter

# 初始化处理器
processor = TrafficDataProcessor()
converter = SankeyConverter()

# 处理数据并转换为桑基图格式
processed_data = processor.process_traffic_data(raw_data)
sankey_data = converter.convert_to_sankey(processed_data)
```