"""
无人机风速稳定性控制器测试套件
Test Suite for Wind Stability Controller

测试高风速环境下的无人机飞行稳定性控制算法
"""

import unittest
import numpy as np
import math
from drone_flight_control.wind_stability_controller import (
    WindStabilityController, DroneState, WindEstimate, WindCondition
)

class TestWindStabilityController(unittest.TestCase):
    """风速稳定性控制器测试类"""
    
    def setUp(self):
        """测试初始化"""
        self.controller = WindStabilityController(max_wind_speed=20.0)
        self.sample_drone_state = DroneState(
            position=(0.0, 0.0, 10.0),
            velocity=(0.0, 0.0, 0.0),
            attitude=(0.0, 0.0, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
            timestamp=0.0
        )
    
    def test_controller_initialization(self):
        """测试控制器初始化"""
        self.assertEqual(self.controller.max_wind_speed, 20.0)
        self.assertIsNotNone(self.controller.base_pid_params)
        self.assertEqual(len(self.controller.state_history), 0)
        self.assertEqual(len(self.controller.wind_history), 0)
    
    def test_wind_estimation_calm_conditions(self):
        """测试无风条件下的风速估计"""
        control_input = np.array([0.0, 0.0, 0.0, 0.0])
        wind_estimate = self.controller.estimate_wind_conditions(
            self.sample_drone_state, control_input
        )
        
        self.assertEqual(wind_estimate.condition, WindCondition.CALM)
        self.assertEqual(wind_estimate.magnitude, 0.0)
        self.assertEqual(wind_estimate.confidence, 0.0)
    
    def test_wind_estimation_with_history(self):
        """测试有历史数据时的风速估计"""
        # 添加历史状态
        state1 = DroneState(
            position=(0.0, 0.0, 10.0),
            velocity=(0.0, 0.0, 0.0),
            attitude=(0.0, 0.0, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
            timestamp=0.0
        )
        
        state2 = DroneState(
            position=(1.0, 1.0, 10.0),
            velocity=(2.0, 1.0, 0.0),  # 有明显速度变化
            attitude=(0.1, 0.05, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
            timestamp=0.1
        )
        
        self.controller.state_history = [state1]
        control_input = np.array([0.0, 0.0, 0.0, 0.0])
        
        wind_estimate = self.controller.estimate_wind_conditions(state2, control_input)
        
        # 应该检测到风速
        self.assertGreater(wind_estimate.magnitude, 0.0)
        self.assertIsInstance(wind_estimate.condition, WindCondition)
    
    def test_adaptive_pid_gains(self):
        """测试自适应PID参数调整"""
        # 测试不同风况下的PID参数
        wind_conditions = [
            WindCondition.CALM,
            WindCondition.LIGHT,
            WindCondition.MODERATE,
            WindCondition.STRONG,
            WindCondition.SEVERE
        ]
        
        for condition in wind_conditions:
            wind_estimate = WindEstimate(
                velocity=(0.0, 0.0, 0.0),
                magnitude=0.0,
                direction=0.0,
                condition=condition,
                confidence=1.0
            )
            
            adaptive_params = self.controller.adaptive_pid_gains(wind_estimate)
            
            # 检查参数结构
            self.assertIn('position', adaptive_params)
            self.assertIn('attitude', adaptive_params)
            self.assertIn('velocity', adaptive_params)
            
            # 检查参数值为正数
            for controller_type in adaptive_params:
                for param_name, value in adaptive_params[controller_type].items():
                    self.assertGreater(value, 0.0)
            
            # 强风条件下参数应该更大
            if condition == WindCondition.SEVERE:
                base_kp = self.controller.base_pid_params['position']['kp']
                adaptive_kp = adaptive_params['position']['kp']
                self.assertGreater(adaptive_kp, base_kp)
    
    def test_wind_compensation_control(self):
        """测试风补偿控制输出"""
        target_position = (5.0, 5.0, 10.0)
        target_attitude = (0.0, 0.0, 0.0)
        
        wind_estimate = WindEstimate(
            velocity=(5.0, 2.0, 0.0),  # 模拟侧风
            magnitude=5.4,
            direction=math.atan2(2.0, 5.0),
            condition=WindCondition.LIGHT,
            confidence=0.8
        )
        
        control_output = self.controller.wind_compensation_control(
            self.sample_drone_state, target_position, target_attitude, wind_estimate
        )
        
        # 检查控制输出格式
        self.assertEqual(len(control_output), 4)
        
        # 检查推力范围
        thrust = control_output[0]
        self.assertGreaterEqual(thrust, 0.1)
        self.assertLessEqual(thrust, 1.0)
        
        # 检查姿态指令范围
        roll_cmd, pitch_cmd = control_output[1], control_output[2]
        self.assertGreaterEqual(roll_cmd, -0.5)
        self.assertLessEqual(roll_cmd, 0.5)
        self.assertGreaterEqual(pitch_cmd, -0.5)
        self.assertLessEqual(pitch_cmd, 0.5)
        
        # 检查偏航指令范围
        yaw_cmd = control_output[3]
        self.assertGreaterEqual(yaw_cmd, -1.0)
        self.assertLessEqual(yaw_cmd, 1.0)
    
    def test_safety_check_normal_conditions(self):
        """测试正常条件下的安全检查"""
        wind_estimate = WindEstimate(
            velocity=(3.0, 2.0, 0.0),
            magnitude=3.6,
            direction=0.0,
            condition=WindCondition.LIGHT,
            confidence=0.9
        )
        
        is_safe, warning = self.controller.safety_check(wind_estimate, self.sample_drone_state)
        
        self.assertTrue(is_safe)
        self.assertEqual(warning, "系统状态正常")
    
    def test_safety_check_high_wind(self):
        """测试高风速条件下的安全检查"""
        wind_estimate = WindEstimate(
            velocity=(25.0, 10.0, 0.0),
            magnitude=26.9,  # 超过最大风速限制
            direction=0.0,
            condition=WindCondition.SEVERE,
            confidence=0.9
        )
        
        is_safe, warning = self.controller.safety_check(wind_estimate, self.sample_drone_state)
        
        self.assertFalse(is_safe)
        self.assertIn("风速过大", warning)
    
    def test_safety_check_extreme_attitude(self):
        """测试极端姿态下的安全检查"""
        extreme_drone_state = DroneState(
            position=(0.0, 0.0, 10.0),
            velocity=(0.0, 0.0, 0.0),
            attitude=(math.radians(50), 0.0, 0.0),  # 50度横滚角，超过45度限制
            angular_velocity=(0.0, 0.0, 0.0),
            timestamp=0.0
        )
        
        wind_estimate = WindEstimate(
            velocity=(0.0, 0.0, 0.0),
            magnitude=0.0,
            direction=0.0,
            condition=WindCondition.CALM,
            confidence=1.0
        )
        
        is_safe, warning = self.controller.safety_check(wind_estimate, extreme_drone_state)
        
        self.assertFalse(is_safe)
        self.assertIn("roll角度过大", warning)
    
    def test_safety_check_low_altitude(self):
        """测试低高度下的安全检查"""
        low_altitude_state = DroneState(
            position=(0.0, 0.0, 1.5),  # 1.5米高度，低于2米安全限制
            velocity=(0.0, 0.0, 0.0),
            attitude=(0.0, 0.0, 0.0),
            angular_velocity=(0.0, 0.0, 0.0),
            timestamp=0.0
        )
        
        wind_estimate = WindEstimate(
            velocity=(0.0, 0.0, 0.0),
            magnitude=0.0,
            direction=0.0,
            condition=WindCondition.CALM,
            confidence=1.0
        )
        
        is_safe, warning = self.controller.safety_check(wind_estimate, low_altitude_state)
        
        self.assertFalse(is_safe)
        self.assertIn("高度过低", warning)
    
    def test_state_history_update(self):
        """测试状态历史记录更新"""
        wind_estimate = WindEstimate(
            velocity=(1.0, 1.0, 0.0),
            magnitude=1.4,
            direction=math.pi/4,
            condition=WindCondition.CALM,
            confidence=0.5
        )
        
        # 添加状态记录
        self.controller.update_state_history(self.sample_drone_state, wind_estimate)
        
        self.assertEqual(len(self.controller.state_history), 1)
        self.assertEqual(len(self.controller.wind_history), 1)
        self.assertEqual(self.controller.state_history[0], self.sample_drone_state)
        self.assertEqual(self.controller.wind_history[0], wind_estimate)
    
    def test_history_length_limit(self):
        """测试历史记录长度限制"""
        wind_estimate = WindEstimate(
            velocity=(0.0, 0.0, 0.0),
            magnitude=0.0,
            direction=0.0,
            condition=WindCondition.CALM,
            confidence=1.0
        )
        
        # 添加超过最大长度的记录
        for i in range(60):  # 超过max_history_length=50
            state = DroneState(
                position=(i, i, 10.0),
                velocity=(0.0, 0.0, 0.0),
                attitude=(0.0, 0.0, 0.0),
                angular_velocity=(0.0, 0.0, 0.0),
                timestamp=float(i)
            )
            self.controller.update_state_history(state, wind_estimate)
        
        # 检查历史记录长度不超过限制
        self.assertEqual(len(self.controller.state_history), 50)
        self.assertEqual(len(self.controller.wind_history), 50)
        
        # 检查最新记录是否正确
        self.assertEqual(self.controller.state_history[-1].position[0], 59.0)
    
    def test_control_status(self):
        """测试控制器状态获取"""
        # 初始状态
        status = self.controller.get_control_status()
        self.assertEqual(status["status"], "初始化中")
        self.assertEqual(status["wind_condition"], "未知")
        
        # 添加风况记录后
        wind_estimate = WindEstimate(
            velocity=(8.0, 6.0, 0.0),
            magnitude=10.0,
            direction=0.0,
            condition=WindCondition.MODERATE,
            confidence=0.8
        )
        
        self.controller.update_state_history(self.sample_drone_state, wind_estimate)
        
        status = self.controller.get_control_status()
        self.assertEqual(status["status"], "运行中")
        self.assertEqual(status["wind_condition"], "moderate")
        self.assertEqual(status["wind_speed"], "10.0 m/s")
        self.assertEqual(status["confidence"], "0.80")
        self.assertEqual(status["history_length"], 1)

class TestWindConditionClassification(unittest.TestCase):
    """风况分类测试"""
    
    def test_wind_condition_enum(self):
        """测试风况枚举值"""
        self.assertEqual(WindCondition.CALM.value, "calm")
        self.assertEqual(WindCondition.LIGHT.value, "light")
        self.assertEqual(WindCondition.MODERATE.value, "moderate")
        self.assertEqual(WindCondition.STRONG.value, "strong")
        self.assertEqual(WindCondition.SEVERE.value, "severe")

class TestDataStructures(unittest.TestCase):
    """数据结构测试"""
    
    def test_drone_state_creation(self):
        """测试无人机状态数据结构"""
        state = DroneState(
            position=(1.0, 2.0, 3.0),
            velocity=(0.5, 0.6, 0.7),
            attitude=(0.1, 0.2, 0.3),
            angular_velocity=(0.01, 0.02, 0.03),
            timestamp=123.456
        )
        
        self.assertEqual(state.position, (1.0, 2.0, 3.0))
        self.assertEqual(state.velocity, (0.5, 0.6, 0.7))
        self.assertEqual(state.attitude, (0.1, 0.2, 0.3))
        self.assertEqual(state.angular_velocity, (0.01, 0.02, 0.03))
        self.assertEqual(state.timestamp, 123.456)
    
    def test_wind_estimate_creation(self):
        """测试风速估计数据结构"""
        estimate = WindEstimate(
            velocity=(5.0, 3.0, 0.0),
            magnitude=5.83,
            direction=0.54,
            condition=WindCondition.LIGHT,
            confidence=0.75
        )
        
        self.assertEqual(estimate.velocity, (5.0, 3.0, 0.0))
        self.assertAlmostEqual(estimate.magnitude, 5.83, places=2)
        self.assertAlmostEqual(estimate.direction, 0.54, places=2)
        self.assertEqual(estimate.condition, WindCondition.LIGHT)
        self.assertEqual(estimate.confidence, 0.75)

if __name__ == '__main__':
    # 运行所有测试
    unittest.main(verbosity=2)