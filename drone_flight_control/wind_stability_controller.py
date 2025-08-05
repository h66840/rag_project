"""
无人机高风速环境飞行稳定性控制器
High Wind Speed Flight Stability Controller for Drones

此模块实现了在高风速环境下的无人机飞行稳定性控制算法
包含风速估计、姿态补偿和动态PID调节功能
"""

import numpy as np
import math
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class WindCondition(Enum):
    """风况等级枚举"""
    CALM = "calm"           # 0-5 m/s
    LIGHT = "light"         # 5-10 m/s  
    MODERATE = "moderate"   # 10-15 m/s
    STRONG = "strong"       # 15-20 m/s
    SEVERE = "severe"       # >20 m/s

@dataclass
class DroneState:
    """无人机状态数据结构"""
    position: Tuple[float, float, float]  # x, y, z coordinates
    velocity: Tuple[float, float, float]  # vx, vy, vz
    attitude: Tuple[float, float, float]  # roll, pitch, yaw (radians)
    angular_velocity: Tuple[float, float, float]  # wx, wy, wz
    timestamp: float

@dataclass
class WindEstimate:
    """风速估计数据结构"""
    velocity: Tuple[float, float, float]  # 风速向量 (m/s)
    magnitude: float                      # 风速大小 (m/s)
    direction: float                      # 风向 (radians)
    condition: WindCondition              # 风况等级
    confidence: float                     # 估计置信度 [0-1]

