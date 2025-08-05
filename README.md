# RAG Project

## 项目概述

RAG (Retrieval-Augmented Generation) 项目是一个基于检索增强生成技术的智能问答系统。本项目结合了先进的自然语言处理技术和高效的数据检索机制，为用户提供准确、相关的信息检索和生成服务。

## 数据库架构

### 当前数据库版本
- **最新迁移版本**: `20250805093323`
- **最新迁移名称**: `create_writing_logs_table`
- **数据库项目ID**: `zxqzmvnauqjtclckddoi`

### 主要数据表结构

本项目使用Supabase作为后端数据库，包含以下核心表结构：

#### 核心业务表
- **reviews**: 用户评论和反馈系统
- **employees**: 员工信息管理
- **profiles**: 用户配置文件
- **artifacts**: 系统生成的文档和资源

#### 专业功能表
- **genes**: 基因数据存储
- **genomic_sequence_schema**: 基因序列架构
- **fluid_simulation_results**: 流体仿真结果
- **carbon_emissions**: 碳排放数据追踪
- **elderly_care_clients**: 老年护理客户信息

#### 系统监控表
- **api_call_logs**: API调用日志
- **library_usage**: 库使用统计
- **daily_active_users**: 日活跃用户统计
- **flight_records**: 飞行记录数据
- **printer_logs**: 打印机使用日志
- **writing_logs**: 写作活动日志

#### 客户服务表
- **client_case_notes_system**: 客户案例记录系统
- **user_review_aggregator_tables**: 用户评价聚合表

### 数据库特性
- ✅ 行级安全策略 (RLS) 已启用
- ✅ 性能优化索引已配置
- ✅ 实时数据同步支持
- ✅ 自动备份机制

## 技术栈

- **后端数据库**: Supabase PostgreSQL
- **数据处理**: Python
- **API框架**: RESTful API
- **实时通信**: WebSocket
- **安全认证**: JWT Token

## 项目结构

```
rag_project/
├── src/                    # 源代码目录
├── docs/                   # 项目文档
├── tests/                  # 测试文件
├── supabase/              # 数据库迁移和配置
├── data_processor.py      # 数据处理模块
├── requirements.txt       # 依赖包列表
└── README.md             # 项目说明文档
```

## 快速开始

### 环境要求
- Python 3.8+
- PostgreSQL 13+
- Supabase CLI

### 安装步骤

1. 克隆项目仓库
```bash
git clone https://github.com/h66840/rag_project.git
cd rag_project
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置数据库连接
```bash
# 设置环境变量
export SUPABASE_URL="your-supabase-url"
export SUPABASE_KEY="your-supabase-key"
```

4. 运行数据库迁移
```bash
supabase db push
```

## 数据库迁移历史

最近的重要迁移更新：

| 版本 | 日期 | 描述 |
|------|------|------|
| 20250805093323 | 2025-08-05 | 创建写作日志表 |
| 20250805093152 | 2025-08-05 | 创建客户案例记录系统 |
| 20250805093045 | 2025-08-05 | 创建打印机日志表 |
| 20250805091440 | 2025-08-05 | 创建用户评价聚合表 |
| 20250805083225 | 2025-08-05 | 创建基因序列架构 |

## 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目维护者: h66840
- 项目链接: [https://github.com/h66840/rag_project](https://github.com/h66840/rag_project)

---

*最后更新: 2025年1月 - 数据库版本 20250805093323*