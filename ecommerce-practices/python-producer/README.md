# 电商场景 Kafka Python 生产者

这是一个简单的 Python 示例，演示如何在电商场景下向 Kafka 发送订单事件。

## 功能

- 模拟发送订单创建事件
- 支持批量发送
- 自动序列化为 JSON 格式
- 使用订单ID作为 Key，确保同一订单的消息有序

## 环境要求

- Python 3.7+
- Kafka 集群已启动（通过 docker-compose）

## 安装依赖

```bash
cd python-producer
pip install -r requirements.txt
```

或者使用虚拟环境：

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Linux/WSL:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

## 使用方法

### 1. 确保 Kafka 集群运行

```bash
# 在 ecommerce-practices 目录下
docker compose ps
```

### 2. 创建主题（如果还没有）

```bash
# 进入 Kafka 容器
docker exec -it kafka-1 bash

# 创建主题
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic order-events \
  --partitions 3 \
  --replication-factor 3

# 查看主题
kafka-topics.sh --bootstrap-server localhost:9092 --list
```

### 3. 运行生产者

```bash
python producer.py
```

## 输出示例

```
============================================================
电商场景 Kafka 生产者示例
============================================================
Kafka 服务器: localhost:19092, localhost:19093, localhost:19094
主题: order-events
============================================================

开始发送 10 条订单事件...
✓ [1/10] 订单事件已发送: ORD202401150001 -> Topic: order-events, Partition: 1, Offset: 0
✓ [2/10] 订单事件已发送: ORD202401150002 -> Topic: order-events, Partition: 2, Offset: 0
...
所有事件发送完成！

生产者已关闭
```

## 验证消息

### 方式一：使用 Kafka UI

访问 http://localhost:8080，查看 `order-events` 主题的消息。

### 方式二：使用命令行消费者

```bash
# 进入 Kafka 容器
docker exec -it kafka-1 bash

# 消费消息
kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-events \
  --from-beginning \
  --property print.key=true \
  --property print.timestamp=true
```

## 消息格式

发送的消息格式如下：

```json
{
  "orderId": "ORD202401150001",
  "userId": "U1234",
  "amount": 299.00,
  "productId": "PROD5678",
  "eventType": "ORDER_CREATED",
  "timestamp": "2024-01-15T14:30:25.123456",
  "paymentMethod": "alipay"
}
```

## 配置说明

### 修改 Kafka 服务器地址

如果 Kafka 不在本地，修改 `producer.py` 中的 `bootstrap_servers`：

```python
bootstrap_servers = [
    'your-kafka-host:19092',
    'your-kafka-host:19093',
    'your-kafka-host:19094'
]
```

### 修改发送数量

在 `main()` 函数中修改：

```python
producer.send_batch_events(count=20)  # 发送 20 条
```

### 修改主题名称

在 `OrderEventProducer.__init__()` 中修改：

```python
self.topic = 'your-topic-name'
```

## 常见问题

### 1. 连接失败

**错误**: `kafka.errors.KafkaTimeoutError`

**解决**:
- 确认 Kafka 集群正在运行：`docker compose ps`
- 检查端口是否正确（19092, 19093, 19094）
- 如果在 Windows 中运行，可能需要使用 WSL 的 IP 地址

### 2. 主题不存在

**错误**: `kafka.errors.UnknownTopicOrPartitionError`

**解决**: 先创建主题（见上面的"创建主题"步骤）

### 3. 编码问题

如果遇到中文编码问题，确保 Python 文件使用 UTF-8 编码。

## 下一步

- 添加更多事件类型（支付、发货、取消等）
- 实现消费者示例
- 添加错误处理和重试机制
- 使用 Avro 或 Protobuf 格式