class WindStabilityController:
    """高风速环境下的无人机稳定性控制器"""
    
    def __init__(self, max_wind_speed: float = 25.0):
        """
        初始化控制器
        
        Args:
            max_wind_speed: 最大可操作风速 (m/s)
        """
        self.max_wind_speed = max_wind_speed
        
        # PID控制器参数 - 基础值
        self.base_pid_params = {
            'position': {'kp': 1.2, 'ki': 0.1, 'kd': 0.8},
            'attitude': {'kp': 2.5, 'ki': 0.2, 'kd': 1.5},
            'velocity': {'kp': 0.8, 'ki': 0.05, 'kd': 0.6}
        }
        
        # 风速自适应增益系数
        self.wind_gain_factors = {
            WindCondition.CALM: 1.0,
            WindCondition.LIGHT: 1.2,
            WindCondition.MODERATE: 1.5,
            WindCondition.STRONG: 2.0,
            WindCondition.SEVERE: 2.8
        }
        
        # 历史数据缓存
        self.state_history = []
        self.wind_history = []
        self.max_history_length = 50
        
        # 控制器状态
        self.last_error = {'position': np.zeros(3), 'attitude': np.zeros(3)}
        self.integral_error = {'position': np.zeros(3), 'attitude': np.zeros(3)}
        
    def estimate_wind_conditions(self, drone_state: DroneState, 
                                control_input: np.ndarray) -> WindEstimate:
        """
        估计当前风况条件
        
        Args:
            drone_state: 当前无人机状态
            control_input: 当前控制输入
            
        Returns:
            WindEstimate: 风况估计结果
        """
        # 基于无人机状态和控制输入估计风速
        # 这里使用简化的风速估计算法
        
        # 计算期望加速度与实际加速度的差异
        if len(self.state_history) >= 2:
            dt = drone_state.timestamp - self.state_history[-1].timestamp
            if dt > 0:
                # 计算实际加速度
                actual_accel = np.array([
                    (drone_state.velocity[i] - self.state_history[-1].velocity[i]) / dt
                    for i in range(3)
                ])
                
                # 估计风扰动（简化模型）
                wind_disturbance = actual_accel - control_input[:3] * 0.1
                
                # 计算风速大小和方向
                wind_magnitude = np.linalg.norm(wind_disturbance[:2])  # 忽略垂直分量
                wind_direction = math.atan2(wind_disturbance[1], wind_disturbance[0])
                
                # 确定风况等级
                if wind_magnitude < 5.0:
                    condition = WindCondition.CALM
                elif wind_magnitude < 10.0:
                    condition = WindCondition.LIGHT
                elif wind_magnitude < 15.0:
                    condition = WindCondition.MODERATE
                elif wind_magnitude < 20.0:
                    condition = WindCondition.STRONG
                else:
                    condition = WindCondition.SEVERE
                
                # 计算置信度（基于历史数据一致性）
                confidence = min(1.0, len(self.wind_history) / 10.0)
                
                return WindEstimate(
                    velocity=(wind_disturbance[0], wind_disturbance[1], wind_disturbance[2]),
                    magnitude=wind_magnitude,
                    direction=wind_direction,
                    condition=condition,
                    confidence=confidence
                )
        
        # 默认返回无风状态
        return WindEstimate(
            velocity=(0.0, 0.0, 0.0),
            magnitude=0.0,
            direction=0.0,
            condition=WindCondition.CALM,
            confidence=0.0
        )
    
    def adaptive_pid_gains(self, wind_estimate: WindEstimate) -> Dict[str, Dict[str, float]]:
        """
        根据风况自适应调整PID参数
        
        Args:
            wind_estimate: 风况估计
            
        Returns:
            Dict: 调整后的PID参数
        """
        gain_factor = self.wind_gain_factors[wind_estimate.condition]
        
        # 根据风况调整PID参数
        adaptive_params = {}
        for controller_type, base_params in self.base_pid_params.items():
            adaptive_params[controller_type] = {}
            for param_name, base_value in base_params.items():
                if param_name == 'kp':
                    # 比例增益随风速增加
                    adaptive_params[controller_type][param_name] = base_value * gain_factor
                elif param_name == 'ki':
                    # 积分增益适度增加以消除稳态误差
                    adaptive_params[controller_type][param_name] = base_value * (1 + 0.3 * (gain_factor - 1))
                elif param_name == 'kd':
                    # 微分增益显著增加以提高响应速度
                    adaptive_params[controller_type][param_name] = base_value * gain_factor * 1.2
        
        return adaptive_params
    
    def wind_compensation_control(self, drone_state: DroneState, 
                                 target_position: Tuple[float, float, float],
                                 target_attitude: Tuple[float, float, float],
                                 wind_estimate: WindEstimate) -> np.ndarray:
        """
        计算带风补偿的控制输出
        
        Args:
            drone_state: 当前无人机状态
            target_position: 目标位置
            target_attitude: 目标姿态
            wind_estimate: 风况估计
            
        Returns:
            np.ndarray: 控制输出 [thrust, roll_cmd, pitch_cmd, yaw_cmd]
        """
        # 获取自适应PID参数
        pid_params = self.adaptive_pid_gains(wind_estimate)
        
        # 位置控制
        position_error = np.array(target_position) - np.array(drone_state.position)
        
        # 风补偿 - 前馈控制
        wind_compensation = np.array(wind_estimate.velocity) * 0.5  # 补偿系数
        
        # PID位置控制
        position_p = pid_params['position']['kp'] * position_error
        self.integral_error['position'] += position_error * 0.01  # 假设dt=0.01s
        position_i = pid_params['position']['ki'] * self.integral_error['position']
        position_d = pid_params['position']['kd'] * (position_error - self.last_error['position']) / 0.01
        
        position_control = position_p + position_i + position_d + wind_compensation
        
        # 姿态控制
        attitude_error = np.array(target_attitude) - np.array(drone_state.attitude)
        
        # 处理角度环绕问题
        for i in range(3):
            while attitude_error[i] > math.pi:
                attitude_error[i] -= 2 * math.pi
            while attitude_error[i] < -math.pi:
                attitude_error[i] += 2 * math.pi
        
        # PID姿态控制
        attitude_p = pid_params['attitude']['kp'] * attitude_error
        self.integral_error['attitude'] += attitude_error * 0.01
        attitude_i = pid_params['attitude']['ki'] * self.integral_error['attitude']
        attitude_d = pid_params['attitude']['kd'] * (attitude_error - self.last_error['attitude']) / 0.01
        
        attitude_control = attitude_p + attitude_i + attitude_d
        
        # 更新历史误差
        self.last_error['position'] = position_error.copy()
        self.last_error['attitude'] = attitude_error.copy()
        
        # 组合控制输出
        # [推力, 横滚指令, 俯仰指令, 偏航指令]
        thrust = max(0.1, min(1.0, 0.5 + position_control[2]))  # 垂直推力
        roll_cmd = np.clip(attitude_control[0], -0.5, 0.5)      # 横滚角度指令
        pitch_cmd = np.clip(attitude_control[1], -0.5, 0.5)     # 俯仰角度指令  
        yaw_cmd = np.clip(attitude_control[2], -1.0, 1.0)       # 偏航角速度指令
        
        return np.array([thrust, roll_cmd, pitch_cmd, yaw_cmd])
    
    def safety_check(self, wind_estimate: WindEstimate, 
                    drone_state: DroneState) -> Tuple[bool, str]:
        """
        安全检查函数
        
        Args:
            wind_estimate: 风况估计
            drone_state: 无人机状态
            
        Returns:
            Tuple[bool, str]: (是否安全, 警告信息)
        """
        warnings = []
        
        # 检查风速是否超过安全限制
        if wind_estimate.magnitude > self.max_wind_speed:
            warnings.append(f"风速过大: {wind_estimate.magnitude:.1f} m/s > {self.max_wind_speed} m/s")
        
        # 检查姿态角是否过大
        max_angle = math.radians(45)  # 45度限制
        for i, angle in enumerate(drone_state.attitude):
            if abs(angle) > max_angle:
                axis_name = ['roll', 'pitch', 'yaw'][i]
                warnings.append(f"{axis_name}角度过大: {math.degrees(angle):.1f}°")
        
        # 检查高度是否安全
        if drone_state.position[2] < 2.0:  # 最低2米
            warnings.append(f"高度过低: {drone_state.position[2]:.1f}m")
        
        is_safe = len(warnings) == 0
        warning_msg = "; ".join(warnings) if warnings else "系统状态正常"
        
        return is_safe, warning_msg
    
    def update_state_history(self, drone_state: DroneState, wind_estimate: WindEstimate):
        """更新状态历史记录"""
        self.state_history.append(drone_state)
        self.wind_history.append(wind_estimate)
        
        # 限制历史记录长度
        if len(self.state_history) > self.max_history_length:
            self.state_history.pop(0)
        if len(self.wind_history) > self.max_history_length:
            self.wind_history.pop(0)
    
    def get_control_status(self) -> Dict:
        """获取控制器状态信息"""
        if not self.wind_history:
            return {"status": "初始化中", "wind_condition": "未知"}
        
        latest_wind = self.wind_history[-1]
        return {
            "status": "运行中",
            "wind_condition": latest_wind.condition.value,
            "wind_speed": f"{latest_wind.magnitude:.1f} m/s",
            "confidence": f"{latest_wind.confidence:.2f}",
            "history_length": len(self.state_history)
        }


