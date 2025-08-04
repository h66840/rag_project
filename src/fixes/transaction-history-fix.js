// 修复交易历史显示错误 - 增强版本
class TransactionHistoryFix {
    constructor() {
        this.apiEndpoint = '/api/transactions';
        this.retryCount = 0;
        this.maxRetries = 3;
    }

    // 修复交易历史数据获取 - 增加重试机制
    async fetchTransactionHistory(userId) {
        try {
            const response = await fetch(`${this.apiEndpoint}/${userId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getAuthToken()}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.retryCount = 0; // 重置重试计数
            return this.formatTransactionData(data);
        } catch (error) {
            console.error('获取交易历史失败:', error);
            
            // 实现重试机制
            if (this.retryCount < this.maxRetries) {
                this.retryCount++;
                console.log(`重试第 ${this.retryCount} 次...`);
                await this.delay(1000 * this.retryCount); // 递增延迟
                return this.fetchTransactionHistory(userId);
            }
            
            return [];
        }
    }

    // 格式化交易数据 - 增强版本
    formatTransactionData(rawData) {
        if (!Array.isArray(rawData)) {
            console.warn('交易数据格式不正确，期望数组格式');
            return [];
        }

        return rawData.map(transaction => {
            // 数据验证和清理
            const cleanTransaction = {
                id: transaction.id || `temp_${Date.now()}`,
                date: this.formatDate(transaction.timestamp || transaction.date),
                amount: this.formatAmount(transaction.amount),
                type: this.validateTransactionType(transaction.type),
                status: this.validateStatus(transaction.status),
                description: this.sanitizeDescription(transaction.description),
                category: transaction.category || '其他',
                currency: transaction.currency || 'CNY'
            };

            return cleanTransaction;
        }).filter(transaction => transaction.id && transaction.amount); // 过滤无效数据
    }

    // 日期格式化
    formatDate(dateInput) {
        try {
            const date = new Date(dateInput);
            if (isNaN(date.getTime())) {
                return '日期无效';
            }
            return date.toLocaleDateString('zh-CN', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch (error) {
            return '日期无效';
        }
    }

    // 金额格式化
    formatAmount(amount) {
        try {
            const numAmount = parseFloat(amount);
            if (isNaN(numAmount)) {
                return '0.00';
            }
            return numAmount.toFixed(2);
        } catch (error) {
            return '0.00';
        }
    }

    // 验证交易类型
    validateTransactionType(type) {
        const validTypes = ['income', 'expense', 'transfer'];
        return validTypes.includes(type) ? type : 'unknown';
    }

    // 验证状态
    validateStatus(status) {
        const validStatuses = ['pending', 'completed', 'failed', 'cancelled'];
        return validStatuses.includes(status) ? status : 'unknown';
    }

    // 清理描述文本
    sanitizeDescription(description) {
        if (!description || typeof description !== 'string') {
            return '无描述';
        }
        
        // 移除HTML标签和特殊字符
        return description
            .replace(/<[^>]*>/g, '')
            .replace(/[<>\"']/g, '')
            .trim()
            .substring(0, 100) || '无描述';
    }

    // 延迟函数
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // 获取认证令牌 - 增强版本
    getAuthToken() {
        const token = localStorage.getItem('authToken') || 
                     sessionStorage.getItem('authToken') || 
                     this.getCookieValue('authToken');
        
        if (!token) {
            console.warn('未找到认证令牌，可能需要重新登录');
        }
        
        return token || '';
    }

    // 从Cookie获取值
    getCookieValue(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return null;
    }

    // 缓存管理
    setCacheData(key, data, expireMinutes = 5) {
        const cacheData = {
            data: data,
            timestamp: Date.now(),
            expire: expireMinutes * 60 * 1000
        };
        localStorage.setItem(`cache_${key}`, JSON.stringify(cacheData));
    }

    getCacheData(key) {
        try {
            const cacheStr = localStorage.getItem(`cache_${key}`);
            if (!cacheStr) return null;
            
            const cache = JSON.parse(cacheStr);
            if (Date.now() - cache.timestamp > cache.expire) {
                localStorage.removeItem(`cache_${key}`);
                return null;
            }
            
            return cache.data;
        } catch (error) {
            return null;
        }
    }
}

export default TransactionHistoryFix;