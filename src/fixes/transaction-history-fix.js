// 修复交易历史显示错误
class TransactionHistoryFix {
    constructor() {
        this.apiEndpoint = '/api/transactions';
    }

    // 修复交易历史数据获取
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
            return this.formatTransactionData(data);
        } catch (error) {
            console.error('获取交易历史失败:', error);
            return [];
        }
    }

    // 格式化交易数据
    formatTransactionData(rawData) {
        return rawData.map(transaction => ({
            id: transaction.id,
            date: new Date(transaction.timestamp).toLocaleDateString(),
            amount: parseFloat(transaction.amount).toFixed(2),
            type: transaction.type,
            status: transaction.status,
            description: transaction.description || '无描述'
        }));
    }

    // 获取认证令牌
    getAuthToken() {
        return localStorage.getItem('authToken') || '';
    }
}

export default TransactionHistoryFix;