# 使用示例和测试代码
if __name__ == "__main__":
    # 创建控制器实例
    controller = WindStabilityController(max_wind_speed=20.0)
    
    # 模拟无人机状态
    drone_state = DroneState(
        position=(0.0, 0.0, 10.0),
        velocity=(1.0, 0.5, 0.0),
        attitude=(0.1, -0.05, 0.0),
        angular_velocity=(0.0, 0.0, 0.0),
        timestamp=0.0
    )
    
    # 目标状态
    target_position = (5.0, 5.0, 10.0)
    target_attitude = (0.0, 0.0, 0.0)
    
    # 模拟控制输入
    control_input = np.array([0.0, 0.0, 0.0, 0.0])
    
    # 估计风况
    wind_estimate = controller.estimate_wind_conditions(drone_state, control_input)
    
    # 计算控制输出
    control_output = controller.wind_compensation_control(
        drone_state, target_position, target_attitude, wind_estimate
    )
    
    # 安全检查
    is_safe, warning = controller.safety_check(wind_estimate, drone_state)
    
    # 更新历史记录
    controller.update_state_history(drone_state, wind_estimate)
    
    print("无人机风速稳定性控制器测试")
    print(f"风况估计: {wind_estimate.condition.value}, 风速: {wind_estimate.magnitude:.1f} m/s")
    print(f"控制输出: 推力={control_output[0]:.3f}, 横滚={control_output[1]:.3f}, 俯仰={control_output[2]:.3f}, 偏航={control_output[3]:.3f}")
    print(f"安全状态: {'安全' if is_safe else '警告'} - {warning}")
    print(f"控制器状态: {controller.get_control_status()}")