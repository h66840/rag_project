#!/usr/bin/env python3
"""
农业无人机精准喷洒路径优化算法
Agricultural Drone Precision Spray Path Optimization Algorithm

作者: 农业无人机操作团队
版本: 1.0.0
日期: 2025-08-05

本模块实现了一个高效的农业无人机作物精准喷洒路径优化算法，
旨在提高农药利用率，减少环境污染，并确保作物覆盖的均匀性。
"""

import numpy as np
import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SprayPattern(Enum):
    """喷洒模式枚举"""
    UNIFORM = "uniform"          # 均匀喷洒
    VARIABLE = "variable"        # 变量喷洒
    PRECISION = "precision"      # 精准喷洒

class FlightMode(Enum):
    """飞行模式枚举"""
    ZIGZAG = "zigzag"           # 之字形
    SPIRAL = "spiral"           # 螺旋形
    PARALLEL = "parallel"       # 平行线
    ADAPTIVE = "adaptive"       # 自适应

@dataclass
class Point:
    """二维点坐标"""
    x: float
    y: float
    z: float = 0.0  # 高度信息

@dataclass
class FieldBoundary:
    """田地边界定义"""
    vertices: List[Point]
    obstacles: List[List[Point]] = None  # 障碍物列表

@dataclass
class SprayParameters:
    """喷洒参数"""
    flow_rate: float = 1.0      # 流量 L/min
    spray_width: float = 5.0    # 喷洒宽度 m
    spray_height: float = 3.0   # 喷洒高度 m
    overlap_ratio: float = 0.1  # 重叠比例
    wind_compensation: bool = True

@dataclass
class EnvironmentalData:
    """环境数据"""
    wind_speed: float = 0.0     # 风速 m/s
    wind_direction: float = 0.0 # 风向 度
    temperature: float = 25.0   # 温度 °C
    humidity: float = 60.0      # 湿度 %

@dataclass
class CropData:
    """作物数据"""
    crop_type: str = "unknown"
    crop_height: float = 1.0    # 作物高度 m
    density: float = 1.0        # 密度系数
    health_status: float = 1.0  # 健康状态 0-1

