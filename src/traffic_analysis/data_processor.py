"""
城市交通流量数据处理器

这个模块提供了城市交通流量数据的处理和分析功能，
包括数据清洗、预处理和桑基图数据转换。
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import json


class TrafficDataProcessor:
    """交通数据处理器类"""
    
    def __init__(self):
        """初始化处理器"""
        self.processed_data = None
        self.raw_data = None
        
    def generate_sample_traffic_data(self, num_records: int = 1000) -> pd.DataFrame:
        """
        生成模拟的交通流量数据
        
        Args:
            num_records: 生成记录数量
            
        Returns:
            包含交通数据的DataFrame
        """
        np.random.seed(42)
        
        # 定义交通节点
        intersections = [
            "市中心广场", "火车站", "机场", "商业区", "住宅区A", 
            "住宅区B", "工业园区", "大学城", "医院", "体育中心"
        ]
        
        # 定义道路类型
        road_types = ["主干道", "次干道", "支路", "高速公路"]
        
        # 生成时间序列
        start_time = datetime.now() - timedelta(days=7)
        time_points = [start_time + timedelta(hours=i) for i in range(num_records)]
        
        data = []
        for i in range(num_records):
            # 随机选择起点和终点
            source = np.random.choice(intersections)
            target = np.random.choice([x for x in intersections if x != source])
            
            # 根据时间段调整流量（模拟早晚高峰）
            hour = time_points[i].hour
            if 7 <= hour <= 9 or 17 <= hour <= 19:  # 高峰期
                base_flow = np.random.normal(800, 200)
            elif 22 <= hour or hour <= 6:  # 夜间
                base_flow = np.random.normal(200, 50)
            else:  # 平峰期
                base_flow = np.random.normal(500, 100)
            
            flow = max(0, int(base_flow))
            
            record = {
                'timestamp': time_points[i],
                'source': source,
                'target': target,
                'flow_volume': flow,
                'road_type': np.random.choice(road_types),
                'average_speed': np.random.normal(35, 10),  # km/h
                'travel_time': np.random.normal(15, 5),     # minutes
                'congestion_level': np.random.choice(['低', '中', '高'], p=[0.4, 0.4, 0.2])
            }
            data.append(record)
        
        df = pd.DataFrame(data)
        df['average_speed'] = df['average_speed'].clip(lower=5, upper=80)
        df['travel_time'] = df['travel_time'].clip(lower=1, upper=60)
        
        return df
    
    def clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        清洗交通数据
        
        Args:
            data: 原始交通数据
            
        Returns:
            清洗后的数据
        """
        # 移除空值
        cleaned_data = data.dropna()
        
        # 移除异常值
        cleaned_data = cleaned_data[cleaned_data['flow_volume'] >= 0]
        cleaned_data = cleaned_data[cleaned_data['average_speed'] > 0]
        cleaned_data = cleaned_data[cleaned_data['travel_time'] > 0]
        
        # 标准化时间格式
        if 'timestamp' in cleaned_data.columns:
            cleaned_data['timestamp'] = pd.to_datetime(cleaned_data['timestamp'])
            cleaned_data['hour'] = cleaned_data['timestamp'].dt.hour
            cleaned_data['day_of_week'] = cleaned_data['timestamp'].dt.dayofweek
        
        return cleaned_data
    
    def aggregate_flow_data(self, data: pd.DataFrame, 
                           group_by: List[str] = ['source', 'target']) -> pd.DataFrame:
        """
        聚合流量数据
        
        Args:
            data: 交通数据
            group_by: 聚合字段
            
        Returns:
            聚合后的数据
        """
        agg_functions = {
            'flow_volume': ['sum', 'mean', 'count'],
            'average_speed': 'mean',
            'travel_time': 'mean'
        }
        
        aggregated = data.groupby(group_by).agg(agg_functions).reset_index()
        
        # 扁平化列名
        aggregated.columns = [
            '_'.join(col).strip('_') if col[1] else col[0] 
            for col in aggregated.columns.values
        ]
        
        return aggregated
    
    def convert_to_sankey_format(self, data: pd.DataFrame, 
                                source_col: str = 'source',
                                target_col: str = 'target', 
                                value_col: str = 'flow_volume_sum') -> List[Dict]:
        """
        将交通数据转换为桑基图格式
        
        Args:
            data: 聚合后的交通数据
            source_col: 源节点列名
            target_col: 目标节点列名
            value_col: 流量值列名
            
        Returns:
            桑基图数据格式的列表
        """
        sankey_data = []
        
        for _, row in data.iterrows():
            if pd.notna(row[source_col]) and pd.notna(row[target_col]) and row[value_col] > 0:
                sankey_record = {
                    'source': str(row[source_col]),
                    'target': str(row[target_col]),
                    'value': int(row[value_col])
                }
                sankey_data.append(sankey_record)
        
        # 按流量值排序
        sankey_data.sort(key=lambda x: x['value'], reverse=True)
        
        return sankey_data
    
    def process_traffic_data(self, raw_data: Optional[pd.DataFrame] = None) -> Dict:
        """
        完整的交通数据处理流程
        
        Args:
            raw_data: 原始数据，如果为None则生成示例数据
            
        Returns:
            包含处理结果的字典
        """
        # 获取或生成数据
        if raw_data is None:
            print("生成示例交通数据...")
            raw_data = self.generate_sample_traffic_data()
        
        self.raw_data = raw_data
        print(f"原始数据记录数: {len(raw_data)}")
        
        # 数据清洗
        print("清洗数据...")
        cleaned_data = self.clean_data(raw_data)
        print(f"清洗后数据记录数: {len(cleaned_data)}")
        
        # 数据聚合
        print("聚合流量数据...")
        aggregated_data = self.aggregate_flow_data(cleaned_data)
        print(f"聚合后数据记录数: {len(aggregated_data)}")
        
        # 转换为桑基图格式
        print("转换为桑基图格式...")
        sankey_data = self.convert_to_sankey_format(aggregated_data)
        print(f"桑基图数据记录数: {len(sankey_data)}")
        
        # 生成统计信息
        stats = {
            'total_flow': aggregated_data['flow_volume_sum'].sum(),
            'avg_speed': cleaned_data['average_speed'].mean(),
            'avg_travel_time': cleaned_data['travel_time'].mean(),
            'peak_flow': aggregated_data['flow_volume_sum'].max(),
            'unique_routes': len(aggregated_data),
            'unique_intersections': len(set(cleaned_data['source'].tolist() + 
                                         cleaned_data['target'].tolist()))
        }
        
        self.processed_data = {
            'raw_data': raw_data,
            'cleaned_data': cleaned_data,
            'aggregated_data': aggregated_data,
            'sankey_data': sankey_data,
            'statistics': stats
        }
        
        return self.processed_data
    
    def get_top_routes(self, n: int = 10) -> List[Dict]:
        """
        获取流量最大的前N条路线
        
        Args:
            n: 返回的路线数量
            
        Returns:
            前N条路线的列表
        """
        if self.processed_data is None:
            raise ValueError("请先运行 process_traffic_data() 方法")
        
        sankey_data = self.processed_data['sankey_data']
        return sankey_data[:n]
    
    def export_sankey_data(self, filename: str = 'traffic_sankey_data.json'):
        """
        导出桑基图数据到JSON文件
        
        Args:
            filename: 输出文件名
        """
        if self.processed_data is None:
            raise ValueError("请先运行 process_traffic_data() 方法")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.processed_data['sankey_data'], f, 
                     ensure_ascii=False, indent=2)
        
        print(f"桑基图数据已导出到: {filename}")


def main():
    """主函数 - 演示数据处理流程"""
    print("=== 城市交通流量数据分析演示 ===\n")
    
    # 初始化处理器
    processor = TrafficDataProcessor()
    
    # 处理数据
    results = processor.process_traffic_data()
    
    # 显示统计信息
    print("\n=== 数据统计 ===")
    stats = results['statistics']
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    
    # 显示前10条流量最大的路线
    print("\n=== 流量最大的前10条路线 ===")
    top_routes = processor.get_top_routes(10)
    for i, route in enumerate(top_routes, 1):
        print(f"{i}. {route['source']} → {route['target']}: {route['value']} 车次")
    
    # 导出数据
    processor.export_sankey_data()
    
    print("\n数据处理完成！")
    return results


if __name__ == "__main__":
    main()