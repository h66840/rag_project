# 合作画廊艺术品目录API集成文档

## 概述
本文档描述了与合作画廊艺术品目录系统的API集成方案，包括数据获取、认证机制和集成流程。

## API基本信息
- **基础URL**: `https://api.artgallery-partner.com/v1`
- **API版本**: v1.2.3
- **协议**: HTTPS
- **数据格式**: JSON
- **认证方式**: OAuth 2.0 + API Key

## 认证配置
### OAuth 2.0 配置
```json
{
  "client_id": "gallery_client_12345",
  "client_secret": "[需要配置]",
  "authorization_url": "https://api.artgallery-partner.com/oauth/authorize",
  "token_url": "https://api.artgallery-partner.com/oauth/token",
  "scope": "artworks:read collections:read"
}
```

### API Key配置
```json
{
  "api_key_header": "X-Gallery-API-Key",
  "api_key": "[需要配置]"
}
```

## 核心API端点

### 1. 获取艺术品列表
- **端点**: `GET /artworks`
- **参数**:
  - `page`: 页码 (默认: 1)
  - `limit`: 每页数量 (默认: 20, 最大: 100)
  - `category`: 艺术品类别 (可选)
  - `artist`: 艺术家名称 (可选)
  - `available`: 是否可售 (true/false)

### 2. 获取艺术品详情
- **端点**: `GET /artworks/{artwork_id}`
- **参数**:
  - `artwork_id`: 艺术品唯一标识符

### 3. 获取艺术家信息
- **端点**: `GET /artists/{artist_id}`
- **参数**:
  - `artist_id`: 艺术家唯一标识符

### 4. 获取收藏系列
- **端点**: `GET /collections`
- **参数**:
  - `page`: 页码
  - `limit`: 每页数量

## 数据结构

### 艺术品对象 (Artwork)
```json
{
  "id": "artwork_12345",
  "title": "星夜印象",
  "artist": {
    "id": "artist_789",
    "name": "张三",
    "biography": "著名现代艺术家...",
    "birth_year": 1975
  },
  "category": "油画",
  "medium": "布面油画",
  "dimensions": {
    "width": 80,
    "height": 60,
    "unit": "cm"
  },
  "creation_year": 2023,
  "price": {
    "amount": 15000,
    "currency": "CNY"
  },
  "availability": {
    "status": "available",
    "location": "北京展厅"
  },
  "images": [
    {
      "url": "https://images.artgallery-partner.com/artwork_12345_main.jpg",
      "type": "main",
      "width": 1200,
      "height": 900
    }
  ],
  "description": "这是一幅充满现代感的油画作品...",
  "tags": ["现代艺术", "抽象", "色彩丰富"],
  "created_at": "2023-10-15T10:30:00Z",
  "updated_at": "2023-11-20T14:45:00Z"
}
```

### 艺术家对象 (Artist)
```json
{
  "id": "artist_789",
  "name": "张三",
  "biography": "张三是一位享誉国际的现代艺术家...",
  "birth_year": 1975,
  "nationality": "中国",
  "education": ["中央美术学院", "巴黎美术学院"],
  "exhibitions": [
    {
      "title": "现代艺术展",
      "year": 2023,
      "location": "北京现代艺术馆"
    }
  ],
  "awards": ["2022年度最佳艺术家奖"],
  "artwork_count": 45,
  "profile_image": "https://images.artgallery-partner.com/artist_789_profile.jpg"
}
```

## 错误处理
### 标准错误响应格式
```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数无效",
    "details": "参数 'limit' 不能超过 100",
    "timestamp": "2023-11-20T15:30:00Z"
  }
}
```

### 常见错误码
- `UNAUTHORIZED`: 认证失败
- `FORBIDDEN`: 权限不足
- `NOT_FOUND`: 资源不存在
- `RATE_LIMIT_EXCEEDED`: 请求频率超限
- `INVALID_REQUEST`: 请求参数无效
- `SERVER_ERROR`: 服务器内部错误

## 速率限制
- **标准用户**: 1000 请求/小时
- **高级用户**: 5000 请求/小时
- **企业用户**: 10000 请求/小时

## Webhook支持
画廊系统支持以下事件的Webhook通知：
- `artwork.created`: 新艺术品添加
- `artwork.updated`: 艺术品信息更新
- `artwork.sold`: 艺术品售出
- `artist.updated`: 艺术家信息更新

### Webhook配置
```json
{
  "webhook_url": "https://your-system.com/webhooks/gallery",
  "events": ["artwork.created", "artwork.updated", "artwork.sold"],
  "secret": "[webhook密钥]"
}
```

## 集成注意事项
1. **数据同步频率**: 建议每小时同步一次艺术品数据
2. **图片缓存**: 建议本地缓存艺术品图片以提高加载速度
3. **错误重试**: 实现指数退避重试机制
4. **数据验证**: 对接收的数据进行完整性验证
5. **日志记录**: 记录所有API调用和错误信息

## 测试环境
- **测试URL**: `https://api-staging.artgallery-partner.com/v1`
- **测试凭证**: 联系画廊技术团队获取

## 技术支持
- **联系邮箱**: tech-support@artgallery-partner.com
- **技术文档**: https://docs.artgallery-partner.com
- **状态页面**: https://status.artgallery-partner.com

## 更新日志
- **v1.2.3** (2023-11-20): 添加Webhook支持
- **v1.2.2** (2023-10-15): 优化艺术品搜索功能
- **v1.2.1** (2023-09-01): 增加艺术家详情API
- **v1.2.0** (2023-08-01): 初始版本发布