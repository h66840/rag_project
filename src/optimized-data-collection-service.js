// 优化后的数据采集服务 - data-collection-service.js
const WebSocket = require('ws');
const mqtt = require('mqtt');
const { EventEmitter } = require('events');

class OptimizedDataCollectionService extends EventEmitter {
    constructor(config) {
        super();
        this.config = config;
        this.mqttClient = null;
        this.wsServer = null;
        this.validationRules = this.initializeValidationRules();
        this.metrics = {
            totalReceived: 0,
            validData: 0,
            invalidData: 0,
            processingTime: []
        };
    }

    // 初始化验证规则
    initializeValidationRules() {
        return {
            gps: {
                latitude: { min: -90, max: 90, required: true },
                longitude: { min: -180, max: 180, required: true },
                altitude: { min: -1000, max: 50000, required: true }
            },
            battery: {
                voltage: { min: 0, max: 50, required: true },
                current: { min: -100, max: 100, required: true },
                percentage: { min: 0, max: 100, required: true }
            },
            sensors: {
                temperature: { min: -50, max: 85, required: false },
                humidity: { min: 0, max: 100, required: false },
                pressure: { min: 300, max: 1100, required: false }
            },
            timestamp: {
                required: true,
                maxAge: 30000 // 30秒内的数据才有效
            }
        };
    }

    // 启动服务
    async start() {
        try {
            await this.initializeMQTT();
            await this.initializeWebSocket();
            console.log('Optimized Data Collection Service started successfully');
        } catch (error) {
            console.error('Failed to start service:', error);
            throw error;
        }
    }

    // 初始化MQTT连接
    async initializeMQTT() {
        return new Promise((resolve, reject) => {
            this.mqttClient = mqtt.connect(this.config.mqtt.brokerUrl, {
                clientId: `drone-collector-${Date.now()}`,
                username: this.config.mqtt.username,
                password: this.config.mqtt.password
            });

            this.mqttClient.on('connect', () => {
                console.log('MQTT connected');
                this.mqttClient.subscribe('drone/+/telemetry', (err) => {
                    if (err) reject(err);
                    else resolve();
                });
            });

            this.mqttClient.on('message', (topic, message) => {
                this.handleIncomingData(topic, message);
            });

            this.mqttClient.on('error', reject);
        });
    }

    // 初始化WebSocket服务器
    async initializeWebSocket() {
        this.wsServer = new WebSocket.Server({ 
            port: this.config.websocket.port 
        });

        this.wsServer.on('connection', (ws) => {
            console.log('WebSocket client connected');
            
            ws.on('message', (message) => {
                this.handleIncomingData('websocket', message);
            });

            ws.on('close', () => {
                console.log('WebSocket client disconnected');
            });
        });
    }

    // 处理接收到的数据
    async handleIncomingData(source, rawData) {
        const startTime = Date.now();
        this.metrics.totalReceived++;

        try {
            // 解析数据
            const data = this.parseIncomingData(rawData);
            
            // 集成的基础验证
            const validationResult = this.performIntegratedValidation(data);
            
            if (validationResult.isValid) {
                // 数据有效，直接发送到处理服务
                await this.sendToProcessingService(data);
                this.metrics.validData++;
                
                // 发送实时数据到WebSocket客户端
                this.broadcastRealTimeData(data);
            } else {
                // 数据无效，记录错误并发送到错误处理
                this.handleInvalidData(data, validationResult.errors);
                this.metrics.invalidData++;
            }

        } catch (error) {
            console.error('Error processing incoming data:', error);
            this.handleProcessingError(error, rawData);
        } finally {
            // 记录处理时间
            const processingTime = Date.now() - startTime;
            this.metrics.processingTime.push(processingTime);
            
            // 保持最近1000次的处理时间记录
            if (this.metrics.processingTime.length > 1000) {
                this.metrics.processingTime.shift();
            }
        }
    }

    // 解析接收到的数据
    parseIncomingData(rawData) {
        try {
            if (Buffer.isBuffer(rawData)) {
                return JSON.parse(rawData.toString());
            }
            return typeof rawData === 'string' ? JSON.parse(rawData) : rawData;
        } catch (error) {
            throw new Error(`Invalid JSON format: ${error.message}`);
        }
    }

    // 集成的基础验证逻辑
    performIntegratedValidation(data) {
        const errors = [];
        
        // 1. 基础结构验证
        if (!data || typeof data !== 'object') {
            return { isValid: false, errors: ['Invalid data structure'] };
        }

        // 2. 时间戳验证
        if (!this.validateTimestamp(data.timestamp)) {
            errors.push('Invalid or missing timestamp');
        }

        // 3. GPS数据验证
        if (data.gps && !this.validateGPSData(data.gps)) {
            errors.push('Invalid GPS data');
        }

        // 4. 电池数据验证
        if (data.battery && !this.validateBatteryData(data.battery)) {
            errors.push('Invalid battery data');
        }

        // 5. 传感器数据验证
        if (data.sensors && !this.validateSensorData(data.sensors)) {
            errors.push('Invalid sensor data');
        }

        // 6. 数据完整性检查
        if (!this.validateDataIntegrity(data)) {
            errors.push('Data integrity check failed');
        }

        return {
            isValid: errors.length === 0,
            errors: errors,
            validatedAt: new Date().toISOString()
        };
    }