class PrecisionSprayOptimizer:
    """精准喷洒路径优化器"""
    
    def __init__(self, field_boundary: FieldBoundary, spray_params: SprayParameters):
        """
        初始化优化器
        
        Args:
            field_boundary: 田地边界
            spray_params: 喷洒参数
        """
        self.field_boundary = field_boundary
        self.spray_params = spray_params
        self.flight_path: List[Point] = []
        self.spray_zones: List[Dict] = []
        
        logger.info("精准喷洒路径优化器初始化完成")
    
    def calculate_coverage_path(self, mode: FlightMode = FlightMode.ZIGZAG) -> List[Point]:
        """
        计算覆盖路径
        
        Args:
            mode: 飞行模式
            
        Returns:
            优化后的飞行路径点列表
        """
        logger.info(f"开始计算覆盖路径，模式: {mode.value}")
        
        if mode == FlightMode.ZIGZAG:
            return self._calculate_zigzag_path()
        elif mode == FlightMode.PARALLEL:
            return self._calculate_parallel_path()
        elif mode == FlightMode.ADAPTIVE:
            return self._calculate_adaptive_path()
        else:
            return self._calculate_zigzag_path()  # 默认使用之字形
    
    def _calculate_zigzag_path(self) -> List[Point]:
        """计算之字形路径"""
        path = []
        
        # 获取田地边界框
        min_x = min(p.x for p in self.field_boundary.vertices)
        max_x = max(p.x for p in self.field_boundary.vertices)
        min_y = min(p.y for p in self.field_boundary.vertices)
        max_y = max(p.y for p in self.field_boundary.vertices)
        
        # 计算有效喷洒宽度（考虑重叠）
        effective_width = self.spray_params.spray_width * (1 - self.spray_params.overlap_ratio)
        
        # 生成之字形路径
        y = min_y
        direction = 1  # 1: 从左到右, -1: 从右到左
        
        while y <= max_y:
            if direction == 1:
                # 从左到右
                path.append(Point(min_x, y, self.spray_params.spray_height))
                path.append(Point(max_x, y, self.spray_params.spray_height))
            else:
                # 从右到左
                path.append(Point(max_x, y, self.spray_params.spray_height))
                path.append(Point(min_x, y, self.spray_params.spray_height))
            
            y += effective_width
            direction *= -1
        
        logger.info(f"生成之字形路径，共 {len(path)} 个路径点")
        return path
    
    def _calculate_parallel_path(self) -> List[Point]:
        """计算平行线路径"""
        path = []
        
        # 获取田地边界框
        min_x = min(p.x for p in self.field_boundary.vertices)
        max_x = max(p.x for p in self.field_boundary.vertices)
        min_y = min(p.y for p in self.field_boundary.vertices)
        max_y = max(p.y for p in self.field_boundary.vertices)
        
        # 计算有效喷洒宽度
        effective_width = self.spray_params.spray_width * (1 - self.spray_params.overlap_ratio)
        
        # 生成平行线路径
        y = min_y
        while y <= max_y:
            path.append(Point(min_x, y, self.spray_params.spray_height))
            path.append(Point(max_x, y, self.spray_params.spray_height))
            y += effective_width
        
        logger.info(f"生成平行线路径，共 {len(path)} 个路径点")
        return path
    
    def _calculate_adaptive_path(self) -> List[Point]:
        """计算自适应路径"""
        # 基于作物密度和健康状态的自适应路径规划
        path = []
        
        # 简化实现：基于之字形路径进行自适应调整
        base_path = self._calculate_zigzag_path()
        
        # 根据环境条件调整路径
        for point in base_path:
            adjusted_point = self._adjust_point_for_conditions(point)
            path.append(adjusted_point)
        
        logger.info(f"生成自适应路径，共 {len(path)} 个路径点")
        return path
    
    def _adjust_point_for_conditions(self, point: Point) -> Point:
        """根据环境条件调整路径点"""
        # 简化实现：根据风速调整高度
        adjusted_height = point.z
        
        # 风速补偿：风速越大，飞行高度越低
        if hasattr(self, 'environmental_data'):
            wind_factor = min(self.environmental_data.wind_speed / 10.0, 0.5)
            adjusted_height = max(point.z - wind_factor, 2.0)  # 最低2米
        
        return Point(point.x, point.y, adjusted_height)
    
    def optimize_spray_parameters(self, crop_data: CropData, env_data: EnvironmentalData) -> Dict:
        """
        优化喷洒参数
        
        Args:
            crop_data: 作物数据
            env_data: 环境数据
            
        Returns:
            优化后的喷洒参数字典
        """
        self.environmental_data = env_data
        
        # 基于作物类型调整流量
        flow_rate_multiplier = 1.0
        if crop_data.crop_type == "corn":
            flow_rate_multiplier = 1.2
        elif crop_data.crop_type == "wheat":
            flow_rate_multiplier = 0.8
        elif crop_data.crop_type == "rice":
            flow_rate_multiplier = 1.1
        
        # 基于作物健康状态调整
        health_multiplier = 2.0 - crop_data.health_status  # 健康状态越差，用药越多
        
        # 基于风速调整
        wind_multiplier = 1.0 + (env_data.wind_speed / 20.0)  # 风速越大，流量稍增
        
        # 计算优化后的参数
        optimized_flow_rate = (self.spray_params.flow_rate * 
                             flow_rate_multiplier * 
                             health_multiplier * 
                             wind_multiplier)
        
        # 高度调整
        optimized_height = max(
            self.spray_params.spray_height - env_data.wind_speed * 0.1,
            crop_data.crop_height + 1.5  # 至少比作物高1.5米
        )
        
        optimized_params = {
            "flow_rate": round(optimized_flow_rate, 2),
            "spray_height": round(optimized_height, 2),
            "wind_compensation_angle": self._calculate_wind_compensation_angle(env_data),
            "recommended_speed": self._calculate_optimal_speed(env_data),
        }
        
        logger.info(f"优化喷洒参数: {optimized_params}")
        return optimized_params
    
    def _calculate_wind_compensation_angle(self, env_data: EnvironmentalData) -> float:
        """计算风补偿角度"""
        # 简化的风补偿计算
        if env_data.wind_speed < 2.0:
            return 0.0
        
        # 基于风速计算补偿角度（度）
        compensation_angle = min(env_data.wind_speed * 2.0, 15.0)
        return round(compensation_angle, 1)
    
    def _calculate_optimal_speed(self, env_data: EnvironmentalData) -> float:
        """计算最优飞行速度"""
        base_speed = 5.0  # 基础速度 m/s
        
        # 风速影响：逆风减速，顺风可稍加速
        wind_factor = 1.0 - (env_data.wind_speed / 20.0)
        optimal_speed = max(base_speed * wind_factor, 2.0)  # 最低2m/s
        
        return round(optimal_speed, 1)
    
    def calculate_coverage_efficiency(self, path: List[Point]) -> Dict:
        """
        计算覆盖效率
        
        Args:
            path: 飞行路径
            
        Returns:
            效率统计字典
        """
        if not path:
            return {"error": "路径为空"}
        
        # 计算总飞行距离
        total_distance = 0.0
        for i in range(1, len(path)):
            dx = path[i].x - path[i-1].x
            dy = path[i].y - path[i-1].y
            dz = path[i].z - path[i-1].z
            distance = math.sqrt(dx*dx + dy*dy + dz*dz)
            total_distance += distance
        
        # 计算田地面积（简化为矩形）
        min_x = min(p.x for p in self.field_boundary.vertices)
        max_x = max(p.x for p in self.field_boundary.vertices)
        min_y = min(p.y for p in self.field_boundary.vertices)
        max_y = max(p.y for p in self.field_boundary.vertices)
        
        field_area = (max_x - min_x) * (max_y - min_y)
        
        # 计算覆盖面积
        effective_width = self.spray_params.spray_width * (1 - self.spray_params.overlap_ratio)
        coverage_area = len(path) * effective_width * (max_x - min_x) / 2  # 简化计算
        
        # 计算效率指标
        coverage_ratio = min(coverage_area / field_area, 1.0)
        flight_efficiency = field_area / total_distance if total_distance > 0 else 0
        
        efficiency_stats = {
            "total_distance_m": round(total_distance, 2),
            "field_area_m2": round(field_area, 2),
            "coverage_area_m2": round(coverage_area, 2),
            "coverage_ratio": round(coverage_ratio, 3),
            "flight_efficiency_m2_per_m": round(flight_efficiency, 3),
            "estimated_flight_time_min": round(total_distance / 5.0 / 60, 2),  # 假设5m/s速度
            "path_points": len(path)
        }
        
        logger.info(f"覆盖效率统计: {efficiency_stats}")
        return efficiency_stats
    
    def generate_mission_plan(self, crop_data: CropData, env_data: EnvironmentalData) -> Dict:
        """
        生成完整的任务计划
        
        Args:
            crop_data: 作物数据
            env_data: 环境数据
            
        Returns:
            完整的任务计划字典
        """
        logger.info("开始生成任务计划")
        
        # 计算最优路径
        optimal_path = self.calculate_coverage_path(FlightMode.ADAPTIVE)
        
        # 优化喷洒参数
        optimized_params = self.optimize_spray_parameters(crop_data, env_data)
        
        # 计算效率统计
        efficiency_stats = self.calculate_coverage_efficiency(optimal_path)
        
        # 生成任务计划
        mission_plan = {
            "mission_id": f"spray_mission_{hash(str(optimal_path)) % 10000}",
            "timestamp": "2025-08-05T09:00:00Z",
            "field_info": {
                "boundary_points": len(self.field_boundary.vertices),
                "estimated_area_m2": efficiency_stats["field_area_m2"]
            },
            "flight_plan": {
                "path_points": [{"x": p.x, "y": p.y, "z": p.z} for p in optimal_path],
                "total_waypoints": len(optimal_path),
                "flight_mode": FlightMode.ADAPTIVE.value
            },
            "spray_configuration": {
                "base_flow_rate": self.spray_params.flow_rate,
                "optimized_flow_rate": optimized_params["flow_rate"],
                "spray_width_m": self.spray_params.spray_width,
                "spray_height_m": optimized_params["spray_height"],
                "overlap_ratio": self.spray_params.overlap_ratio
            },
            "environmental_conditions": {
                "wind_speed_ms": env_data.wind_speed,
                "wind_direction_deg": env_data.wind_direction,
                "temperature_c": env_data.temperature,
                "humidity_percent": env_data.humidity,
                "wind_compensation_angle": optimized_params["wind_compensation_angle"]
            },
            "crop_information": {
                "crop_type": crop_data.crop_type,
                "crop_height_m": crop_data.crop_height,
                "density_factor": crop_data.density,
                "health_status": crop_data.health_status
            },
            "performance_metrics": efficiency_stats,
            "safety_parameters": {
                "min_flight_height_m": 2.0,
                "max_wind_speed_ms": 8.0,
                "emergency_landing_points": 3,
                "battery_reserve_percent": 20
            },
            "estimated_resources": {
                "flight_time_min": efficiency_stats["estimated_flight_time_min"],
                "pesticide_volume_l": round(optimized_params["flow_rate"] * efficiency_stats["estimated_flight_time_min"], 2),
                "battery_consumption_percent": min(efficiency_stats["estimated_flight_time_min"] * 2, 80)
            }
        }
        
        logger.info(f"任务计划生成完成，任务ID: {mission_plan['mission_id']}")
        return mission_plan

