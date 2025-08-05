# 智能家居天气窗帘自动调节系统

## 概述

这是一个基于天气数据的智能窗帘自动调节系统，能够根据实时天气条件（如阳光强度、温度、降雨等）自动调整窗帘的开合程度，为您的智能家居提供更舒适和节能的环境控制。

## 功能特性

### 🌤️ 天气感知
- 集成OpenWeatherMap API获取实时天气数据
- 支持多种天气条件识别：晴天、阴天、雨天、暴风雨、雾天等
- 监控温度、湿度、UV指数、风速等关键指标

### 🏠 智能控制
- 支持多个窗帘设备同时控制
- 基于规则的自动化决策系统
- 可配置的窗帘位置：完全开启、大部分开启、半开、大部分关闭、完全关闭

### ⚙️ 灵活配置
- JSON配置文件支持
- 自定义天气规则和优先级
- 静音时段设置（避免夜间自动调节）
- 手动覆盖功能

### 📊 监控与日志
- 详细的操作日志记录
- 可选的通知功能（Webhook、邮件）
- 异步处理确保系统响应性能

## 安装要求

### Python依赖
```bash
pip install aiohttp requests
```

### 系统要求
- Python 3.7+
- 网络连接（用于天气API调用）
- 智能窗帘设备API接口

## 快速开始

### 1. 获取天气API密钥
1. 访问 [OpenWeatherMap](https://openweathermap.org/api)
2. 注册账户并获取免费API密钥
3. 将API密钥填入 `weather_config.json` 文件

### 2. 配置设备信息
编辑 `weather_config.json` 文件：

```json
{
  "weather_api": {
    "api_key": "你的OpenWeatherMap API密钥"
  },
  "location": {
    "city": "你的城市名称",
    "country": "国家代码"
  },
  "curtain_devices": [
    {
      "device_id": "curtain_living_room",
      "name": "客厅窗帘",
      "api_endpoint": "你的窗帘设备API地址",
      "room": "living_room",
      "enabled": true
    }
  ]
}
```

### 3. 运行系统
```python
import asyncio
from weather_module import WeatherCurtainAutomation

async def main():
    automation = WeatherCurtainAutomation(
        weather_api_key="你的API密钥",
        curtain_device_id="curtain_living_room",
        location="Beijing"
    )
    
    # 执行一次调节
    await automation.update_curtain_based_on_weather()
    
    # 或启动持续监控
    await automation.start_monitoring(interval_minutes=30)

if __name__ == "__main__":
    asyncio.run(main())
```

## 配置详解

### 天气规则配置
系统支持基于以下条件的自定义规则：

- **天气条件**: sunny, cloudy, rainy, snowy, stormy, foggy, windy
- **温度范围**: 最低和最高温度阈值
- **UV指数**: 紫外线强度阈值
- **目标位置**: 0-100的窗帘开合百分比
- **优先级**: 数字越小优先级越高

### 示例规则
```json
{
  "name": "强烈阳光防护",
  "condition": "sunny",
  "temperature_min": 25.0,
  "temperature_max": 40.0,
  "uv_threshold": 6.0,
  "target_position": 25,
  "priority": 1,
  "enabled": true
}
```

### 静音时段
避免在睡眠时间自动调节窗帘：
```json
{
  "quiet_hours": {
    "enabled": true,
    "start_time": "22:00",
    "end_time": "07:00"
  }
}
```

## API接口

### WeatherCurtainAutomation类

#### 主要方法
- `update_curtain_based_on_weather()`: 执行一次天气检查和窗帘调节
- `start_monitoring(interval_minutes)`: 开始持续监控模式
- `add_rule(rule)`: 添加自定义控制规则
- `remove_rule(condition, priority)`: 移除指定规则

#### 使用示例
```python
# 创建自定义规则
from weather_module import CurtainRule, WeatherCondition, CurtainPosition

custom_rule = CurtainRule(
    condition=WeatherCondition.WINDY,
    temperature_range=(10.0, 30.0),
    uv_threshold=0.0,
    target_position=CurtainPosition.MOSTLY_CLOSED,
    priority=2
)

automation.add_rule(custom_rule)
```

## 设备集成

### 窗帘设备API要求
系统通过HTTP POST请求控制窗帘设备，期望的API格式：

```json
POST /api/curtain
{
  "device_id": "curtain_001",
  "position": 75,
  "timestamp": "2025-01-08T10:30:00"
}
```

### 支持的智能家居平台
- Home Assistant
- OpenHAB
- 自定义REST API设备
- MQTT设备（需要网关转换）

## 故障排除

### 常见问题

1. **API密钥错误**
   - 检查OpenWeatherMap API密钥是否正确
   - 确认API密钥有效期和调用限制

2. **窗帘设备无响应**
   - 验证设备API端点地址
   - 检查网络连接和设备状态
   - 查看日志文件获取详细错误信息

3. **天气数据获取失败**
   - 检查网络连接
   - 验证城市名称拼写
   - 确认API服务状态

### 日志查看
```bash
tail -f logs/weather_curtain.log
```

## 安全注意事项

1. **API密钥保护**: 不要将API密钥提交到版本控制系统
2. **网络安全**: 确保设备API使用HTTPS连接
3. **访问控制**: 限制系统的网络访问权限
4. **备份配置**: 定期备份配置文件

## 扩展功能

### 计划中的功能
- [ ] 支持更多天气API提供商
- [ ] 机器学习优化调节策略
- [ ] 移动应用控制界面
- [ ] 与其他智能家居设备联动
- [ ] 能耗统计和分析

### 自定义开发
系统采用模块化设计，支持以下扩展：

1. **新的天气数据源**: 继承 `WeatherAPIClient` 类
2. **设备控制器**: 继承 `CurtainController` 类
3. **决策规则**: 扩展 `CurtainRule` 数据结构

## 贡献指南

欢迎提交Issue和Pull Request来改进这个项目！

### 开发环境设置
```bash
git clone https://github.com/h66840/rag_project.git
cd rag_project
pip install -r requirements.txt
```

### 代码规范
- 遵循PEP 8编码规范
- 添加适当的类型注解
- 编写单元测试
- 更新文档

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: [项目Issues页面](https://github.com/h66840/rag_project/issues)
- 邮箱: [项目维护者邮箱]

---

**享受您的智能家居生活！** 🏡✨