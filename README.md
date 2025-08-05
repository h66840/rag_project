# 酒店收益分析项目 (Hotel Revenue Analysis Project)

## 项目简介

本项目是一个基于RAG（Retrieval-Augmented Generation）技术的酒店收益分析系统，旨在通过数据分析和机器学习技术帮助酒店优化收益管理策略。

## 项目结构

```
rag_project/
├── src/                    # 源代码目录
├── tests/                  # 测试文件
├── project/               # 项目配置文件
├── supabase/              # Supabase配置
├── requirements.txt       # Python依赖包
└── README.md             # 项目说明文档
```

## 数据库访问

### 数据库用户命名规范

为了确保数据库访问的安全性和可管理性，我们制定了以下数据库用户命名规范：

#### 命名格式
```
{用户类型}_{项目标识}_{具体描述}
```

#### 用户类型分类
- `internal_` - 内部开发人员
- `external_` - 外部开发人员/合作伙伴
- `readonly_` - 只读访问用户
- `admin_` - 管理员用户
- `service_` - 服务账户

#### 项目标识
- `hotel_revenue` - 酒店收益分析项目
- `rag` - RAG相关功能
- `analytics` - 数据分析模块

#### 示例用户名
- `external_dev_hotel_revenue` - 外部开发人员（酒店收益项目）
- `internal_dev_rag` - 内部开发人员（RAG功能）
- `readonly_analytics` - 只读分析用户
- `service_hotel_revenue` - 酒店收益服务账户

#### 权限分配原则
1. **最小权限原则** - 用户只获得完成工作所需的最小权限
2. **外部用户限制** - 外部开发人员默认只有SELECT权限
3. **定期审查** - 定期审查和更新用户权限
4. **密码策略** - 使用强密码，定期更换

### 当前数据库用户

| 用户名 | 类型 | 权限 | 创建日期 | 用途 |
|--------|------|------|----------|------|
| external_dev_hotel_revenue | 外部开发 | SELECT | 2024-01-XX | 酒店收益分析项目外部开发人员 |

## 开发环境设置

### 数据库连接
```bash
# 开发环境数据库连接字符串示例
postgresql://username:password@localhost:5432/myapp
```

### 安装依赖
```bash
pip install -r requirements.txt
```

## 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 项目维护者：h66840
- 邮箱：[项目邮箱]
- Issue：在本仓库创建 Issue

---

*最后更新：2024年1月*