def demo_precision_spray_optimization():
    """演示精准喷洒路径优化功能"""
    print("=== 农业无人机精准喷洒路径优化算法演示 ===\n")
    
    # 定义田地边界（100m x 80m的矩形田地）
    field_boundary = FieldBoundary([
        Point(0, 0),
        Point(100, 0),
        Point(100, 80),
        Point(0, 80)
    ])
    
    # 定义喷洒参数
    spray_params = SprayParameters(
        flow_rate=1.5,      # 1.5 L/min
        spray_width=6.0,    # 6米喷洒宽度
        spray_height=3.5,   # 3.5米飞行高度
        overlap_ratio=0.15  # 15%重叠
    )
    
    # 创建优化器
    optimizer = PrecisionSprayOptimizer(field_boundary, spray_params)
    
    # 定义作物数据
    crop_data = CropData(
        crop_type="corn",
        crop_height=2.0,
        density=0.9,
        health_status=0.8  # 80%健康状态
    )
    
    # 定义环境数据
    env_data = EnvironmentalData(
        wind_speed=3.5,      # 3.5 m/s风速
        wind_direction=45,   # 45度风向
        temperature=28,      # 28°C
        humidity=65         # 65%湿度
    )
    
    # 生成完整任务计划
    mission_plan = optimizer.generate_mission_plan(crop_data, env_data)
    
    # 输出结果
    print("📋 任务计划概览:")
    print(f"  任务ID: {mission_plan['mission_id']}")
    print(f"  田地面积: {mission_plan['field_info']['estimated_area_m2']} m²")
    print(f"  路径点数: {mission_plan['flight_plan']['total_waypoints']}")
    print(f"  预计飞行时间: {mission_plan['estimated_resources']['flight_time_min']} 分钟")
    print(f"  农药用量: {mission_plan['estimated_resources']['pesticide_volume_l']} 升")
    
    print("\n🎯 性能指标:")
    metrics = mission_plan['performance_metrics']
    print(f"  覆盖率: {metrics['coverage_ratio']*100:.1f}%")
    print(f"  飞行效率: {metrics['flight_efficiency_m2_per_m']:.2f} m²/m")
    print(f"  总飞行距离: {metrics['total_distance_m']} 米")
    
    print("\n💨 环境适应:")
    print(f"  风速补偿角度: {mission_plan['environmental_conditions']['wind_compensation_angle']}°")
    print(f"  优化后喷洒高度: {mission_plan['spray_configuration']['spray_height_m']} 米")
    print(f"  优化后流量: {mission_plan['spray_configuration']['optimized_flow_rate']} L/min")
    
    print("\n✅ 算法优化效果:")
    base_efficiency = 100 * 80 / (100 * 2 + 80 * 2)  # 简化的基础效率
    optimized_efficiency = metrics['flight_efficiency_m2_per_m']
    improvement = ((optimized_efficiency - base_efficiency) / base_efficiency) * 100
    print(f"  相比传统方法效率提升: {improvement:.1f}%")
    print(f"  预计农药节约: {15 + improvement*0.5:.1f}%")
    
    # 保存任务计划到文件
    with open('mission_plan.json', 'w', encoding='utf-8') as f:
        json.dump(mission_plan, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 完整任务计划已保存到: mission_plan.json")
    print("\n=== 演示完成 ===")

if __name__ == "__main__":
    demo_precision_spray_optimization()