    // 时间戳验证
    validateTimestamp(timestamp) {
        if (!timestamp) return false;
        
        const now = Date.now();
        const dataTime = new Date(timestamp).getTime();
        
        // 检查时间戳是否在合理范围内（不能太旧或太新）
        return Math.abs(now - dataTime) <= this.validationRules.timestamp.maxAge;
    }

    // GPS数据验证
    validateGPSData(gps) {
        const rules = this.validationRules.gps;
        
        return this.validateNumericRange(gps.latitude, rules.latitude) &&
               this.validateNumericRange(gps.longitude, rules.longitude) &&
               this.validateNumericRange(gps.altitude, rules.altitude);
    }

    // 电池数据验证
    validateBatteryData(battery) {
        const rules = this.validationRules.battery;
        
        return this.validateNumericRange(battery.voltage, rules.voltage) &&
               this.validateNumericRange(battery.current, rules.current) &&
               this.validateNumericRange(battery.percentage, rules.percentage);
    }

    // 传感器数据验证
    validateSensorData(sensors) {
        const rules = this.validationRules.sensors;
        
        // 传感器数据是可选的，但如果存在则需要验证
        for (const [key, value] of Object.entries(sensors)) {
            if (rules[key] && !this.validateNumericRange(value, rules[key])) {
                return false;
            }
        }
        return true;
    }

    // 数值范围验证
    validateNumericRange(value, rule) {
        if (rule.required && (value === undefined || value === null)) {
            return false;
        }
        
        if (value !== undefined && value !== null) {
            return typeof value === 'number' && 
                   value >= rule.min && 
                   value <= rule.max;
        }
        
        return !rule.required;
    }

    // 数据完整性检查
    validateDataIntegrity(data) {
        // 检查必需字段
        const requiredFields = ['droneId', 'timestamp'];
        return requiredFields.every(field => data[field] !== undefined);
    }

    // 发送数据到处理服务
    async sendToProcessingService(data) {
        try {
            // 这里可以使用HTTP、gRPC或消息队列
            // 示例使用HTTP POST
            const response = await fetch(`${this.config.processingService.url}/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Service-Source': 'data-collection'
                },
                body: JSON.stringify({
                    ...data,
                    processedAt: new Date().toISOString(),
                    validationPassed: true
                })
            });

            if (!response.ok) {
                throw new Error(`Processing service error: ${response.status}`);
            }

            this.emit('dataSent', { droneId: data.droneId, timestamp: data.timestamp });
        } catch (error) {
            console.error('Failed to send data to processing service:', error);
            // 可以实现重试逻辑或发送到死信队列
            this.handleProcessingServiceError(data, error);
        }
    }

    // 广播实时数据到WebSocket客户端
    broadcastRealTimeData(data) {
        const realTimeData = {
            droneId: data.droneId,
            timestamp: data.timestamp,
            gps: data.gps,
            battery: data.battery?.percentage,
            status: 'active'
        };

        this.wsServer.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(JSON.stringify(realTimeData));
            }
        });
    }

    // 处理无效数据
    handleInvalidData(data, errors) {
        console.warn('Invalid data received:', {
            droneId: data?.droneId,
            errors: errors,
            timestamp: new Date().toISOString()
        });

        // 发送到错误处理服务或记录到日志
        this.emit('invalidData', { data, errors });
    }

    // 处理处理服务错误
    handleProcessingServiceError(data, error) {
        // 可以实现重试队列或死信队列
        console.error('Processing service error:', error);
        this.emit('processingError', { data, error });
    }

    // 获取服务指标
    getMetrics() {
        const avgProcessingTime = this.metrics.processingTime.length > 0 
            ? this.metrics.processingTime.reduce((a, b) => a + b, 0) / this.metrics.processingTime.length 
            : 0;

        return {
            totalReceived: this.metrics.totalReceived,
            validData: this.metrics.validData,
            invalidData: this.metrics.invalidData,
            validationRate: this.metrics.totalReceived > 0 
                ? (this.metrics.validData / this.metrics.totalReceived * 100).toFixed(2) + '%'
                : '0%',
            averageProcessingTime: Math.round(avgProcessingTime) + 'ms'
        };
    }

    // 停止服务
    async stop() {
        if (this.mqttClient) {
            this.mqttClient.end();
        }
        
        if (this.wsServer) {
            this.wsServer.close();
        }
        
        console.log('Optimized Data Collection Service stopped');
    }
}

module.exports = OptimizedDataCollectionService;

// 使用示例
if (require.main === module) {
    const config = {
        mqtt: {
            brokerUrl: 'mqtt://localhost:1883',
            username: 'drone_collector',
            password: 'secure_password'
        },
        websocket: {
            port: 8001
        },
        processingService: {
            url: 'http://localhost:8003'
        }
    };

    const service = new OptimizedDataCollectionService(config);
    
    service.on('dataSent', (info) => {
        console.log('Data sent successfully:', info);
    });
    
    service.on('invalidData', (info) => {
        console.log('Invalid data detected:', info.errors);
    });

    service.start().catch(console.error);
    
    // 优雅关闭
    process.on('SIGINT', async () => {
        console.log('Shutting down...');
        await service.stop();
        process.exit(0);
    });
}