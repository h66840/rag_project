# Inventory Report Generator

## 概述

Inventory Report Generator 是一个自动化的库存报告生成工具，专为提高团队效率而设计。该工具支持多种数据源，可以生成美观的HTML报告，并支持邮件自动发送功能。

## 功能特性

- 📊 **多数据源支持**: CSV、JSON文件和数据库
- 📧 **邮件通知**: 自动发送报告到指定邮箱
- 🎨 **美观报告**: 生成专业的HTML格式报告
- ⚠️ **库存预警**: 自动识别低库存商品
- 📈 **数据分析**: 提供详细的库存统计和分析
- 🔧 **高度可配置**: 通过JSON配置文件灵活设置

## 安装依赖

在使用脚本之前，请确保安装以下Python包：

```bash
pip install pandas jinja2
```

## 快速开始

### 1. 配置文件设置

复制 `config.json` 文件并根据您的需求进行修改：

```json
{
  "data_sources": {
    "csv_files": ["data/inventory.csv"],
    "json_files": ["data/inventory.json"],
    "database": {
      "enabled": false,
      "connection_string": "sqlite:inventory.db",
      "query": "SELECT * FROM inventory"
    }
  },
  "output": {
    "format": "html",
    "filename_template": "inventory_report_{date}.{format}",
    "output_directory": "./reports"
  },
  "email": {
    "enabled": true,
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "your-email@company.com",
    "password": "your-app-password",
    "recipients": ["manager@company.com"]
  }
}
```

### 2. 数据格式要求

#### CSV/JSON 数据格式
您的库存数据应包含以下字段：

| 字段名 | 类型 | 必需 | 描述 |
|--------|------|------|------|
| item_id | string | 是 | 商品唯一标识 |
| name | string | 是 | 商品名称 |
| category | string | 否 | 商品类别 |
| quantity | number | 是 | 库存数量 |
| unit_price | number | 是 | 单价 |
| supplier | string | 否 | 供应商 |

#### CSV 示例
```csv
item_id,name,category,quantity,unit_price,supplier
ITM001,Widget A,Electronics,150,25.99,TechCorp
ITM002,Widget B,Electronics,8,45.50,TechCorp
ITM003,Gadget X,Tools,75,12.75,ToolMaster
```

#### JSON 示例
```json
[
  {
    "item_id": "ITM001",
    "name": "Widget A",
    "category": "Electronics",
    "quantity": 150,
    "unit_price": 25.99,
    "supplier": "TechCorp"
  }
]
```

### 3. 运行脚本

#### 基本用法
```bash
python src/inventory_report.py
```

#### 指定配置文件
```bash
python src/inventory_report.py --config my_config.json
```

#### 启用详细日志
```bash
python src/inventory_report.py --verbose
```

## 配置选项详解

### 数据源配置 (data_sources)

- **csv_files**: CSV文件路径列表
- **json_files**: JSON文件路径列表
- **database**: 数据库连接配置
  - `enabled`: 是否启用数据库
  - `connection_string`: 数据库连接字符串
  - `query`: SQL查询语句

### 输出配置 (output)

- **format**: 报告格式 (目前支持 "html")
- **filename_template**: 文件名模板，支持 {date} 和 {format} 占位符
- **output_directory**: 报告输出目录

### 邮件配置 (email)

- **enabled**: 是否启用邮件发送
- **smtp_server**: SMTP服务器地址
- **smtp_port**: SMTP端口
- **username**: 邮箱用户名
- **password**: 邮箱密码或应用专用密码
- **recipients**: 收件人列表
- **subject_template**: 邮件主题模板

### 报告设置 (report_settings)

- **include_low_stock_alerts**: 是否包含低库存预警
- **low_stock_threshold**: 低库存阈值
- **include_charts**: 是否包含图表 (未来功能)
- **currency_symbol**: 货币符号

## 报告内容

生成的报告包含以下内容：

1. **总览统计**
   - 总商品数量
   - 总库存价值
   - 商品类别数
   - 供应商数量

2. **低库存预警**
   - 库存量低于阈值的商品列表
   - 包含商品ID、名称、当前库存和类别

3. **高价值商品**
   - 按总价值排序的前5名商品

4. **类别分析**
   - 按类别统计的商品数量、库存量和总价值

5. **供应商分析**
   - 按供应商统计的相关数据

## 自动化设置

### 使用 Cron (Linux/Mac)

添加到 crontab 以实现每周自动运行：

```bash
# 每周一上午9点运行
0 9 * * 1 /usr/bin/python3 /path/to/src/inventory_report.py
```

### 使用 Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务
3. 设置触发器为"每周"
4. 设置操作为运行Python脚本

## 故障排除

### 常见问题

1. **找不到数据文件**
   - 检查配置文件中的文件路径是否正确
   - 确保文件存在且有读取权限

2. **邮件发送失败**
   - 检查SMTP设置是否正确
   - 确认邮箱密码或应用专用密码
   - 检查网络连接

3. **数据格式错误**
   - 确保CSV/JSON文件包含必需字段
   - 检查数据类型是否正确

### 日志文件

脚本会生成详细的日志文件 `inventory_report.log`，包含：
- 运行时间戳
- 数据加载状态
- 错误信息
- 报告生成状态

## 扩展功能

### 添加新的数据源

可以通过修改 `InventoryReportGenerator` 类来添加新的数据源支持：

```python
def load_custom_data(self, source_config):
    # 实现自定义数据源加载逻辑
    pass
```

### 自定义报告模板

修改 `generate_html_report` 方法中的HTML模板来自定义报告外观。

### 添加新的输出格式

可以添加PDF、Excel等输出格式支持。

## 版本历史

- **v1.0.0** (2024): 初始版本
  - 基本报告生成功能
  - 多数据源支持
  - 邮件通知功能

## 支持

如有问题或建议，请联系开发团队或在项目仓库中提交Issue。

## 许可证

本项目采用 MIT 许可证。